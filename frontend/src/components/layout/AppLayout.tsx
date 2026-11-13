import React from "react";
import { Outlet, Link } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { Header } from "./Header";
import { useStore } from "../../store/useStore";
import { Loader2, ArrowRight } from "lucide-react";

export const AppLayout: React.FC = () => {
  const { activeJob } = useStore();

  return (
    <div className="flex min-h-screen bg-slate-50">
      {/* Sidebar Navigation */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header />

        {/* Global Active Processing Banner if job in progress */}
        {activeJob && activeJob.status === "in_progress" && (
          <div className="bg-primary-900 text-white px-6 py-2.5 flex items-center justify-between text-xs animate-in fade-in">
            <div className="flex items-center gap-3">
              <Loader2 className="h-4 w-4 animate-spin text-amber-300" />
              <span>
                <strong>Lectura Agent Pipeline Active:</strong> Step{" "}
                <code className="bg-primary-800 px-1.5 py-0.5 rounded text-amber-200">
                  {activeJob.current_node || "processing"}
                </code>{" "}
                ({activeJob.progress_percentage}% completed)
              </span>
            </div>
            <Link
              to="/import"
              className="flex items-center gap-1 font-semibold text-amber-300 hover:text-white transition-colors"
            >
              <span>View Live Logs</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>
        )}

        {/* Page Content Outlet */}
        <main className="flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
