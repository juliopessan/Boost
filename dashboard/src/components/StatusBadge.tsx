import type { MessageStatus } from "../types";

const variants: Record<MessageStatus, string> = {
  success: "bg-green-100 text-green-800",
  error: "bg-red-100 text-red-800",
  processing: "bg-amber-100 text-amber-800",
  queued: "bg-gray-100 text-gray-700",
  dlq: "bg-red-200 text-red-900",
};

const labels: Record<MessageStatus, string> = {
  success: "Sucesso",
  error: "Erro",
  processing: "Processando",
  queued: "Na fila",
  dlq: "DLQ",
};

export function StatusBadge({ status }: { status: MessageStatus }) {
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${variants[status]}`}>
      {labels[status]}
    </span>
  );
}
