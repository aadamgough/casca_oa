from datetime import datetime
from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional

class Transaction(BaseModel):
    date: datetime
    description: str
    amount: Decimal
    transaction_type: str = Field(..., description="credit or debit")
    balance_after: Decimal
    category: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "date": "2024-03-20T10:00:00",
                "description": "Payment to Supplier XYZ",
                "amount": 1000.00,
                "transaction_type": "debit",
                "balance_after": 5000.00,
                "category": "supplier_payment"
            }
        }