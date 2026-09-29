from fastapi import APIRouter
from pydantic import BaseModel

from app.ai.llm_client import generate_text

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str


@router.post("")
def chat(request: ChatRequest) -> dict:
    response = generate_text(
        prompt=request.message,
        system_instruction=(
            "You are a helpful personal finance assistant. "
            "Answer the user's questions clearly and concisely. "
            "Give practical financial guidance, but do not claim to "
            "have access to the user's financial data unless it is "
            "provided in the conversation."
        ),
    )

    return {"response": response}