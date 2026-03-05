# 🤖 Satish AI - Personal Desktop Assistant

Satish is a full-stack, voice-activated AI desktop assistant designed to act as a highly intelligent, multilingual system companion. Built with an ultra-fast modern tech stack, Satish can hold contextual conversations, process spoken audio in multiple languages, and physically interact with the Windows operating system to open applications and local files.

## ✨ Key Features

* **🎙️ AI Voice Recognition:** Integrates Groq's Whisper API to perfectly transcribe spoken English, Hindi, and Marathi—even when mixed in the same sentence.
* **🔊 Dynamic Text-to-Speech:** Automatically detects the language of the AI's response and switches browser voices for natural-sounding playback.
* **💻 OS-Level Automation:** Capable of executing Windows commands to launch websites (YouTube, Google), system apps (Notepad, Calculator), and specific local project directories.
* **🧠 Contextual Memory:** Maintains short-term conversational history for natural, flowing interactions.
* **⏱️ Real-Time Awareness:** Dynamically injected system prompts give the AI real-time awareness of the current clock, date, and location.
* **🚀 One-Click Launcher:** Includes a custom Windows Batch script to simultaneously boot the Python server, React frontend, and browser UI with a single desktop click.

## 🛠️ Tech Stack

**Frontend (The Face & Ears)**
* React.js (Vite)
* Web Speech API (Text-to-Speech)
* MediaRecorder API (Audio Capture)
* Custom CSS (Cyberpunk/Dark Mode UI)

**Backend (The Brain & Hands)**
* Python 3 & FastAPI
* Groq API (Llama-3.3-70b-versatile for logic, Whisper-large-v3 for audio)
* Python `os`, `subprocess`, and `webbrowser` modules for OS control
* Uvicorn (ASGI Server)

## ⚙️ Local Setup & Installation

**1. Clone the repository**
```bash
git clone [https://github.com/YourUsername/satu-ai.git](https://github.com/YourUsername/satu-ai.git)
cd satu-ai