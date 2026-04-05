"""Constructs and submits Alpaca order requests."""

from alpaca.trading.models import Order
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

import alpaca_client
from logger import logger


def build_market_order(symbol: str, side: str, qty: int) -> MarketOrderRequest:
    return MarketOrderRequest(
        symbol=symbol,
        qty=qty,
        side=OrderSide.BUY if side == "buy" else OrderSide.SELL,
        time_in_force=TimeInForce.DAY,
    )


def submit_order(order_request: MarketOrderRequest) -> Order:
    client = alpaca_client.get_client()
    order: Order = client.submit_order(order_request)
    logger.info(
        "order_submitted",
        extra={
            "payload": {
                "order_id": str(order.id),
                "symbol": order.symbol,
                "side": str(order.side),
                "qty": order.qty,
                "status": str(order.status),
            }
        },
    )
    return order
