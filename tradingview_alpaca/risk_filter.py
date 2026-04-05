"""Pre-trade risk checks run before any order is submitted."""

from datetime import datetime, timezone
import threading

import alpaca_client
from config import settings
from logger import logger
from models import SignalPayload

_daily_order_count: int = 0
_last_reset_date: str = ""
_counter_lock = threading.Lock()


def _reset_daily_counter_if_needed() -> None:
    global _daily_order_count, _last_reset_date
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if today != _last_reset_date:
        _daily_order_count = 0
        _last_reset_date = today


def increment_daily_counter() -> None:
    global _daily_order_count
    with _counter_lock:
        _reset_daily_counter_if_needed()
        _daily_order_count += 1


def check_all(payload: SignalPayload) -> tuple[bool, str]:
    with _counter_lock:
        _reset_daily_counter_if_needed()
        current_count = _daily_order_count

    try:
        clock = alpaca_client.get_clock()
    except Exception as exc:
        return False, f"clock check failed: {exc}"

    if not clock.is_open:
        logger.info("risk_check_failed", extra={"payload": {"reason": "market_closed", "symbol": payload.symbol}})
        return False, "market is closed"

    try:
        account = alpaca_client.get_account()
    except Exception as exc:
        return False, f"account check failed: {exc}"

    if account.trading_blocked:
        logger.info("risk_check_failed", extra={"payload": {"reason": "trading_blocked", "symbol": payload.symbol}})
        return False, "account trading is blocked"

    if current_count >= settings.MAX_DAILY_ORDERS:
        logger.info("risk_check_failed", extra={"payload": {"reason": "daily_limit_reached", "count": current_count}})
        return False, f"daily order limit of {settings.MAX_DAILY_ORDERS} reached"

    if float(account.buying_power) <= 0:
        logger.info("risk_check_failed", extra={"payload": {"reason": "no_buying_power", "symbol": payload.symbol}})
        return False, "insufficient buying power"

    if payload.qty > settings.MAX_ORDER_QTY:
        logger.info("risk_check_failed", extra={"payload": {"reason": "qty_exceeds_max", "symbol": payload.symbol, "qty": payload.qty}})
        return False, f"qty {payload.qty} exceeds MAX_ORDER_QTY {settings.MAX_ORDER_QTY}"

    try:
        position = alpaca_client.get_open_position(payload.symbol)
    except Exception as exc:
        return False, f"position check failed: {exc}"

    if payload.side == "buy" and position is not None and float(position.qty) > 0:
        logger.info("risk_check_failed", extra={"payload": {"reason": "duplicate_long", "symbol": payload.symbol}})
        return False, "already long this symbol"

    if payload.side == "sell":
        if position is None or float(position.qty) == 0:
            logger.info("risk_check_failed", extra={"payload": {"reason": "no_position_to_sell", "symbol": payload.symbol}})
            return False, "no position to sell"
        if float(position.qty) < 0:
            logger.info("risk_check_failed", extra={"payload": {"reason": "already_short", "symbol": payload.symbol}})
            return False, "already short this symbol"

    return True, ""
