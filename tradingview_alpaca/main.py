"""FastAPI application entry point for webhook and health endpoints."""

import asyncio

from fastapi import FastAPI, Header, HTTPException

import order_manager
import risk_filter
from config import settings
from logger import logger
from models import OrderResponse, SignalPayload

app = FastAPI(title="TradingView Alpaca Receiver")


@app.post("/webhook", response_model=OrderResponse)
async def webhook(
    payload: SignalPayload,
    x_webhook_secret: str | None = Header(default=None),
) -> OrderResponse:
    if x_webhook_secret != settings.WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Invalid or missing X-Webhook-Secret")

    logger.info(
        "webhook_received",
        extra={
            "payload": {
                "symbol": payload.symbol,
                "side": payload.side,
                "qty": payload.qty,
                "strategy": payload.strategy,
            }
        },
    )

    try:
        passed, reason = await asyncio.wait_for(
            asyncio.to_thread(risk_filter.check_all, payload),
            timeout=settings.RISK_CHECK_TIMEOUT_SECONDS,
        )
    except TimeoutError:
        logger.error(
            "risk_check_timeout",
            extra={"payload": {"symbol": payload.symbol, "side": payload.side}},
        )
        return OrderResponse(
            status="error",
            symbol=payload.symbol,
            side=payload.side,
            qty=payload.qty,
            reason="risk check timeout",
        )

    if not passed:
        logger.info(
            "order_skipped",
            extra={"payload": {"symbol": payload.symbol, "side": payload.side, "reason": reason}},
        )
        return OrderResponse(
            status="skipped",
            symbol=payload.symbol,
            side=payload.side,
            qty=payload.qty,
            reason=reason,
        )

    order_request = order_manager.build_market_order(payload.symbol, payload.side, payload.qty)

    try:
        order = await asyncio.wait_for(
            asyncio.to_thread(order_manager.submit_order, order_request),
            timeout=settings.ORDER_SUBMIT_TIMEOUT_SECONDS,
        )
    except TimeoutError:
        logger.error(
            "order_submit_timeout",
            extra={"payload": {"symbol": payload.symbol, "side": payload.side}},
        )
        return OrderResponse(
            status="error",
            symbol=payload.symbol,
            side=payload.side,
            qty=payload.qty,
            reason="order submit timeout",
        )
    except Exception as exc:
        logger.error("order_error", extra={"payload": {"symbol": payload.symbol, "error": str(exc)}}, exc_info=True)
        return OrderResponse(
            status="error",
            symbol=payload.symbol,
            side=payload.side,
            qty=payload.qty,
            reason=str(exc),
        )

    risk_filter.increment_daily_counter()

    return OrderResponse(
        status="submitted",
        order_id=str(order.id),
        symbol=order.symbol,
        side=order.side.value if hasattr(order.side, "value") else str(order.side),
        qty=int(order.qty) if order.qty else payload.qty,
    )


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "paper": settings.PAPER_TRADING}
