from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from otica_scripts.message_tracker import MessageManager
from otica_scripts.store import StoreManager
from otica_scripts.whatsapp_sender import WhatsAppSender

app = FastAPI(title="Ótica Price Finder")
templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


class StoreInput(BaseModel):
    name: str
    phone: str
    address: str | None = None
    instagram: str | None = None


class MessageInput(BaseModel):
    message: str


class ResponseInput(BaseModel):
    phone: str
    response: str


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    store_manager = StoreManager()
    msg_manager = MessageManager()
    stores = store_manager.get_all_stores()
    messages = msg_manager.get_latest_message_per_store()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "stores": stores, "messages": messages}
    )


@app.post("/stores")
async def add_store(store: StoreInput) -> dict:
    manager = StoreManager()
    new_store = manager.add_store(store.name, store.phone, store.address, store.instagram)
    return {"success": True, "store": new_store.to_dict()}


@app.get("/stores")
async def list_stores() -> dict:
    manager = StoreManager()
    stores = manager.get_all_stores()
    return {"stores": [s.to_dict() for s in stores]}


@app.delete("/stores/{name}")
async def remove_store(name: str) -> dict:
    manager = StoreManager()
    success = manager.remove_store(name)
    return {"success": success}


@app.post("/send")
async def send_message(message_input: MessageInput) -> dict:
    manager = StoreManager()
    stores = manager.get_all_stores()
    sender = WhatsAppSender()
    try:
        sender.open_whatsapp()
        results = sender.send_to_all(stores, message_input.message)
        success_count = sum(1 for v in results.values() if v)
        return {
            "success": True,
            "sent": success_count,
            "total": len(stores),
            "results": results
        }
    finally:
        sender.close()


@app.post("/send-test")
async def send_test_message(message_input: MessageInput) -> dict:
    manager = StoreManager()
    stores = manager.get_all_stores()
    if not stores:
        return {"success": False, "store": "No stores"}

    sender = WhatsAppSender()
    try:
        sender.open_whatsapp()
        store = stores[0]
        success = sender.send_to_store(store, message_input.message)
        if success:
            msg_manager = MessageManager()
            msg_manager.add_message(store.name, store.phone, message_input.message)
        return {
            "success": success,
            "store": store.name
        }
    finally:
        sender.close()


@app.get("/messages")
async def get_messages() -> dict:
    msg_manager = MessageManager()
    messages = msg_manager.get_latest_message_per_store()
    return {"messages": {k: v.to_dict() for k, v in messages.items()}}


@app.post("/respond")
async def add_response(response_input: ResponseInput) -> dict:
    msg_manager = MessageManager()
    success = msg_manager.mark_as_responded(response_input.phone, response_input.response)
    return {"success": success}


@app.get("/stats")
async def get_stats() -> dict:
    msg_manager = MessageManager()
    messages = msg_manager.get_latest_message_per_store()
    sent = sum(1 for m in messages.values() if m.status == "sent")
    responded = sum(1 for m in messages.values() if m.status == "responded")
    return {"sent": sent, "responded": responded, "pending": sent - responded}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
