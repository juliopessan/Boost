export type MessageStatus = "queued" | "processing" | "success" | "error" | "dlq";
export type MessageType = "text" | "button" | "interactive" | "audio" | "image" | "video" | "document" | "order" | "unknown";

export interface Flow {
  id: string;
  name: string;
  trigger_type: MessageType;
  handler_arn: string;
  is_active: boolean;
  timeout_minutes: number;
  created_at: string;
}

export interface Message {
  id: string;
  flow_id: string;
  phone_hash: string;
  type: MessageType;
  status: MessageStatus;
  latency_ms: number | null;
  error_reason: string | null;
  created_at: string;
}

export interface DlqEntry {
  id: string;
  message_id: string;
  payload: Record<string, unknown>;
  retry_count: number;
  last_error: string;
  created_at: string;
}

export interface HourlyMetric {
  hour: string;
  success: number;
  error: number;
  total: number;
}

export interface DashboardMetrics {
  received_today: number;
  processed_today: number;
  errors_today: number;
  dlq_count: number;
  received_trend: number;
  processed_trend: number;
  errors_trend: number;
}
