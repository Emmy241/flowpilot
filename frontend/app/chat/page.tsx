"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import {
  api,
  getToken,
  clearToken,
  UserOut,
  MessageOut,
  ApprovalOut,
  ConversationOut,
} from "@/lib/api";
import MessageBubble from "@/components/MessageBubble";
import ApprovalCard from "@/components/ApprovalCard";

type ChatItem =
  | { kind: "message"; data: MessageOut }
  | { kind: "approval"; data: ApprovalOut };

export default function ChatPage() {
  const router = useRouter();
  const [user, setUser] = useState<UserOut | null>(null);
  const [conversations, setConversations] = useState<ConversationOut[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [items, setItems] = useState<ChatItem[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!getToken()) {
      router.replace("/login");
      return;
    }
    api.me().then(setUser).catch(() => {
      clearToken();
      router.replace("/login");
    });
    api.listConversations().then(setConversations).catch(() => {});
  }, [router]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [items]);

  async function loadConversation(id: string) {
    setConversationId(id);
    setError(null);
    const msgs = await api.listMessages(id);
    setItems(msgs.map((m) => ({ kind: "message", data: m })));
  }

  function startNew() {
    setConversationId(null);
    setItems([]);
    setError(null);
  }

  async function send(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim() || sending) return;
    const text = input.trim();
    setInput("");
    setError(null);
    setSending(true);

    const optimistic: MessageOut = {
      id: `tmp-${Date.now()}`,
      role: "user",
      content: text,
      tool_calls: null,
      tool_call_id: null,
      created_at: new Date().toISOString(),
    };
    setItems((prev) => [...prev, { kind: "message", data: optimistic }]);

    try {
      const res = await api.chat(text, conversationId ?? undefined);
      setConversationId(res.conversation_id);
      setItems((prev) => {
        const next = [...prev, { kind: "message" as const, data: res.message }];
        if (res.approval)
          next.push({ kind: "approval" as const, data: res.approval });
        return next;
      });
      api.listConversations().then(setConversations).catch(() => {});
    } catch (err) {
      setError(err instanceof Error ? err.message : "Send failed");
    } finally {
      setSending(false);
    }
  }

  function onApprovalResolved(
    approvalId: string,
    status: "approved" | "rejected"
  ) {
    setItems((prev) =>
      prev.map((it) =>
        it.kind === "approval" && it.data.id === approvalId
          ? { ...it, data: { ...it.data, status } }
          : it
      )
    );
  }

  if (!user)
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100 text-sm text-gray-600">
        Loading…
      </div>
    );

  return (
    <div className="min-h-screen flex bg-white text-gray-900">
      {/* Sidebar */}
      <aside className="w-64 border-r border-gray-200 bg-gray-50 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <div className="font-bold text-gray-900">FlowPilot</div>
          <div className="text-xs text-gray-600 truncate">{user.email}</div>
        </div>

        <button
          onClick={startNew}
          className="m-3 rounded-md bg-blue-600 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-700"
        >
          + New chat
        </button>

        <div className="flex-1 overflow-y-auto px-2 pb-3 space-y-1">
          {conversations.length === 0 && (
            <div className="text-xs text-gray-500 px-2 py-1">
              No conversations yet
            </div>
          )}
          {conversations.map((c) => {
            const active = conversationId === c.id;
            return (
              <button
                key={c.id}
                onClick={() => loadConversation(c.id)}
                className={`w-full text-left text-sm px-2.5 py-2 rounded-md truncate transition-colors ${
                  active
                    ? "bg-blue-100 text-blue-900 font-medium"
                    : "text-gray-700 hover:bg-gray-200 hover:text-gray-900"
                }`}
                title={c.title ?? "(untitled)"}
              >
                {c.title ?? "(untitled)"}
              </button>
            );
          })}
        </div>

        <div className="p-3 border-t border-gray-200">
          <button
            onClick={() => {
              clearToken();
              router.push("/login");
            }}
            className="w-full text-sm font-medium text-gray-700 hover:text-gray-900"
          >
            Sign out
          </button>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 flex flex-col bg-white">
        <div className="flex-1 overflow-y-auto p-6 space-y-3">
          {items.length === 0 && (
            <div className="text-center text-gray-500 text-sm mt-24">
              Try: “Remind me to call mom tomorrow at 6pm”
            </div>
          )}
          {items.map((it) =>
            it.kind === "message" ? (
              <MessageBubble key={it.data.id} message={it.data} />
            ) : (
              <ApprovalCard
                key={it.data.id}
                approval={it.data}
                onResolved={(status) => onApprovalResolved(it.data.id, status)}
              />
            )
          )}
          <div ref={bottomRef} />
        </div>

        {error && (
          <div className="mx-6 mb-2 text-sm text-red-700 bg-red-50 border border-red-200 rounded-md px-3 py-2">
            {error}
          </div>
        )}

        <form
          onSubmit={send}
          className="border-t border-gray-200 p-4 flex gap-2 bg-white"
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type a message…"
            disabled={sending}
            className="flex-1 rounded-md border border-gray-300 bg-white px-3 py-2.5 text-sm text-gray-900 placeholder-gray-400 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
          />
          <button
            type="submit"
            disabled={sending || !input.trim()}
            className="rounded-md bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-blue-700 disabled:opacity-50"
          >
            {sending ? "…" : "Send"}
          </button>
        </form>
      </main>
    </div>
  );
}
