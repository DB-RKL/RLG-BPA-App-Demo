import { useState, useEffect } from "react";
import { Routes, Route, Navigate, useNavigate } from "react-router-dom";
import Icon from "./components/Icon";
import Sidebar from "./components/Sidebar";
import ToastHost from "./components/ToastHost";
import DashboardHome from "./pages/DashboardHome";
import CustomersPage from "./pages/CustomersPage";
import CustomerDetailPage from "./pages/CustomerDetailPage";
import ReviewPage from "./pages/ReviewPage";
import DashboardPage from "./pages/DashboardPage";
import GeniePage from "./pages/GeniePage";
import { useDocumentStore } from "./stores/documentStore";

function getGreeting(): string {
  const h = new Date().getHours();
  if (h < 12) return "Good morning";
  if (h < 18) return "Good afternoon";
  return "Good evening";
}

export default function App() {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const { documents, volumeFiles, fetchDocuments, fetchVolumeFiles } = useDocumentStore();

  useEffect(() => {
    fetchDocuments();
    fetchVolumeFiles();
  }, []);

  const processedNames = new Set(documents.map((d) => d.filename));
  const inboxCount = volumeFiles.filter((f) => !processedNames.has(f.name)).length;
  const reviewCount = documents.filter((d) => d.status === "review").length;

  return (
    <div className="min-h-screen bg-surface text-on-surface font-body antialiased">
      <Sidebar
        collapsed={collapsed}
        onToggle={() => setCollapsed(!collapsed)}
        inboxCount={inboxCount}
        reviewCount={reviewCount}
      />

      <div
        className={`transition-all duration-300 ease-in-out ${
          collapsed ? "ml-[68px]" : "ml-64"
        }`}
      >
        {/* Top utility bar */}
        <header
          className="w-full h-14 sticky top-0 z-40 flex justify-end items-center px-8 gap-3 border-b border-surface-container-high/60"
          style={{ backgroundColor: "rgba(249, 249, 249, 0.85)", backdropFilter: "blur(20px)" }}
        >
          <div className="flex items-center gap-4 mr-auto">
            <span className="font-headline text-sm text-on-surface">
              {getGreeting()},{" "}
              <span className="font-medium text-primary">Ruby</span>
            </span>
            <div className="relative hidden lg:block">
              <Icon name="search" className="absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant/40" size={16} />
              <input
                className="w-56 bg-surface-container-high/50 hover:bg-surface-container-high focus:bg-white border border-outline-variant/20 focus:border-outline-variant/40 rounded-lg focus:ring-0 pl-9 pr-3 py-1.5 text-xs font-label transition-all placeholder:text-on-surface-variant/40"
                placeholder="Search documents..."
                type="text"
              />
            </div>
          </div>
          <button className="relative p-1.5 text-on-surface-variant/60 hover:text-on-surface transition-colors rounded-lg hover:bg-surface-container-high/60">
            <Icon name="notifications" size={18} />
            {(inboxCount > 0 || reviewCount > 0) && (
              <span className="absolute top-0.5 right-0.5 w-2 h-2 bg-error rounded-full" />
            )}
          </button>
          <button className="p-1.5 text-on-surface-variant/60 hover:text-on-surface transition-colors rounded-lg hover:bg-surface-container-high/60">
            <Icon name="help_outline" size={18} />
          </button>
          <div className="w-px h-5 bg-outline-variant/30 mx-1" />
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-full flex items-center justify-center text-white text-[10px] font-bold font-label" style={{ backgroundColor: "#450350" }}>
              RL
            </div>
          </div>
        </header>

        <main className="p-8 lg:p-12">
          <Routes>
            <Route path="/" element={<DashboardHome />} />
            <Route path="/customers" element={<CustomersPage />} />
            <Route path="/customers/:slug" element={<CustomerDetailPage />} />
            <Route path="/inbox" element={<Navigate to="/customers" replace />} />
            <Route path="/review" element={<ReviewPage />} />
            <Route path="/review/:id" element={<ReviewPage />} />
            <Route path="/insights" element={<DashboardPage />} />
            <Route path="/genie" element={<GeniePage />} />
          </Routes>
        </main>
      </div>
      <ToastHost />
    </div>
  );
}
