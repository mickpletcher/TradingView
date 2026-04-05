"""Pydantic v2 models for inbound TradingView webhook payloads and outbound responses."""

import re
from typing import Literal
from pydantic import BaseModel, Field, field_validator, model_validator

from config import settings


class SignalPayload(BaseModel):
    symbol: str
    side: Literal["buy", "sell"]
    qty: int = Field(gt=0)
    strategy: str
    price: float | None = None
    interval: str | None = None
    time: str | None = None

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, value: str) -> str:
        normalized = value.strip().upper()
        if not re.fullmatch(r"[A-Z][A-Z0-9.-]{0,14}", normalized):
            raise ValueError("symbol must contain only A-Z, 0-9, dot, or hyphen and start with a letter")
        return normalized

    @model_validator(mode="after")
    def check_qty_against_config(self) -> "SignalPayload":
        if self.qty > settings.MAX_ORDER_QTY:
            raise ValueError(f"qty {self.qty} exceeds MAX_ORDER_QTY {settings.MAX_ORDER_QTY}")
        return self


class OrderResponse(BaseModel):
    status: Literal["submitted", "skipped", "error"]
    order_id: str | None = None
    symbol: str
    side: str
    qty: int | None = None
    reason: str | None = None
