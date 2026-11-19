
import { useEffect, useRef, useState } from "react";
import {
  Bot, Send, X, Sparkles, MessageCircle, LoaderCircle
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "./Chatbot.css";

const API_URL = "http://127.0.0.1:8000/api/chat/";

const suggestions = [
  "Analyze all my machines",
  "Which machines need attention?",
  "Summarize upcoming maintenance",
  "Give me maintenance recommendations"
];

function Chatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading, isOpen]);

  async function sendMessage(text = input) {
    const message = text.trim();

    if (!message || loading) return;

    setError("");
    setInput("");

    const previousMessages = messages;

    const updatedMessages = [
      ...previousMessages,
      { role: "user", content: message }
    ];

    setMessages(updatedMessages);
    setLoading(true);

    try {
      const history = previousMessages.slice(-10).map(item => ({
        role: item.role,
        content: item.content
      }));

      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          message,
          history
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "The AI assistant could not process your request."
        );
      }

      if (!data.reply) {
        throw new Error("The AI returned an empty response.");
      }

      setMessages(current => [
        ...current,
        { role: "assistant", content: data.reply }
      ]);

    } catch (err) {
      setError(err.message || "Unable to connect to Maintena AI.");
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(event) {
    event.preventDefault();
    sendMessage();
  }

  function handleKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  }

  return (
    <>
      {!isOpen && (
        <button
          className="chat-launcher"
          onClick={() => setIsOpen(true)}
          aria-label="Open Maintena AI"
        >
          <MessageCircle size={22} />
          <span>Ask Maintena AI</span>
          <span className="chat-launcher-dot" />
        </button>
      )}

      {isOpen && (
        <section className="chat-window">

          <header className="chat-header">
            <div className="chat-brand">
              <div className="chat-brand-icon">
                <Bot size={22} />
              </div>

              <div>
                <strong>Maintena AI</strong>
                <span><i /> AI OPERATIONS ASSISTANT</span>
              </div>
            </div>

            <button
              className="chat-close"
              onClick={() => setIsOpen(false)}
              aria-label="Close chat"
            >
              <X size={19} />
            </button>
          </header>

          <div className="chat-messages">

            {messages.length === 0 && (
              <div className="chat-welcome">

                <div className="chat-welcome-icon">
                  <Sparkles size={25} />
                </div>

                <h3>Welcome to Maintena AI</h3>

                <p>
                  Your intelligent industrial operations assistant.
                  Ask me about your machines, maintenance schedules
                  and operational risks.
                </p>

                <div className="chat-suggestions">
                  <span>QUICK QUESTIONS</span>

                  {suggestions.map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => sendMessage(suggestion)}
                      disabled={loading}
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>

              </div>
            )}

            {messages.map((message, index) => (
              <div
                key={index}
                className={`chat-message ${message.role}`}
              >

                {message.role === "assistant" && (
                  <div className="message-avatar">
                    <Bot size={15} />
                  </div>
                )}

                <div className="message-content">

                  {message.role === "assistant" ? (
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {message.content}
                    </ReactMarkdown>
                  ) : (
                    message.content
                  )}

                </div>

              </div>
            ))}

            {loading && (
              <div className="chat-message assistant">

                <div className="message-avatar">
                  <Bot size={15} />
                </div>

                <div className="message-content typing">
                  <LoaderCircle size={15} className="chat-spinner" />
                  Analyzing your facility...
                </div>

              </div>
            )}

            {error && (
              <div className="chat-error">
                <strong>Message failed</strong>
                <span>{error}</span>
                <button onClick={() => setError("")}>Dismiss</button>
              </div>
            )}

            <div ref={bottomRef} />

          </div>

          <form className="chat-input-area" onSubmit={handleSubmit}>

            <textarea
              value={input}
              onChange={event => setInput(event.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about your machines..."
              rows={1}
              maxLength={2000}
              disabled={loading}
            />

            <button
              type="submit"
              disabled={!input.trim() || loading}
              aria-label="Send message"
            >
              <Send size={17} />
            </button>

          </form>

          <div className="chat-disclaimer">
            AI responses are based on available facility records.
          </div>

        </section>
      )}
    </>
  );
}

export default Chatbot;
