"""
Pydantic models shared across agents.
"""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class UIAction(BaseModel):
    action_type: Literal["redirect", "set_filter", "popup", "trigger_api", "open_inline_procurement"] = Field(
        description="The type of UI action to perform."
    )
    params: dict = Field(
        default_factory=dict,
        description="The parameters for the UI action (e.g., view name for redirect, filter values for set_filter, endpoint and label for trigger_api)."
    )


class OrchestrationResponse(BaseModel):
    decision: Literal["num2text", "text2num", "email", "unknown"] = Field(
        description="The routing decision for the orchestrator."
    )
    ui_actions: List[UIAction] = Field(
        default_factory=list,
        description="A list of UI actions to trigger based on user intent."
    )
    chat_response: Optional[str] = Field(
        default=None,
        description="A direct conversational response for greetings or banter."
    )


class EmailExtraction(BaseModel):
    item_name: str = Field(description="The name or description of the requested product/item.")
    quantity: int = Field(description="The numeric quantity requested.")
    days_available: int = Field(description="The number of days within which the items are needed.")
    priority: str = Field(description="Priority: 'High' (within 7 days), 'Medium' (7-30 days), or 'Low' (after 30 days)")
    summary: str = Field(description="A brief 1-sentence summary of the request.")
