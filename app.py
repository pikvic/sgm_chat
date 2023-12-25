from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from uuid import uuid4

class ChatMessage:
    message: str

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

#async def root(request: Request):
    #response = templates.TemplateResponse("index.html", {"request": Request})
    #chat_id = str(uuid4())
    #response.set_cookie(key="chat_id", value=chat_id)
 #   return {"hello": "fds"}

# @app.post("/chat")
# async def chat(message: ChatMessage):
#     return {"message": message}
    