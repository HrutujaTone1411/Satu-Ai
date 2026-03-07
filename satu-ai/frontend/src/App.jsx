import { useState, useEffect, useRef } from 'react'
import './App.css'

function App() {
  const [status, setStatus] = useState("Checking...");
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const chatWindowRef = useRef(null);

  const isRecordingRef = useRef(false);
  const silenceTimerRef = useRef(null);
  const audioContextRef = useRef(null);
  const animationFrameRef = useRef(null);

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
    // NEW: Strip out the image URL so the browser doesn't try to read it!
    const spokenText = text.includes("IMAGE_URL:") ? text.split("IMAGE_URL:")[0] : text;

    const utterance = new SpeechSynthesisUtterance(spokenText);
    const containsDevanagari = /[\u0900-\u097F]/.test(spokenText);

    utterance.lang = containsDevanagari ? 'hi-IN' : 'en-IN';
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    window.speechSynthesis.speak(utterance);
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];
      isRecordingRef.current = true;
      setIsRecording(true);

      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      audioContextRef.current = audioContext;
      const analyser = audioContext.createAnalyser();
      const source = audioContext.createMediaStreamSource(stream);
      source.connect(analyser);
      analyser.fftSize = 512;
      const dataArray = new Uint8Array(analyser.frequencyBinCount);

      const detectSilence = () => {
        if (!isRecordingRef.current) return;
        analyser.getByteFrequencyData(dataArray);
        const volume = dataArray.reduce((a, b) => a + b) / dataArray.length;

        if (volume > 12) {
          if (silenceTimerRef.current) {
            clearTimeout(silenceTimerRef.current);
            silenceTimerRef.current = null;
          }
        } else {
          if (!silenceTimerRef.current) {
            silenceTimerRef.current = setTimeout(() => {
              stopRecording();
            }, 2000);
          }
        }
        animationFrameRef.current = requestAnimationFrame(detectSilence);
      };

      detectSilence();

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        setIsLoading(true);
        isRecordingRef.current = false;

        if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
        if (audioContextRef.current?.state !== 'closed') audioContextRef.current.close();
        stream.getTracks().forEach(track => track.stop());

        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        const formData = new FormData();
        formData.append("file", audioBlob, "voice.webm");

        try {
          const response = await fetch("http://127.0.0.1:8000/transcribe", {
            method: "POST",
            body: formData,
          });
          const data = await response.json();
          if (data.text) {
            setInputText(data.text);
            sendMessage(data.text);
          }
        } catch (error) {
          console.error("Transcription error:", error);
        } finally {
          setIsLoading(false);
        }
      };

      mediaRecorder.start();
    } catch (err) {
      alert("Microphone access denied.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecordingRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      isRecordingRef.current = false;
      if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
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

    setMessages([...messages, { sender: "You", text: finalMessage }]);
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
      setMessages((prev) => [...prev, { sender: "System", text: "Error connecting to Satish." }]);
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
          messages.map((msg, index) => {
            // NEW: Split the text and image apart so React can render them beautifully
            const hasImage = msg.text.includes("IMAGE_URL:");
            const textPart = hasImage ? msg.text.split("IMAGE_URL:")[0] : msg.text;
            const imageUrl = hasImage ? msg.text.split("IMAGE_URL:")[1] : null;

            return (
              <div key={index} className={`message-bubble ${msg.sender === 'You' ? 'message-you' : 'message-satish'}`}>
                <strong>{msg.sender === 'You' ? 'USER' : 'SATISH'}: </strong>
                <span>{textPart}</span>

                {/* NEW: The Magic Image Renderer */}
                {imageUrl && (
                  <img
                    src={imageUrl}
                    alt="AI Generated"
                    style={{ width: '100%', borderRadius: '10px', marginTop: '10px', boxShadow: '0 4px 12px rgba(0,0,0,0.4)' }}
                  />
                )}
              </div>
            );
          })
        )}
        {isLoading && <div className="system-text">Satish is processing...</div>}
      </div>

      <div className="input-area">
        <button
          className={`btn btn-mic ${isRecording ? 'listening' : ''}`}
          onClick={isRecording ? stopRecording : startRecording}
          disabled={isLoading}
          style={{ width: isRecording ? "140px" : "auto", transition: "0.3s" }}
        >
          {isRecording ? "LISTENING..." : "🎤"}
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