import { useEffect, useState } from "react";
import { supabase } from "../lib/supabase";
import { FlowCard } from "../components/FlowCard";
import type { Flow } from "../types";

export function FlowsPage() {
  const [flows, setFlows] = useState<Flow[]>([]);

  useEffect(() => {
    supabase.from("flows").select("*").order("created_at").then(({ data }) => {
      if (data) setFlows(data);
    });
  }, []);

  const handleToggle = (id: string, active: boolean) => {
    setFlows((prev) => prev.map((f) => f.id === id ? { ...f, is_active: active } : f));
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-gray-900">Flows</h1>
        <span className="text-sm text-gray-500">{flows.filter((f) => f.is_active).length} ativos</span>
      </div>

      {flows.length === 0 && (
        <p className="text-gray-400 text-sm">Nenhum flow cadastrado.</p>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {flows.map((flow) => (
          <FlowCard key={flow.id} flow={flow} onToggle={handleToggle} />
        ))}
      </div>
    </div>
  );
}
