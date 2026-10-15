"use client";

import { useState } from "react";
import { ApprovalOut, api } from "@/lib/api";

type Props = {
  approval: ApprovalOut;
  onResolved: (status: "approved" | "rejected") => void;
};

export default function ApprovalCard({ approval, onResolved }: Props) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const args = approval.tool_args as { title?: string; description?: string };

  async function act(kind: "approve" | "reject") {
    setBusy(true);
    setError(null);
    try {
      if (kind === "approve") await api.approve(approval.id);
      else await api.reject(approval.id);
      onResolved(kind === "approve" ? "approved" : "rejected");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Action failed");
    } finally {
      setBusy(false);
    }
  }

  if (approval.status !== "pending") {
    return (
      <div
        className={`border rounded-xl p-3 text-sm ${
          approval.status === "approved"
            ? "bg-green-50 border-green-200 text-green-900"
            : "bg-gray-50 border-gray-200 text-gray-700"
        }`}
      >
        {approval.status === "approved" ? "✅ Approved" : "❌ Rejected"}:{" "}
        <span className="font-semibold">{args.title}</span>
      </div>
    );
  }

  return (
    <div className="border-2 border-blue-300 bg-blue-50 rounded-xl p-4 space-y-3 shadow-sm">
      <div className="text-xs uppercase tracking-wide text-blue-700 font-bold">
        Proposed action
      </div>
      <div className="text-sm">
        <div className="font-semibold text-gray-900">
          Create task: {args.title ?? "(no title)"}
        </div>
        {args.description && (
          <div className="text-gray-700 mt-1">{args.description}</div>
        )}
      </div>

      {error && (
        <div className="text-xs text-red-700 bg-red-50 border border-red-200 rounded px-2 py-1">
          {error}
        </div>
      )}

      <div className="flex gap-2">
        <button
          disabled={busy}
          onClick={() => act("approve")}
          className="flex-1 rounded-md bg-blue-600 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-700 disabled:opacity-50"
        >
          Approve
        </button>
        <button
          disabled={busy}
          onClick={() => act("reject")}
          className="flex-1 rounded-md bg-white border border-gray-300 py-2 text-sm font-semibold text-gray-800 hover:bg-gray-100 disabled:opacity-50"
        >
          Reject
        </button>
      </div>
    </div>
  );
}
