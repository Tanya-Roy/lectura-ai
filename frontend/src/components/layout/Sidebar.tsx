import React from "react";
import { Link, useLocation } from "react-router-dom";
import {
  GraduationCap,
  LayoutDashboard,
  PlusCircle,
  BookOpen,
  FileText,
  Layers,
  HelpCircle,
  MessageSquare,
  BarChart3,
  Sparkles,
  ChevronRight,
} from "lucide-react";
import { cn } from "../../lib/utils";
import { Badge } from "../ui/badge";

interface NavItem {
  label: string;
  path: string;
  icon: React.ElementType;
  badge?: string;
}

const navItems: NavItem[] = [
  { label: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
  { label: "Import Lecture", path: "/import", icon: PlusCircle, badge: "New" },
  { label: "My Courses", path: "/courses", icon: BookOpen },
  { label: "Study Notes", path: "/notes", icon: FileText },
  { label: "Flashcards", path: "/flashcards", icon: Layers },
  { label: "Quizzes", path: "/quizzes", icon: HelpCircle },
  { label: "AI Study Chat", path: "/chat", icon: MessageSquare },
  { label: "Analytics", path: "/analytics", icon: BarChart3 },
];

export const Sidebar: React.FC = () => {
  const location = useLocation();

  return (
    <aside className="w-64 bg-white border-r border-slate-200 flex flex-col shrink-0 h-screen sticky top-0">
      {/* Brand Logo */}
      <div className="h-16 flex items-center gap-3 px-6 border-b border-slate-100">
        <div className="h-9 w-9 rounded-xl bg-primary-700 flex items-center justify-center text-white shadow-md shadow-primary-700/20">
          <GraduationCap className="h-5 w-5" />
        </div>
        <div>
          <div className="flex items-center gap-1.5">
            <span className="font-bold text-lg text-slate-900 tracking-tight">Lectura</span>
            <span className="text-xs font-bold text-primary-700 bg-primary-50 px-1.5 py-0.5 rounded">AI</span>
          </div>
          <p className="text-[10px] text-slate-400 font-medium">Academic Synthesis</p>
        </div>
      </div>

      {/* Navigation Links */}
      <div className="flex-1 py-6 px-4 space-y-1.5 overflow-y-auto">
        <div className="px-3 pb-2 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
          Core Workspace
        </div>

        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive =
            location.pathname === item.path ||
            (item.path !== "/" && location.pathname.startsWith(`${item.path}/`));

          return (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                "flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all group",
                isActive
                  ? "bg-primary-50 text-primary-800 font-semibold shadow-sm"
                  : "text-slate-600 hover:bg-slate-100/80 hover:text-slate-900"
              )}
            >
              <div className="flex items-center gap-3">
                <Icon
                  className={cn(
                    "h-4 w-4 transition-colors",
                    isActive ? "text-primary-700" : "text-slate-400 group-hover:text-slate-600"
                  )}
                />
                <span>{item.label}</span>
              </div>
              {item.badge ? (
                <Badge variant="default" className="text-[10px] py-0 px-1.5 h-4 bg-primary-600 text-white">
                  {item.badge}
                </Badge>
              ) : isActive ? (
                <ChevronRight className="h-3.5 w-3.5 text-primary-600" />
              ) : null}
            </Link>
          );
        })}
      </div>

      {/* AI Pro Banner */}
      <div className="p-4 border-t border-slate-100">
        <div className="rounded-xl bg-gradient-to-br from-primary-900 to-primary-700 p-4 text-white shadow-sm">
          <div className="flex items-center gap-2 mb-1.5">
            <Sparkles className="h-4 w-4 text-amber-300" />
            <span className="text-xs font-bold uppercase tracking-wider text-amber-200">Fact-Checking Agent</span>
          </div>
          <p className="text-xs text-primary-100 leading-relaxed mb-3">
            Multi-stage verification enabled. Rigor scoring active.
          </p>
          <div className="h-1.5 w-full bg-primary-950/40 rounded-full overflow-hidden">
            <div className="h-full bg-emerald-400 w-[98%]" />
          </div>
          <p className="text-[10px] text-primary-200 mt-1.5 flex justify-between">
            <span>Audit Reliability</span>
            <span className="font-semibold text-white">98% Strict</span>
          </p>
        </div>
      </div>
    </aside>
  );
};
