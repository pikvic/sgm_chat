import os
from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from uuid import uuid4


from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole

def get_start_payload():
    return Chat(
        messages=[
            Messages(
                role=MessagesRole.SYSTEM,
                content="Ты ассистент геолога-исследователя. Тебе необходимо через наводящие вопросы привести геолога к выбору метода обработки его данных, решения его задачи. Цель твоего диалога с ним - выяснить, какие у него данные: текстовые, количественные, картографические, изображения. Начинать диалог всегда надо с приветствия и рассказа о себе. Потом уже геолог будет писать сообщения в ответ на твои наводящие вопросы."
            )
        ],
        temperature=0.7,
        max_tokens=100,
    )

class ChatMessage(BaseModel):
    role: str
    content: str

chats = {}

hello = "Здравствуйте! Я — виртуальный ассистент, который помогает геологам-исследователям в обработке данных и решении задач. Как я могу Вам помочь?"

token = os.environ.get("GIGACHAT_TOKEN", None)
print(token)
app = FastAPI()

templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    chat_id = request.cookies.get("chat_id", None)
    message = ChatMessage(role="bot", content=hello)
    response = templates.TemplateResponse("index.html", {"request": request, "messages": [message]})
    if not chat_id:
        chat_id = str(uuid4())
        response.set_cookie(key="chat_id", value=chat_id)
    chat = get_start_payload()
    chats[chat_id] = {"chat": chat, "messages": [message]}
    return response

@app.post("/chat", response_model=ChatMessage)
async def chat(request: Request, message: ChatMessage):
    print(chats)
    chat_id = request.cookies.get("chat_id", None)
    payload = chats[chat_id]["chat"]
    with GigaChat(credentials=token, verify_ssl_certs=False) as giga:
        payload.messages.append(Messages(role=MessagesRole.USER, content=message.content))
        response = giga.chat(payload)
        payload.messages.append(response.choices[0].message)
        msg = ChatMessage(role="bot", content=response.choices[0].message.content)
        chats[chat_id]["messages"].append(msg)
    return msg
