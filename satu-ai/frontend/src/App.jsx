import { useState, useEffect, useRef } from 'react'
import './App.css'

function App() {
  const [status, setStatus] = useState("Checking...");
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // NEW: Real audio recording states
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const chatWindowRef = useRef(null);

  useEffect(() => {
    if (chatWindowRef.current) {
      chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/status")
      .then(response => response.json())
      .then(data => setStatus(data.status))
      .catch(() => setStatus("Offline"));
  }, []);

  const speakText = (text) => {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    const containsDevanagari = /[\u0900-\u097F]/.test(text);

    if (containsDevanagari) {
      utterance.lang = 'hi-IN';
    } else {
      utterance.lang = 'en-IN';
    }
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    window.speechSynthesis.speak(utterance);
  };

  // --- NEW: THE AUDIO RECORDER LOGIC ---
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        setIsLoading(true);
        // 1. Package the audio into a file
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        const formData = new FormData();
        formData.append("file", audioBlob, "voice.webm");

        try {
          // 2. Send the audio file to Python to be transcribed
          const response = await fetch("http://127.0.0.1:8000/transcribe", {
            method: "POST",
            body: formData,
          });
          const data = await response.json();

          if (data.text) {
            setInputText(data.text);
            sendMessage(data.text); // 3. Auto-send the transcribed text!
          } else {
            console.error("Transcription failed:", data.error);
          }
        } catch (error) {
          console.error("Error sending audio:", error);
        } finally {
          setIsLoading(false);
          // Turn off the red recording light on the browser tab
          stream.getTracks().forEach(track => track.stop());
        }
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      alert("Microphone access denied. Please allow microphone permissions in your browser.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop(); // This triggers the onstop event above
      setIsRecording(false);
    }
  };

  const sendMessage = async (overrideText = null) => {
    const finalMessage = typeof overrideText === 'string' ? overrideText : inputText;
    if (!finalMessage.trim() || isLoading) return;

    const chatHistory = messages
      .filter(msg => msg.sender === "You" || msg.sender === "Satish")
      .map(msg => ({
        role: msg.sender === "You" ? "user" : "assistant",
        content: msg.text
      }));

    const newMessages = [...messages, { sender: "You", text: finalMessage }];
    setMessages(newMessages);
    setInputText("");
    setIsLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: finalMessage, history: chatHistory }),
      });
      const data = await response.json();
      setMessages((prev) => [...prev, { sender: "Satish", text: data.reply }]);
      speakText(data.reply);
    } catch (error) {
      setMessages((prev) => [...prev, { sender: "System", text: "Error connecting to Satish's core." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <div className="header">
        <h1>SATISH AI</h1>
        <div className={`status-indicator ${status === 'Online' ? 'online' : 'offline'}`}>
          SYSTEM STATUS: {status.toUpperCase()}
        </div>
      </div>

      <div className="chat-window" ref={chatWindowRef}>
        {messages.length === 0 ? (
          <div className="system-text">Awaiting user input...</div>
        ) : (
          messages.map((msg, index) => (
            <div key={index} className={`message-bubble ${msg.sender === 'You' ? 'message-you' : 'message-satish'}`}>
              <strong>{msg.sender === 'You' ? 'USER' : 'SATISH'}: </strong>
              <span>{msg.text}</span>
            </div>
          ))
        )}
        {isLoading && <div className="system-text">Satish is processing...</div>}
      </div>

      <div className="input-area">
        {/* The new smart recording button */}
        <button
          className={`btn btn-mic ${isRecording ? 'listening' : ''}`}
          onClick={isRecording ? stopRecording : startRecording}
          disabled={isLoading && !isRecording}
          style={{ width: isRecording ? "180px" : "auto", transition: "0.3s" }}
        >
          {isRecording ? "🛑 STOP & SEND" : "🎤"}
        </button>

        <input
          type="text"
          className="chat-input"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Enter command or click mic..."
          disabled={isLoading || isRecording}
        />

        <button className="btn" onClick={sendMessage} disabled={isLoading || isRecording}>
          {isLoading ? "TX..." : "SEND"}
        </button>
      </div>
    </div>
  )
}

export default App