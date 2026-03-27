import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import get_agent

app = FastAPI(title="Chat Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    history: list = []

@app.get("/")
def home():
    return {"message": "Chat service running"}

@app.post("/chat")
async def chat(req: ChatRequest):
    agent = get_agent()
    result = agent.invoke({
        "input": req.message,
        "chat_history": req.history
    })
    return {"reply": result["output"]}