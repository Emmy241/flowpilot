"use client";

import { MessageOut } from "@/lib/api";

export default function MessageBubble({ message }: { message: MessageOut }) {
  if (message.role === "tool") {
    return (
      <div className="text-xs text-gray-500 italic text-center my-2">
        {message.content}
      </div>
    );
  }

  const isUser = message.role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[75%] rounded-2xl px-4 py-2.5 text-sm whitespace-pre-wrap shadow-sm ${
          isUser
            ? "bg-blue-600 text-white"
            : "bg-gray-100 text-gray-900 border border-gray-200"
        }`}
      >
        {message.content ?? (message.tool_calls ? "…" : "")}
      </div>
    </div>
  );
}
