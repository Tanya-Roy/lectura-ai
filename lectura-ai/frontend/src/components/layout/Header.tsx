import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { Plus, Search, Bell, Sparkles, BookOpen } from "lucide-react";
import { Button } from "../ui/button";
import { Avatar, AvatarFallback } from "../ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "../ui/dropdown-menu";
import { useStore } from "../../store/useStore";

export const Header: React.FC = () => {
  const { currentUser } = useStore();
  const navigate = useNavigate();

  return (
    <header className="h-16 bg-white/80 backdrop-blur-md border-b border-slate-200 sticky top-0 z-40 px-6 flex items-center justify-between">
      {/* Quick Search Bar / Filter Input */}
      <div className="flex items-center gap-3 w-full max-w-md">
        <div className="relative w-full">
          <Search className="h-4 w-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search concepts, lectures, formulas, or notes..."
            className="w-full pl-9 pr-4 py-1.5 text-xs bg-slate-100 hover:bg-slate-200/70 focus:bg-white text-slate-900 border border-transparent focus:border-primary-400 rounded-lg outline-none transition-all placeholder:text-slate-400"
          />
        </div>
      </div>

      {/* Action Controls */}
      <div className="flex items-center gap-3">
        <Link to="/import">
          <Button size="sm" className="gap-1.5 shadow-sm">
            <Plus className="h-4 w-4" />
            <span>Import YouTube</span>
          </Button>
        </Link>

        <div className="h-4 w-px bg-slate-200 mx-1" />

        {/* User Account Menu */}
        <DropdownMenu>
          <DropdownMenuTrigger className="outline-none">
            <div className="flex items-center gap-2.5 p-1 rounded-full hover:bg-slate-100 transition-colors">
              <Avatar className="h-8 w-8">
                <AvatarFallback>AA</AvatarFallback>
              </Avatar>
              <div className="text-left hidden md:block">
                <p className="text-xs font-semibold text-slate-800 leading-tight">
                  {currentUser?.full_name || "Alex Academic"}
                </p>
                <p className="text-[10px] text-slate-400">Student Scholar</p>
              </div>
            </div>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56">
            <DropdownMenuLabel>My Account</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={() => navigate("/dashboard")}>
              <BookOpen className="h-4 w-4 mr-2 text-slate-500" />
              <span>Dashboard</span>
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => navigate("/analytics")}>
              <Sparkles className="h-4 w-4 mr-2 text-slate-500" />
              <span>Study Analytics</span>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={() => navigate("/")}>
              <span>Landing Page</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
};
