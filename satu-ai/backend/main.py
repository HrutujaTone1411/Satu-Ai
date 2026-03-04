from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from groq import Groq

# --- WAKING UP GROQ ---
print("\n--- STARTING SATU AI (GROQ EDITION) ---")
load_dotenv() 
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("🚨 FATAL ERROR: Cannot find GROQ_API_KEY in .env")
else:
    print("✅ SUCCESS: Groq API Key found!")
print("----------------------------------------\n")

# Initialize Groq Client
client = Groq(api_key=api_key)

# Define Satu's Persona
system_instruction = """
You are Satu Ai, a highly advanced AI agent and a loyal best friend. 
You are talking to an IT student. You are conversational, empathetic, and slightly humorous. 
You can speak fluently in English, Marathi, and Hindi. 
If your friend is practicing English, be supportive and speak clearly.
Always be ready to help with coding, daily tasks, or just having a good chat.
Keep your responses concise and natural.
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
            
        # Sending the message to Groq (using Meta's ultra-fast Llama 3 model)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_instruction
                },
                {
                    "role": "user",
                    "content": request.message
                }
            ],
            model="llama-3.3-70b-versatile", # This is a massive, highly capable model
            temperature=0.7,
        )
        
        # Getting the reply
        reply = chat_completion.choices[0].message.content
        return {"reply": reply}
        
    except Exception as e:
        return {"reply": f"System Error: {str(e)}"}