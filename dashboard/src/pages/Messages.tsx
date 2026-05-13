import { useEffect, useState } from "react";
import { supabase } from "../lib/supabase";
import { StatusBadge } from "../components/StatusBadge";
import type { Message, MessageStatus } from "../types";

const PAGE_SIZE = 20;

function maskPhone(hash: string) {
  return `****${hash.slice(-4)}`;
}

export function MessagesPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [status, setStatus] = useState<MessageStatus | "all">("all");
  const [page, setPage] = useState(0);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    let query = supabase
      .from("messages")
      .select("*", { count: "exact" })
      .order("created_at", { ascending: false })
      .range(page * PAGE_SIZE, (page + 1) * PAGE_SIZE - 1);

    if (status !== "all") query = query.eq("status", status);

    query.then(({ data, count }) => {
      if (data) setMessages(data);
      if (count !== null) setTotal(count);
    });
  }, [status, page]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-gray-900">Mensagens</h1>
        <select
          value={status}
          onChange={(e) => { setStatus(e.target.value as MessageStatus | "all"); setPage(0); }}
          className="text-sm border border-gray-200 rounded-md px-3 py-1.5 bg-white"
        >
          <option value="all">Todos os status</option>
          <option value="success">Sucesso</option>
          <option value="error">Erro</option>
          <option value="queued">Na fila</option>
          <option value="dlq">DLQ</option>
        </select>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="text-left px-4 py-3 text-gray-500 font-medium">Horário</th>
              <th className="text-left px-4 py-3 text-gray-500 font-medium">Telefone</th>
              <th className="text-left px-4 py-3 text-gray-500 font-medium">Tipo</th>
              <th className="text-left px-4 py-3 text-gray-500 font-medium">Status</th>
              <th className="text-right px-4 py-3 text-gray-500 font-medium">Latência</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {messages.map((m) => (
              <tr key={m.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-gray-500 text-xs">
                  {new Date(m.created_at).toLocaleString("pt-BR")}
                </td>
                <td className="px-4 py-3 font-mono text-gray-700">{maskPhone(m.phone_hash)}</td>
                <td className="px-4 py-3 text-gray-600 uppercase text-xs">{m.type}</td>
                <td className="px-4 py-3"><StatusBadge status={m.status} /></td>
                <td className="px-4 py-3 text-right text-gray-500">
                  {m.latency_ms ? `${m.latency_ms}ms` : "—"}
                </td>
              </tr>
            ))}
            {messages.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-gray-400">
                  Nenhuma mensagem encontrada.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between text-sm text-gray-500">
        <span>{total} mensagens no total</span>
        <div className="flex gap-2">
          <button
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0}
            className="px-3 py-1 rounded border border-gray-200 disabled:opacity-40"
          >
            ← Anterior
          </button>
          <button
            onClick={() => setPage((p) => p + 1)}
            disabled={(page + 1) * PAGE_SIZE >= total}
            className="px-3 py-1 rounded border border-gray-200 disabled:opacity-40"
          >
            Próxima →
          </button>
        </div>
      </div>
    </div>
  );
}
