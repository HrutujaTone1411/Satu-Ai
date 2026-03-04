import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [status, setStatus] = useState("Checking...");
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState("");

  // NEW: We add a loading state to lock the UI while waiting
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/status")
      .then(response => response.json())
      .then(data => setStatus(data.status))
      .catch(() => setStatus("Offline"));
  }, []);

  const sendMessage = async () => {
    // If the box is empty OR if Satu is already thinking, do nothing!
    if (!inputText.trim() || isLoading) return;

    const newMessages = [...messages, { sender: "You", text: inputText }];
    setMessages(newMessages);
    setInputText("");

    // Lock the input box and button
    setIsLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: inputText }),
      });

      const data = await response.json();

      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: "Satu Ai", text: data.reply },
      ]);
    } catch (error) {
      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: "System", text: "Error connecting to Satu's brain." },
      ]);
    } finally {
      // Unlock the input box and button after we get a reply (or an error)
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container" style={{ padding: "20px", fontFamily: "sans-serif" }}>
      <h1>Satu Ai</h1>
      <p style={{ color: status === "Online" ? "green" : "red" }}>
        Status: {status}
      </p>

      <div
        className="chat-window"
        style={{
          border: "1px solid #ccc",
          height: "400px",
          overflowY: "scroll",
          padding: "10px",
          marginBottom: "10px",
          backgroundColor: "#f9f9f9",
          color: "#333"
        }}
      >
        {messages.length === 0 ? (
          <p style={{ color: "#888" }}>Say hello to start the conversation!</p>
        ) : (
          messages.map((msg, index) => (
            <div key={index} style={{ marginBottom: "10px", textAlign: msg.sender === "You" ? "right" : "left" }}>
              <strong>{msg.sender}: </strong>
              <span>{msg.text}</span>
            </div>
          ))
        )}
        {/* NEW: Show a typing indicator */}
        {isLoading && <p style={{ color: "#888", fontStyle: "italic" }}>Satu is typing...</p>}
      </div>

      <div style={{ display: "flex", gap: "10px" }}>
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Type a message (English, Marathi, or Hindi)..."
          disabled={isLoading} // Disables typing while loading
          style={{ flex: 1, padding: "10px", fontSize: "16px" }}
        />
        <button
          onClick={sendMessage}
          disabled={isLoading} // Disables clicking while loading
          style={{ padding: "10px 20px", fontSize: "16px", cursor: isLoading ? "not-allowed" : "pointer" }}
        >
          {isLoading ? "Sending..." : "Send"}
        </button>
      </div>
    </div>
  )
}

export default App