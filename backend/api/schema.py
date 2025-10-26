"""
Pydantic Models for Receipt Data Interface
"""
from pydantic import BaseModel, Field
from typing import List

class ReceiptItem(BaseModel):
    """
    Represents a single line item extracted from a receipt.
    
    Each field includes a description which is passed to the AI model
    to help it understand what data to populate.
    """
    item_en: str = Field(
        description="The clear English translation of the item name (e.g., 'TV Shrimp Gratin')."
    )
    
    price: int = Field(
        description="The price of the item as an integer, with no currency symbols (e.g., 458)."
    )
    currency: str = Field(
        description="The currency used in the transaction in ISO 4217 currency codes (e.g., USD)."
    )



class Receipt(BaseModel):
    """
    A root-level model that represents the entire processed receipt.
    
    It contains a list of all extracted line items.
    """
    
    items: List[ReceiptItem] = Field(
        description="A complete list of all individual items found on the receipt."
    )
