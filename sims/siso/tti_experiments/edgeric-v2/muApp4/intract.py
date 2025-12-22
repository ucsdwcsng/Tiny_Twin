from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import datetime

app = FastAPI()

# Serve the HTML file (assuming it's named 'chat.html' and in the same directory)
@app.get("/", response_class=HTMLResponse)
async def get_chat_ui():
    with open("chat.html", "r", encoding="utf-8") as f:
        return f.read()

# Simple chat API endpoint
@app.post("/api/chat")
async def chat_api(request: Request):
    data = await request.json()
    message = data.get("message", "").strip()
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] User:", message)

    # Basic example response logic
    if not message:
        reply = "Say something so I can reply 🙂"
    elif "hello" in message.lower():
        reply = "Hello! 👋 How are you today?"
    elif "time" in message.lower():
        reply = f"The current time is {datetime.datetime.now().strftime('%H:%M:%S')}."
    else:
        # default echo
        reply = f"You said: '{message}' (I'm just an echo bot for now!)"

    return JSONResponse({"reply": reply})

# Optional: serve other static files (images, JS modules, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    print("🚀 Starting chat server on http://127.0.0.1:7000")
    
    uvicorn.run(app, host="0.0.0.0", port=7000)
