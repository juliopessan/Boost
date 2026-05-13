import { useEffect, useState } from "react";
import { supabase } from "../lib/supabase";

interface Settings {
  dlq_alert_threshold: number;
  default_session_timeout: number;
  notification_email: string;
  slack_webhook_url: string;
}

export function SettingsPage() {
  const [form, setForm] = useState<Settings>({
    dlq_alert_threshold: 10,
    default_session_timeout: 30,
    notification_email: "",
    slack_webhook_url: "",
  });
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    supabase.from("settings").select("*").single().then(({ data }) => {
      if (data) setForm(data);
    });
  }, []);

  const save = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    await supabase.from("settings").upsert(form);
    setSaving(false);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const field = (label: string, key: keyof Settings, type = "text", hint?: string) => (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      {hint && <p className="text-xs text-gray-400 mb-2">{hint}</p>}
      <input
        type={type}
        value={form[key]}
        onChange={(e) => setForm((f) => ({ ...f, [key]: type === "number" ? Number(e.target.value) : e.target.value }))}
        className="w-full border border-gray-200 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
    </div>
  );

  return (
    <div className="space-y-6 max-w-2xl">
      <h1 className="text-xl font-bold text-gray-900">Configurações</h1>

      <form onSubmit={save} className="bg-white rounded-lg border border-gray-200 p-6 space-y-5">
        {field("Threshold de alerta DLQ", "dlq_alert_threshold", "number", "Alerta quando DLQ atingir este número de mensagens")}
        {field("Timeout de sessão padrão (min)", "default_session_timeout", "number", "Tempo em minutos antes de uma sessão inativa expirar")}
        {field("E-mail de notificação", "notification_email", "email")}
        {field("Slack Webhook URL", "slack_webhook_url", "url", "URL do webhook para alertas no Slack")}

        <div className="pt-2 flex items-center gap-3">
          <button
            type="submit"
            disabled={saving}
            className="px-5 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? "Salvando..." : "Salvar"}
          </button>
          {saved && <span className="text-sm text-green-600">✓ Salvo com sucesso</span>}
        </div>
      </form>
    </div>
  );
}
