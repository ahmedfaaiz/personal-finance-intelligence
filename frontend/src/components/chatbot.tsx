import { useState } from "react";
import { api } from "../services/api";

type Message = {
  role: "user" | "bot";
  text: string;
};

export function Chatbot() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "bot",
      text: "Hi! I'm your personal finance assistant. How can I help you?",
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    const message = input.trim();

    if (!message || loading) return;

    setMessages((prev) => [...prev, { role: "user", text: message }]);
    setInput("");
    setLoading(true);

    try {
      const data = await api.chat(message);

      setMessages((prev) => [
        ...prev,
        { role: "bot", text: data.response },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          text: "Sorry, I couldn't connect to the AI right now.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 w-96 bg-white rounded-2xl shadow-2xl border border-gray-200 overflow-hidden">
      <div className="bg-gray-800 text-white px-5 py-4">
        <h2 className="font-semibold text-lg">Finance Assistant</h2>
        <p className="text-sm text-gray-300">Powered by Gemini</p>
      </div>

      <div className="h-96 overflow-y-auto p-4 space-y-3">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${
              message.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-2 text-sm ${
                message.role === "user"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 text-gray-800"
              }`}
            >
              {message.text}
            </div>
          </div>
        ))}

        {loading && (
          <div className="text-sm text-gray-500">
            Thinking...
          </div>
        )}
      </div>

      <div className="border-t p-3 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              sendMessage();
            }
          }}
          placeholder="Ask about your finances..."
          className="flex-1 border rounded-xl px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500"
        />

        <button
          onClick={sendMessage}
          disabled={loading || !input.trim()}
          className="bg-blue-600 text-white px-4 py-2 rounded-xl disabled:opacity-50"
        >
          Send
        </button>
      </div>
    </div>
  );
}