from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import subprocess
import webbrowser
import re # NEW: Helps us spot the hidden <SEARCH> tags
from dotenv import load_dotenv
from groq import Groq
from datetime import datetime
import psutil
import requests
from ddgs import DDGS # NEW: The DuckDuckGo Internet Searcher!

print("\n--- STARTING SATISH AI (LIVE INTERNET EDITION) ---")
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
        if not api_key:
            return {"reply": "System Error: Missing Groq API Key."}
            
        current_time = datetime.now().strftime("%I:%M %p")
        current_date = datetime.now().strftime("%A, %B %d, %Y")
        
        # --- HARDWARE & WEATHER SENSORS ---
        cpu_usage = psutil.cpu_percent(interval=0.1) 
        ram = psutil.virtual_memory()
        ram_usage = ram.percent 
        battery = psutil.sensors_battery()
        battery_status = f"{battery.percent}%" if battery else "Plugged In"

        try:
            weather_url = "https://api.open-meteo.com/v1/forecast?latitude=19.033&longitude=73.030&current_weather=true"
            weather_data = requests.get(weather_url).json()
            temp = weather_data["current_weather"]["temperature"]
            weather_status = f"{temp}°C"
        except:
            weather_status = "Offline"

        # --- THE MASTER SYSTEM PROMPT ---
        dynamic_instruction = f"""
        You are Satish, a highly advanced AI agent and a loyal best friend. 
        You are talking to an IT student. You are conversational, empathetic, and slightly humorous. 
        You can speak fluently in English, Marathi, and Hindi. 
        
        CRITICAL VOICE RULE:
        Keep your answers incredibly short and concise. Speak in 1 to 2 short sentences maximum.
        
        REAL-TIME CONTEXT:
        Time: {current_time} | Date: {current_date} | Location: Navi Mumbai | Weather: {weather_status}
        CPU: {cpu_usage}% | RAM: {ram_usage}% | Power: {battery_status}
        
        WEB SEARCH INSTRUCTIONS (CRITICAL):
        If the user asks for live information, current prices (like gold or stocks), news, or facts you don't know, YOU MUST SEARCH THE WEB.
        Reply with EXACTLY this format and nothing else: <SEARCH: your query>
        Example: If asked for the gold rate, reply ONLY with: <SEARCH: today gold rate in India>    
       
         PC CONTROL INSTRUCTIONS:
        Use these tags to control the PC: <CMD: web_youtube>, <CMD: web_google>, <CMD: app_notepad>, <CMD: app_calc>, <CMD: open_satu_result>.
        """
            
        groq_messages = [{"role": "system", "content": dynamic_instruction}]
        
        for past_msg in request.history:
            if past_msg.get("role") in ["user", "assistant"]:
                groq_messages.append(past_msg)
                
        groq_messages.append({"role": "user", "content": request.message})
            
        # --- THE FIRST TAP (Ask Satish what he wants to do) ---
        chat_completion = client.chat.completions.create(
            messages=groq_messages, 
            model="llama-3.3-70b-versatile",
            temperature=0.7,
        )
        
        reply = chat_completion.choices[0].message.content

        # --- THE INTERCEPTOR (Check if Satish wants to search the web) ---
        search_match = re.search(r"<SEARCH:\s*(.*?)>", reply)
        
        if search_match:
            search_query = search_match.group(1)
            print(f"🔍 Satish is searching the web for: {search_query}")
            
            try:
                # 1. Fetch live internet results
                results = DDGS().text(search_query, max_results=5)
                
                # NEW: Check if DuckDuckGo blocked us or found nothing!
                if not results:
                    search_context = "Error: Search engine returned no data. Tell the user you cannot verify the live price right now."
                    print("🚨 DEBUG: DuckDuckGo returned NO results! (Possible rate limit)")
                else:
                    search_context = f"Live Web Results for '{search_query}':\n" + "\n".join([f"- {res['body']}" for res in results])
                
                # NEW: Print exactly what Satish is reading to your terminal!
                print("\n=== RAW DATA SATISH IS READING ===")
                print(search_context)
                print("==================================\n")
                
                # 2. Add the results to the chat history silently
                groq_messages.append({"role": "assistant", "content": reply})
                groq_messages.append({
                    "role": "user", 
                    "content": f"""Here is the raw data from the internet: 
                    
                    {search_context}
CRITICAL INSTRUCTIONS:
1. Search snippets can be messy or conflicting. Act as an expert data analyst.
2. If the data contains multiple different numbers (like gold prices), use your logical reasoning to deduce the correct one (e.g., distinguish between 1 gram vs 10 gram prices).
3. Ignore outdated data, SEO spam, or absurd outliers.
4. Speak the final, logically verified answer directly to me in a short sentence. Do NOT output the <SEARCH> tag again."""
                })
                
                # 3. THE SECOND TAP 
                chat_completion_2 = client.chat.completions.create(
                    messages=groq_messages,
                    model="llama-3.3-70b-versatile",
                    temperature=0.7,
                )
                reply = chat_completion_2.choices[0].message.content
            except Exception as e:
                reply = "I tried to check the internet, but my connection failed."
                print(f"🚨 SEARCH ERROR: {str(e)}")

        # --- PC COMMAND INTERCEPTORS ---
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