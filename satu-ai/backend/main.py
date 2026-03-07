from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import base64
import requests
import subprocess
import webbrowser
import re 
import urllib.parse 
from dotenv import load_dotenv
from groq import Groq
from datetime import datetime
import psutil
from ddgs import DDGS 

print("\n--- STARTING SATISH AI (PRO ARTIST EDITION) ---")
load_dotenv() 
api_key = os.getenv("GROQ_API_KEY")
hf_api_key = os.getenv("HF_API_KEY") # NEW: Loading your Hugging Face Key!

if not api_key: print("🚨 FATAL ERROR: Cannot find GROQ_API_KEY in .env")
else: print("✅ SUCCESS: Groq API Key found!")

if not hf_api_key: print("🚨 WARNING: Cannot find HF_API_KEY in .env. Art will fail.")
else: print("✅ SUCCESS: Hugging Face API Key found!")
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
def read_root(): return {"message": "Satish Backend is awake!"}

@app.get("/status")
def get_status(): return {"status": "Online"}

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        audio_bytes = await file.read()
        transcription = client.audio.transcriptions.create(
            file=("audio.webm", audio_bytes),
            model="whisper-large-v3",
            response_format="json",
        )
        return {"text": transcription.text.strip()}
    except Exception as e:
        return {"error": str(e)}

@app.post("/chat")
def chat_with_satu(request: ChatRequest):
    try:
        if not api_key: return {"reply": "System Error: Missing Groq API Key."}
            
        current_time = datetime.now().strftime("%I:%M %p")
        current_date = datetime.now().strftime("%A, %B %d, %Y")
        
        cpu_usage = psutil.cpu_percent(interval=0.1) 
        ram = psutil.virtual_memory()
        ram_usage = ram.percent 
        battery = psutil.sensors_battery()
        battery_status = f"{battery.percent}%" if battery else "Plugged In"

        dynamic_instruction = f"""
        You are SATISH, a highly intelligent personal AI assistant like Jarvis.
        Your purpose is to help the user manage their computer, automate tasks, and assist in daily life.
        Your name is Satish and you address the user as your friend.

        Personality:
        - Friendly
        - Intelligent
        - Loyal assistant
        - Calm and professional

        Capabilities & Behavior Rules:
        1. Always prioritize safety and ask confirmation before critical system actions.
        2. Explain actions clearly before executing them.
        3. Be proactive and suggest helpful automations.
        4. Maintain a friendly personality like a loyal companion.
        5. Always break tasks into steps and execute them efficiently.

        CRITICAL VOICE RULE: Keep your spoken answers incredibly short. Speak in 1 to 2 short sentences maximum unless asked for a detailed explanation.

        REAL-TIME CONTEXT:
        Time: {current_time} | Date: {current_date} | Location: Navi Mumbai
        CPU: {cpu_usage}% | RAM: {ram_usage}% | Power: {battery_status}
        
        WEB SEARCH INSTRUCTIONS:
        If asked for live information, news, or prices, reply ONLY with: <SEARCH: your query>
        
        IMAGE GENERATION INSTRUCTIONS (CRITICAL):
        If the user asks you to generate, create, or draw an image/photo, reply with EXACTLY this format: <IMAGE: your highly detailed prompt>
        Make the prompts as descriptive and artistic as possible to get the best results.
        
        PC CONTROL INSTRUCTIONS:
        Use these tags to control the PC: <CMD: web_youtube>, <CMD: web_google>, <CMD: app_notepad>, <CMD: app_calc>, <CMD: open_satu_result>.
        """
            
        groq_messages = [{"role": "system", "content": dynamic_instruction}]
        
        for past_msg in request.history:
            if past_msg.get("role") in ["user", "assistant"]: groq_messages.append(past_msg)
                
        groq_messages.append({"role": "user", "content": request.message})
            
        chat_completion = client.chat.completions.create(
            messages=groq_messages, 
            model="llama-3.3-70b-versatile",
            temperature=0.7,
        )
        reply = chat_completion.choices[0].message.content

        search_match = re.search(r"<SEARCH:\s*(.*?)>", reply)
        image_match = re.search(r"<IMAGE:\s*(.*?)>", reply) 
        
        if search_match:
            search_query = search_match.group(1)
            try:
                results = DDGS().text(search_query, max_results=5)
                search_context = "Error: No data." if not results else f"Live Web Results:\n" + "\n".join([f"- {res['body']}" for res in results])
                
                groq_messages.extend([
                    {"role": "assistant", "content": reply},
                    {"role": "user", "content": f"Raw internet data:\n\n{search_context}\n\nAct as a data analyst. Give me the final verified answer directly in a short sentence. Do NOT output the <SEARCH> tag again."}
                ])
                chat_completion_2 = client.chat.completions.create(messages=groq_messages, model="llama-3.3-70b-versatile", temperature=0.7)
                reply = chat_completion_2.choices[0].message.content
            except:
                reply = "My internet connection failed."
                
        # --- THE PRO IMAGE GENERATOR (Hugging Face API) ---
        elif image_match:
            image_prompt = image_match.group(1)
            print(f"🎨 Satish is painting via Hugging Face: {image_prompt}")
            
            if not hf_api_key:
                reply = reply.replace(image_match.group(0), "System Error: Missing Hugging Face API Key.")
            else:
                try:
                    # We are using Stable Diffusion XL Base 1.0!
                    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
                    headers = {"Authorization": f"Bearer {hf_api_key}"}
                    payload = {"inputs": image_prompt}
                    
                    print(f"⏳ Sending request to AI cluster...")
                    img_response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
                    
                    if img_response.status_code == 200:
                        img_base64 = base64.b64encode(img_response.content).decode('utf-8')
                        data_uri = f"data:image/jpeg;base64,{img_base64}"
                        reply = reply.replace(image_match.group(0), f"I have generated the artwork for you. IMAGE_URL:{data_uri}")
                        print("✅ Image successfully generated and sent to React!")
                    else:
                        print(f"🚨 HF API ERROR! Status Code: {img_response.status_code}")
                        print(f"🚨 MSG: {img_response.text[:250]}")
                        # Usually a 503 means the model is just waking up
                        reply = reply.replace(image_match.group(0), "My private art server is warming up. Can you please ask me to generate it again in 20 seconds?")
                except Exception as e:
                    print(f"🚨 IMAGE CRASH: {str(e)}") 
                    reply = reply.replace(image_match.group(0), "I encountered a network error while painting the image.")
                
        # --- PC COMMAND INTERCEPTORS ---
        if "<CMD: web_youtube>" in reply: webbrowser.open("https://www.youtube.com"); reply = reply.replace("<CMD: web_youtube>", "")
        if "<CMD: web_google>" in reply: webbrowser.open("https://www.google.com"); reply = reply.replace("<CMD: web_google>", "")
        if "<CMD: app_notepad>" in reply: subprocess.Popen(["notepad.exe"]); reply = reply.replace("<CMD: app_notepad>", "")
        if "<CMD: app_calc>" in reply: subprocess.Popen(["calc.exe"]); reply = reply.replace("<CMD: app_calc>", "")
        if "<CMD: open_satu_result>" in reply: os.startfile(r"C:\Satu Ai\satu result"); reply = reply.replace("<CMD: open_satu_result>", "")

        return {"reply": reply.strip()}
    except Exception as e:
        return {"reply": f"System Error: {str(e)}"}