import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend,
} from "chart.js";
import { Bar } from "react-chartjs-2";
import type { HourlyMetric } from "../types";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

interface HourlyChartProps {
  data: HourlyMetric[];
}

export function HourlyChart({ data }: HourlyChartProps) {
  const chartData = {
    labels: data.map((d) => d.hour),
    datasets: [
      {
        label: "Sucesso",
        data: data.map((d) => d.success),
        backgroundColor: "#22c55e",
        borderRadius: 4,
      },
      {
        label: "Erro",
        data: data.map((d) => d.error),
        backgroundColor: "#ef4444",
        borderRadius: 4,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: { legend: { position: "top" as const } },
    scales: {
      x: { stacked: true },
      y: { stacked: true, beginAtZero: true },
    },
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-5">
      <h3 className="font-semibold text-gray-800 mb-4">Volume por Hora</h3>
      <Bar data={chartData} options={options} />
    </div>
  );
}
