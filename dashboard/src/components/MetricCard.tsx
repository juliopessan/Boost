interface MetricCardProps {
  label: string;
  value: number;
  trend?: number;
  suffix?: string;
}

export function MetricCard({ label, value, trend, suffix = "" }: MetricCardProps) {
  const trendPositive = trend !== undefined && trend >= 0;

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-5">
      <p className="text-sm text-gray-500 font-medium">{label}</p>
      <p className="mt-1 text-3xl font-bold text-gray-900">
        {value.toLocaleString("pt-BR")}{suffix}
      </p>
      {trend !== undefined && (
        <p className={`mt-1 text-sm font-medium ${trendPositive ? "text-green-600" : "text-red-600"}`}>
          {trendPositive ? "▲" : "▼"} {Math.abs(trend)}% vs ontem
        </p>
      )}
    </div>
  );
}
