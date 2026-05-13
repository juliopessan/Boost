import { BrowserRouter, NavLink, Route, Routes } from "react-router-dom";
import { DashboardPage } from "./pages/Dashboard";
import { DLQPage } from "./pages/DLQ";
import { FlowsPage } from "./pages/Flows";
import { MessagesPage } from "./pages/Messages";
import { SettingsPage } from "./pages/Settings";

const nav = [
  { to: "/", label: "Dashboard", icon: "📊" },
  { to: "/flows", label: "Flows", icon: "⚡" },
  { to: "/messages", label: "Mensagens", icon: "💬" },
  { to: "/dlq", label: "DLQ", icon: "☠️" },
  { to: "/settings", label: "Config", icon: "⚙️" },
];

function Sidebar() {
  return (
    <aside className="w-56 bg-[#1a1a2e] min-h-screen flex flex-col">
      <div className="px-6 py-5 border-b border-white/10">
        <span className="text-white font-bold text-lg tracking-tight">⚡ Boost</span>
        <p className="text-white/40 text-xs mt-0.5">FlowCore Dashboard</p>
      </div>
      <nav className="flex-1 px-3 py-4 space-y-1">
        {nav.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
                isActive
                  ? "bg-white/10 text-white font-medium"
                  : "text-white/60 hover:text-white hover:bg-white/5"
              }`
            }
          >
            <span>{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex min-h-screen bg-gray-50 font-sans">
        <Sidebar />
        <main className="flex-1 px-8 py-8 overflow-auto">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/flows" element={<FlowsPage />} />
            <Route path="/messages" element={<MessagesPage />} />
            <Route path="/dlq" element={<DLQPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
