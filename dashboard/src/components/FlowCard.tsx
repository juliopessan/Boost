import { useState } from "react";
import { supabase } from "../lib/supabase";
import type { Flow } from "../types";

const typeIcons: Record<string, string> = {
  text: "💬",
  button: "🔘",
  interactive: "📋",
  audio: "🎤",
  image: "🖼️",
  order: "📦",
  fallback: "🔀",
};

interface FlowCardProps {
  flow: Flow;
  onToggle: (id: string, active: boolean) => void;
}

export function FlowCard({ flow, onToggle }: FlowCardProps) {
  const [loading, setLoading] = useState(false);

  const handleToggle = async () => {
    if (!flow.handler_arn && !flow.is_active) return;
    setLoading(true);
    const { error } = await supabase
      .from("flows")
      .update({ is_active: !flow.is_active })
      .eq("id", flow.id);
    if (!error) onToggle(flow.id, !flow.is_active);
    setLoading(false);
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-5 flex items-start justify-between gap-4">
      <div className="flex items-start gap-3">
        <span className="text-2xl">{typeIcons[flow.trigger_type] ?? "⚡"}</span>
        <div>
          <p className="font-semibold text-gray-900">{flow.name}</p>
          <p className="text-xs text-gray-500 mt-0.5">
            Trigger: <span className="font-mono">{flow.trigger_type}</span>
          </p>
          <p className="text-xs text-gray-400 mt-0.5">
            Timeout: {flow.timeout_minutes}min
          </p>
        </div>
      </div>
      <button
        onClick={handleToggle}
        disabled={loading}
        className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 focus:outline-none ${
          flow.is_active ? "bg-green-500" : "bg-gray-200"
        } ${loading ? "opacity-50" : ""}`}
        aria-label={flow.is_active ? "Desativar flow" : "Ativar flow"}
      >
        <span
          className={`inline-block h-5 w-5 rounded-full bg-white shadow transform transition-transform duration-200 ${
            flow.is_active ? "translate-x-5" : "translate-x-0"
          }`}
        />
      </button>
    </div>
  );
}
