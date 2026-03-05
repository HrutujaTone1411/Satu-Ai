from fastapi import FastAPI, UploadFile, File # NEW: Added UploadFile and File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import subprocess
import webbrowser
from dotenv import load_dotenv
from groq import Groq
from datetime import datetime

print("\n--- STARTING SATISH AI (WHISPER EDITION) ---")
load_dotenv() 
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("🚨 FATAL ERROR: Cannot find GROQ_API_KEY in .env")
else:
    print("✅ SUCCESS: Groq API Key found!")
print("----------------------------------------\n")

client = Groq(api_key=api_key)

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
    history: list = []

@app.get("/")
def read_root():
    return {"message": "Satish Backend is awake!"}

@app.get("/status")
def get_status():
    return {"status": "Online"}

# --- NEW: THE AI EARS (WHISPER) ---
@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        # 1. Read the audio file from the React frontend
        audio_bytes = await file.read()
        
        # 2. Send it to Groq's incredibly fast Whisper model
        transcription = client.audio.transcriptions.create(
            file=("audio.webm", audio_bytes), # We label it as a webm file
            model="whisper-large-v3",         # The best open-source audio model
            response_format="json",
        )
        
        # 3. Return the perfectly transcribed text
        return {"text": transcription.text.strip()}
    except Exception as e:
        return {"error": str(e)}

# --- EXISTING CHAT LOGIC ---
@app.post("/chat")
def chat_with_satu(request: ChatRequest):
    try:
        if not api_key:
            return {"reply": "System Error: Missing Groq API Key."}
            
        current_time = datetime.now().strftime("%I:%M %p")
        current_date = datetime.now().strftime("%A, %B %d, %Y")
        
        dynamic_instruction = f"""
        You are Satish, a highly advanced AI agent and a loyal best friend. 
        You are talking to an IT student. You are conversational, empathetic, and slightly humorous. 
        You can speak fluently in English, Marathi, and Hindi. 
        
        CRITICAL VOICE RULE:
        Because your answers are being read out loud via text-to-speech, you MUST keep your answers incredibly short and concise. Speak in 1 to 2 short sentences maximum. Never write long paragraphs unless the user explicitly asks for a detailed explanation or a story.
        
        REAL-TIME CONTEXT:
        - Current Time: {current_time}
        - Current Date: {current_date}
        - Current Location: Navi Mumbai, Maharashtra, India
        
        PC CONTROL INSTRUCTIONS:
        If the user asks you to open YouTube, append the exact text <CMD: web_youtube> to your reply.
        If the user asks you to open Google, append the exact text <CMD: web_google> to your reply.
        If the user asks you to open Notepad, append the exact text <CMD: app_notepad> to your reply.
        If the user asks you to open Calculator, append the exact text <CMD: app_calc> to your reply.
        If the user asks you to open the Satu result folder, append the exact text <CMD: open_satu_result> to your reply.
        """ 
            
        groq_messages = [{"role": "system", "content": dynamic_instruction}]
        
        for past_msg in request.history:
            if past_msg.get("role") in ["user", "assistant"]:
                groq_messages.append(past_msg)
                
        groq_messages.append({"role": "user", "content": request.message})
            
        chat_completion = client.chat.completions.create(
            messages=groq_messages, 
            model="llama-3.3-70b-versatile",
            temperature=0.7,
        )
        
        reply = chat_completion.choices[0].message.content

        if "<CMD: web_youtube>" in reply:
            webbrowser.open("https://www.youtube.com")
            reply = reply.replace("<CMD: web_youtube>", "")
        elif "<CMD: web_google>" in reply:
            webbrowser.open("https://www.google.com")
            reply = reply.replace("<CMD: web_google>", "")
        elif "<CMD: app_notepad>" in reply:
            subprocess.Popen(["notepad.exe"])
            reply = reply.replace("<CMD: app_notepad>", "")
        elif "<CMD: app_calc>" in reply:
            subprocess.Popen(["calc.exe"])
            reply = reply.replace("<CMD: app_calc>", "")
        elif "<CMD: open_satu_result>" in reply:
            os.startfile(r"C:\Satu Ai\satu result") 
            reply = reply.replace("<CMD: open_satu_result>", "")

        return {"reply": reply.strip()}
        
    except Exception as e:
        return {"reply": f"System Error: {str(e)}"}