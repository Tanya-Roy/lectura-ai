import React, { useState, useRef, useEffect } from "react";
import {
  Send,
  Sparkles,
  Bot,
  User as UserIcon,
  Clock,
  ArrowRight,
  BookOpen,
  Loader2,
  Trash2,
} from "lucide-react";
import { PageContainer } from "../components/layout/PageContainer";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { sendChatMessage } from "../services/api";
import { ChatMessage, Citation } from "../types";

export const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "msg_init",
      role: "assistant",
      content:
        "Hello! I am your Lectura Study Assistant. I am grounded in your lecture's transcript, mathematical derivations, and verified notes. Ask me anything about the formulas, proofs, or concepts!",
      citations: [
        {
          timestamp_seconds: 120.0,
          label: "02:00 - Introduction",
          snippet: "Overview of loss functions and risk bounds.",
        },
      ],
      timestamp: "Just now",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [suggestedQuestions, setSuggestedQuestions] = useState<string[]>([
    "Why is L2 regularization necessary in high-dimensional domains?",
    "What is the time complexity of mini-batch gradient descent?",
    "How does the condition number affect optimization stability?",
  ]);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (messageText?: string) => {
    const query = (messageText || input).trim();
    if (!query || loading) return;

    setInput("");
    const userMsg: ChatMessage = {
      id: `user_${Date.now()}`,
      role: "user",
      content: query,
      timestamp: "Just now",
    };

    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const response = await sendChatMessage({
        message: query,
        video_id: "vid_ml_01",
        history: messages,
      });

      const botMsg: ChatMessage = {
        id: `assistant_${Date.now()}`,
        role: "assistant",
        content: response.message,
        citations: response.citations,
        timestamp: "Just now",
      };

      setMessages((prev) => [...prev, botMsg]);
      if (response.suggested_followups && response.suggested_followups.length > 0) {
        setSuggestedQuestions(response.suggested_followups);
      }
    } catch (err) {
      console.error("Chat error:", err);
      setMessages((prev) => [
        ...prev,
        {
          id: `err_${Date.now()}`,
          role: "assistant",
          content:
            "I encountered a temporary problem contacting the synthesis model. Here is the verified note summary on this topic: L2 regularization enforces strict convexity on empirical loss surfaces.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setMessages([
      {
        id: "msg_reset",
        role: "assistant",
        content: "Chat history cleared. What would you like to review next?",
      },
    ]);
  };

  return (
    <PageContainer
      title="AI Lecture Assistant"
      subtitle="Interactive Q&A strictly grounded in the video's transcripts and formulas."
      action={
        <Button variant="outline" size="sm" onClick={handleClear} className="gap-1.5">
          <Trash2 className="h-4 w-4" /> Clear Chat
        </Button>
      }
    >
      <div className="max-w-4xl mx-auto flex flex-col h-[calc(100vh-16rem)]">
        {/* Chat Feed */}
        <Card className="flex-1 border-slate-200 overflow-hidden flex flex-col bg-white shadow-sm">
          <div className="flex-1 p-6 overflow-y-auto space-y-6">
            {messages.map((msg, index) => (
              <div
                key={msg.id || index}
                className={`flex gap-3.5 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                {msg.role === "assistant" && (
                  <div className="h-8 w-8 rounded-lg bg-primary-100 text-primary-800 flex items-center justify-center shrink-0 mt-0.5">
                    <Bot className="h-4 w-4" />
                  </div>
                )}

                <div
                  className={`rounded-2xl p-4 max-w-xl text-sm leading-relaxed ${
                    msg.role === "user"
                      ? "bg-primary-700 text-white shadow-sm"
                      : "bg-slate-50 text-slate-900 border border-slate-200"
                  }`}
                >
                  <p className="whitespace-pre-wrap">{msg.content}</p>

                  {/* Timestamp Citations */}
                  {msg.citations && msg.citations.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-slate-200/80 space-y-1.5">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 block">
                        Verified Video Citations:
                      </span>
                      {msg.citations.map((c, i) => (
                        <div
                          key={i}
                          className="flex items-center gap-2 p-1.5 rounded-lg bg-white border border-slate-200 text-xs text-primary-900"
                        >
                          <Clock className="h-3 w-3 text-primary-600 shrink-0" />
                          <span className="font-semibold text-primary-700">{c.label}:</span>
                          <span className="line-clamp-1 text-slate-600 text-[11px]">{c.snippet}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {msg.role === "user" && (
                  <div className="h-8 w-8 rounded-lg bg-slate-900 text-white flex items-center justify-center shrink-0 mt-0.5">
                    <UserIcon className="h-4 w-4" />
                  </div>
                )}
              </div>
            ))}

            {loading && (
              <div className="flex gap-3.5 justify-start">
                <div className="h-8 w-8 rounded-lg bg-primary-100 text-primary-800 flex items-center justify-center shrink-0 mt-0.5">
                  <Bot className="h-4 w-4" />
                </div>
                <div className="bg-slate-50 border border-slate-200 rounded-2xl p-4 flex items-center gap-2 text-xs text-slate-500">
                  <Loader2 className="h-4 w-4 animate-spin text-primary-600" />
                  <span>Retrieving video transcript context...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Suggested Followups */}
          {suggestedQuestions.length > 0 && (
            <div className="px-6 py-2.5 bg-slate-50 border-t border-slate-100 flex items-center gap-2 overflow-x-auto">
              <span className="text-[11px] font-bold text-slate-400 shrink-0 uppercase tracking-wider">
                Suggested:
              </span>
              {suggestedQuestions.map((q, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSend(q)}
                  className="text-xs px-2.5 py-1 bg-white hover:bg-primary-50 hover:text-primary-800 border border-slate-200 rounded-full text-slate-600 transition-colors shrink-0 line-clamp-1"
                >
                  {q}
                </button>
              ))}
            </div>
          )}

          {/* Input Box */}
          <div className="p-4 bg-white border-t border-slate-200">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSend();
              }}
              className="flex items-center gap-2"
            >
              <input
                type="text"
                placeholder="Ask about equations, proofs, or timestamps in this lecture..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                className="flex-1 px-4 py-2.5 text-sm rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-primary-600 bg-white"
              />
              <Button type="submit" size="default" disabled={loading || !input.trim()} className="gap-2 px-5">
                <span>Send</span>
                <Send className="h-3.5 w-3.5" />
              </Button>
            </form>
          </div>
        </Card>
      </div>
    </PageContainer>
  );
};
