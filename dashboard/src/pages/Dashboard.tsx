import { useEffect, useState } from "react";
import { supabase } from "../lib/supabase";
import { HourlyChart } from "../components/HourlyChart";
import { MessageFeed } from "../components/MessageFeed";
import { MetricCard } from "../components/MetricCard";
import type { DashboardMetrics, HourlyMetric } from "../types";

const REFRESH_MS = 30_000;

async function fetchMetrics(): Promise<DashboardMetrics> {
  const today = new Date().toISOString().split("T")[0];

  const [received, processed, errors, dlq] = await Promise.all([
    supabase.from("messages").select("id", { count: "exact", head: true }).gte("created_at", today),
    supabase.from("messages").select("id", { count: "exact", head: true }).eq("status", "success").gte("created_at", today),
    supabase.from("messages").select("id", { count: "exact", head: true }).eq("status", "error").gte("created_at", today),
    supabase.from("dlq_entries").select("id", { count: "exact", head: true }),
  ]);

  return {
    received_today: received.count ?? 0,
    processed_today: processed.count ?? 0,
    errors_today: errors.count ?? 0,
    dlq_count: dlq.count ?? 0,
    received_trend: 0,
    processed_trend: 0,
    errors_trend: 0,
  };
}

async function fetchHourly(): Promise<HourlyMetric[]> {
  const { data } = await supabase.rpc("get_hourly_metrics");
  return data ?? [];
}

export function DashboardPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [hourly, setHourly] = useState<HourlyMetric[]>([]);

  const load = async () => {
    const [m, h] = await Promise.all([fetchMetrics(), fetchHourly()]);
    setMetrics(m);
    setHourly(h);
  };

  useEffect(() => {
    load();
    const interval = setInterval(load, REFRESH_MS);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold text-gray-900">Dashboard</h1>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard label="Recebidas hoje" value={metrics?.received_today ?? 0} trend={metrics?.received_trend} />
        <MetricCard label="Processadas" value={metrics?.processed_today ?? 0} trend={metrics?.processed_trend} />
        <MetricCard label="Erros" value={metrics?.errors_today ?? 0} trend={metrics?.errors_trend} />
        <MetricCard label="DLQ" value={metrics?.dlq_count ?? 0} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <HourlyChart data={hourly} />
        <MessageFeed />
      </div>
    </div>
  );
}
