from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import threading
import uvicorn
import datetime
import argparse
import os
import pickle
import sys
from collections import defaultdict
from datetime import datetime
from threading import Thread
import numpy as np
from openai import OpenAI
import gym
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import math
import time
import re
import ast
import torch
import redis
from edgeric_messenger import EdgericMessenger

weight_array = []
UE_matrix_dict = {}
client = OpenAI(
    # This is the default and can be omitted
    )
class SendWeight:
    def __init__(self):
        self.messenger = EdgericMessenger(socket_type="weights")

    def periodic_send_weight(self):
        global UE_matrix_dict, weight_array
        while True:
            tti_count, ue_dict = self.messenger.get_metrics(True)                # get metrics
            # if tti_count is not None:
            UE_matrix_dict=ue_dict
            weight_array = self.generate_weight_array(ue_dict)                   # compute policy
            self.messenger.send_scheduling_weight(tti_count, weight_array, True) # send policy
    
    def generate_weight_array(self, ue_dict):
        global UE_matrix_dict, weight_array
        #weight_array = [
        #31282, 0.7,  # RNTI 1001 with weight 0.5
        #60481, 0.3,  # RNTI 1002 with weight 0.3  # RNTI 1003 with weight 0.2
        # ]   
        return weight_array


# if __name__ == "__main__":
#     send_weight = SendWeight()

#     # Create and start the periodic sending thread
#     send_weight_thread = threading.Thread(target=send_weight.periodic_send_weight)
#     send_weight_thread.start()

#     # Keep the main thread alive
#     try:
#         while True:
#             time.sleep(1)
#     except KeyboardInterrupt:
#         print("Stopping the weight sending script.")

weight_array = [
31282, 0.7,  # RNTI 1001 with weight 0.5
60481, 0.3,  # RNTI 1002 with weight 0.3  # RNTI 1003 with weight 0.2
]  

def handle_message(message, UE_matrix_dict):
    global weight_array
    # chatgpt logic to handle the message and UE_matrix_dict
    print("Generating response from OpenAI...")
    user_message = f"""You are an expert 5G network optimizer. A set of UEs are connected to a 5G base station. Each UE has the following parameters: {UE_matrix_dict}. Given these parameters, and the user's request: '{message}', provide concise and actionable recommendations to optimize the network performance. your output should be wieght array for prbs.example:```plaintext[RNTI1, weight1, RNTI2, weight2,...]``` where you should read rnti from ue paramitters and weight is a float between 0 and 1 representing the scheduling weight for each UE. Ensure the weights sum up to 1."""
    print("User message for OpenAI:", user_message)
    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a friendly and concise assistant."},
        {"role": "user", "content": user_message},
    ],
    temperature=0.7,
    )
    match = re.search(r'(?:plaintext)?\s*(\[.*?\])\s*', completion.choices[0].message.content, re.DOTALL)
    array_text = match.group(1)
    weight_array = ast.literal_eval(array_text)
    print("Generated weight array:", weight_array)
    return completion.choices[0].message.content


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
    # print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] User:", message)

    # # Basic example response logic
    # if not message:
    #     reply = "Say something so I can reply 🙂"
    # elif "hello" in message.lower():
    #     reply = "Hello! 👋 How are you today?"
    # elif "time" in message.lower():
    #     reply = f"The current time is {datetime.datetime.now().strftime('%H:%M:%S')}."
    # else:
    #     # default echo
    #     reply = f"You said: '{message}' (I'm just an echo bot for now!)"

    reply= handle_message(message, UE_matrix_dict)
    print("Reply:", reply)

    return JSONResponse({"reply": reply})

# Optional: serve other static files (images, JS modules, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    print("🚀 Starting chat server on http://127.0.0.1:7000")
    
    send_weight = SendWeight()

    # Create and start the periodic sending thread
    send_weight_thread = threading.Thread(target=send_weight.periodic_send_weight)
    send_weight_thread.start()
    uvicorn.run(app, host="0.0.0.0", port=7000)
