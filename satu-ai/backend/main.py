from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import subprocess  # NEW: Lets Python open Windows applications
import webbrowser  # NEW: Lets Python open websites
from dotenv import load_dotenv
from groq import Groq

print("\n--- STARTING SATU AI (PC CONTROL EDITION) ---")
load_dotenv() 
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("🚨 FATAL ERROR: Cannot find GROQ_API_KEY in .env")
else:
    print("✅ SUCCESS: Groq API Key found!")
print("----------------------------------------\n")

client = Groq(api_key=api_key)

# NEW: We upgraded the system instructions to teach Satu how to use PC commands
system_instruction =system_instruction = """
You are Satish, a highly advanced AI agent and a loyal best friend. 
You are talking to an IT student. You are conversational, empathetic, and slightly humorous. 
You can speak fluently in English, Marathi, and Hindi. 

PC CONTROL INSTRUCTIONS:
If the user asks you to open YouTube, append the exact text <CMD: web_youtube> to your reply.
If the user asks you to open Google, append the exact text <CMD: web_google> to your reply.
If the user asks you to open Notepad, append the exact text <CMD: app_notepad> to your reply.
If the user asks you to open Calculator, append the exact text <CMD: app_calc> to your reply.

Example: If the user says "Open YouTube", you should reply: "Opening YouTube for you now! <CMD: web_youtube>"
"""

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def read_root():
    return {"message": "Satu Ai Backend is awake!"}

@app.get("/status")
def get_status():
    return {"status": "Online"}

@app.post("/chat")
def chat_with_satu(request: ChatRequest):
    try:
        if not api_key:
            return {"reply": "System Error: Missing Groq API Key."}
            
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": request.message}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
        )
        
        reply = chat_completion.choices[0].message.content

        # NEW: The Interceptor (Checking for hidden commands from the AI)
        if "<CMD: web_youtube>" in reply:
            webbrowser.open("https://www.youtube.com")
            reply = reply.replace("<CMD: web_youtube>", "") # Hide the tag from the user
            
        elif "<CMD: web_google>" in reply:
            webbrowser.open("https://www.google.com")
            reply = reply.replace("<CMD: web_google>", "")
            
        elif "<CMD: app_notepad>" in reply:
            subprocess.Popen(["notepad.exe"]) # Opens Windows Notepad
            reply = reply.replace("<CMD: app_notepad>", "")
            
        elif "<CMD: app_calc>" in reply:
            subprocess.Popen(["calc.exe"]) # Opens Windows Calculator
            reply = reply.replace("<CMD: app_calc>", "")

        return {"reply": reply.strip()}
        
    except Exception as e:
        return {"reply": f"System Error: {str(e)}"}