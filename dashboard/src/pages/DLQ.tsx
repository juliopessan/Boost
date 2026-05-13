import { useEffect, useState } from "react";
import { supabase } from "../lib/supabase";
import { JsonViewer } from "../components/JsonViewer";
import type { DlqEntry } from "../types";

export function DLQPage() {
  const [entries, setEntries] = useState<DlqEntry[]>([]);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [requeueing, setRequeueing] = useState<string | null>(null);

  useEffect(() => {
    supabase.from("dlq_entries").select("*").order("created_at", { ascending: false }).then(({ data }) => {
      if (data) setEntries(data);
    });
  }, []);

  const requeue = async (entry: DlqEntry) => {
    setRequeueing(entry.id);
    const { error } = await supabase.from("dlq_entries").update({ retry_count: entry.retry_count + 1 }).eq("id", entry.id);
    if (!error) {
      setEntries((prev) => prev.map((e) => e.id === entry.id ? { ...e, retry_count: e.retry_count + 1 } : e));
    }
    setRequeueing(null);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-gray-900">Dead Letter Queue</h1>
        <span className="text-sm text-red-500 font-medium">{entries.length} mensagens com falha</span>
      </div>

      {entries.length === 0 && (
        <div className="bg-white rounded-lg border border-gray-200 p-8 text-center text-gray-400">
          Nenhuma mensagem na DLQ.
        </div>
      )}

      <div className="space-y-3">
        {entries.map((entry) => (
          <div key={entry.id} className="bg-white rounded-lg border border-red-100 overflow-hidden">
            <div className="px-5 py-4 flex items-start justify-between gap-4">
              <div>
                <p className="text-sm font-mono text-gray-700">{entry.message_id}</p>
                <p className="text-xs text-red-600 mt-1">{entry.last_error}</p>
                <p className="text-xs text-gray-400 mt-1">
                  {entry.retry_count}x tentativas · {new Date(entry.created_at).toLocaleString("pt-BR")}
                </p>
              </div>
              <div className="flex gap-2 shrink-0">
                <button
                  onClick={() => setExpanded(expanded === entry.id ? null : entry.id)}
                  className="text-xs px-3 py-1.5 rounded border border-gray-200 text-gray-600 hover:bg-gray-50"
                >
                  {expanded === entry.id ? "Ocultar" : "Ver payload"}
                </button>
                <button
                  onClick={() => requeue(entry)}
                  disabled={requeueing === entry.id}
                  className="text-xs px-3 py-1.5 rounded bg-amber-500 text-white hover:bg-amber-600 disabled:opacity-50"
                >
                  {requeueing === entry.id ? "..." : "Reenfileirar"}
                </button>
              </div>
            </div>
            {expanded === entry.id && (
              <div className="px-5 pb-4">
                <JsonViewer data={entry.payload} />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
