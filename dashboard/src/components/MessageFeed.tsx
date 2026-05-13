import { useEffect, useState } from "react";
import { supabase } from "../lib/supabase";
import type { Message } from "../types";
import { StatusBadge } from "./StatusBadge";

function maskPhone(hash: string) {
  return `****${hash.slice(-4)}`;
}

export function MessageFeed() {
  const [messages, setMessages] = useState<Message[]>([]);

  useEffect(() => {
    const load = async () => {
      const { data } = await supabase
        .from("messages")
        .select("*")
        .order("created_at", { ascending: false })
        .limit(10);
      if (data) setMessages(data);
    };

    load();

    const channel = supabase
      .channel("messages-feed")
      .on("postgres_changes", { event: "INSERT", schema: "public", table: "messages" }, (payload) => {
        setMessages((prev) => [payload.new as Message, ...prev].slice(0, 10));
      })
      .subscribe();

    return () => { supabase.removeChannel(channel); };
  }, []);

  return (
    <div className="bg-white rounded-lg border border-gray-200">
      <div className="px-5 py-4 border-b border-gray-100">
        <h3 className="font-semibold text-gray-800">Mensagens Recentes</h3>
      </div>
      <ul className="divide-y divide-gray-100">
        {messages.length === 0 && (
          <li className="px-5 py-4 text-sm text-gray-400">Nenhuma mensagem ainda.</li>
        )}
        {messages.map((m) => (
          <li key={m.id} className="px-5 py-3 flex items-center justify-between gap-4">
            <div className="flex items-center gap-3 min-w-0">
              <span className="text-xs text-gray-400 shrink-0">
                {new Date(m.created_at).toLocaleTimeString("pt-BR")}
              </span>
              <span className="text-sm font-mono text-gray-600">{maskPhone(m.phone_hash)}</span>
              <span className="text-xs text-gray-400 uppercase">{m.type}</span>
            </div>
            <div className="flex items-center gap-3 shrink-0">
              {m.latency_ms && (
                <span className="text-xs text-gray-400">{m.latency_ms}ms</span>
              )}
              <StatusBadge status={m.status} />
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
