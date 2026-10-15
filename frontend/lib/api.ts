const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

const TOKEN_KEY = "flowpilot_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string) {
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  window.localStorage.removeItem(TOKEN_KEY);
}

type ApiOptions = {
  method?: "GET" | "POST" | "PUT" | "DELETE";
  body?: unknown;
  auth?: boolean;
};

async function request<T>(path: string, opts: ApiOptions = {}): Promise<T> {
  const { method = "GET", body, auth = true } = opts;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (auth) {
    const token = getToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (res.status === 401) {
    clearToken();
    if (typeof window !== "undefined") window.location.href = "/login";
    throw new Error("Unauthorized");
  }

  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const data = await res.json();
      if (data?.detail) detail = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
    } catch {
      /* not json */
    }
    throw new Error(detail);
  }

  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export type TokenResponse = { access_token: string; token_type: string };

export type MessageOut = {
  id: string;
  role: "user" | "assistant" | "tool";
  content: string | null;
  tool_calls: unknown[] | null;
  tool_call_id: string | null;
  created_at: string;
};

export type ApprovalOut = {
  id: string;
  tool_call_id: string;
  tool_name: string;
  tool_args: Record<string, unknown>;
  status: "pending" | "approved" | "rejected";
};

export type ChatResponse = {
  conversation_id: string;
  message: MessageOut;
  approval: ApprovalOut | null;
};

export type ConversationOut = {
  id: string;
  title: string | null;
  created_at: string;
};

export type UserOut = {
  id: string;
  email: string;
  created_at: string;
};

export const api = {
  signup: (email: string, password: string) =>
    request<TokenResponse>("/auth/signup", { method: "POST", body: { email, password }, auth: false }),

  login: (email: string, password: string) =>
    request<TokenResponse>("/auth/login", { method: "POST", body: { email, password }, auth: false }),

  me: () => request<UserOut>("/me"),

  chat: (message: string, conversationId?: string) =>
    request<ChatResponse>("/chat", {
      method: "POST",
      body: { message, conversation_id: conversationId ?? null },
    }),

  listConversations: () => request<ConversationOut[]>("/conversations"),

  listMessages: (conversationId: string) =>
    request<MessageOut[]>(`/conversations/${conversationId}/messages`),

  approve: (approvalId: string) =>
    request<ApprovalOut>(`/approvals/${approvalId}/approve`, { method: "POST" }),

  reject: (approvalId: string) =>
    request<ApprovalOut>(`/approvals/${approvalId}/reject`, { method: "POST" }),
};
