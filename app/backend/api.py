from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.common.custom_exception import CustomException
from app.common.logger import get_logger
from app.config.settings import ALLOWED_MODEL_NAMES
from app.core.ai_agent import get_response_for_ai_agent

logger = get_logger(__name__)

app = FastAPI(title="Multi AI Agent")


class RequestState(BaseModel):
    model_name: str
    system_prompt: str
    messages: List[str]
    allow_search: bool


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
def chat_endpoint(request: RequestState):
    logger.info(f"Request received for model {request.model_name}")

    if request.model_name not in ALLOWED_MODEL_NAMES:
        logger.warning("Invalid model name")
        raise HTTPException(status_code=400, detail="Invalid model name")

    try:
        response = get_response_for_ai_agent(
            request.model_name,
            request.messages,
            request.allow_search,
            request.system_prompt,
        )
        logger.info("Response sent")
        return {"response": response}

    except CustomException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(CustomException("Unexpected backend error", e)),
        )