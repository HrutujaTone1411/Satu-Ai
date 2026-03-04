import { useState, useEffect, useRef } from 'react'
import './App.css'

function App() {
  const [status, setStatus] = useState("Checking...");
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);

  // Auto-scroll to the bottom of the chat
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
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    window.speechSynthesis.speak(utterance);
  };

  const startListening = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Your browser does not support voice input. Please use Google Chrome.");
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.lang = 'en-IN';
    recognition.interimResults = false;

    recognition.onstart = () => setIsListening(true);
    recognition.onresult = (event) => setInputText(event.results[0][0].transcript);
    recognition.onerror = () => setIsListening(false);
    recognition.onend = () => setIsListening(false);
    recognition.start();
  };

  const sendMessage = async () => {
    if (!inputText.trim() || isLoading) return;

    // NEW: Package the conversation history for the backend
    const chatHistory = messages
      .filter(msg => msg.sender === "You" || msg.sender === "Satish")
      .map(msg => ({
        role: msg.sender === "You" ? "user" : "assistant",
        content: msg.text
      }));

    const newMessages = [...messages, { sender: "You", text: inputText }];
    setMessages(newMessages);
    setInputText("");
    setIsLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        // NEW: We are now sending BOTH the new message and the history array
        body: JSON.stringify({ message: inputText, history: chatHistory }),
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
        <button
          className={`btn btn-mic ${isListening ? 'listening' : ''}`}
          onClick={startListening}
          disabled={isListening || isLoading}
          title="Click to speak"
        >
          🎤
        </button>

        <input
          type="text"
          className="chat-input"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Enter command or speak..."
          disabled={isLoading}
        />

        <button className="btn" onClick={sendMessage} disabled={isLoading}>
          {isLoading ? "TX..." : "SEND"}
        </button>
      </div>
    </div>
  )
}

export default App