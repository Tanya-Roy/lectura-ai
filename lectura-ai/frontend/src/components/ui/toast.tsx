import * as React from "react";
import { CheckCircle2, AlertCircle, Info, X } from "lucide-react";
import { cn } from "../../lib/utils";

interface ToastProps {
  id: string;
  type?: "success" | "error" | "info";
  title?: string;
  message: string;
  onDismiss: (id: string) => void;
}

export const Toast: React.FC<ToastProps> = ({
  id,
  type = "info",
  title,
  message,
  onDismiss,
}) => {
  return (
    <div
      className={cn(
        "pointer-events-auto flex w-full max-w-sm items-start gap-3 rounded-xl p-4 shadow-lg ring-1 transition-all duration-300",
        type === "success" && "bg-white text-slate-900 ring-emerald-200 border-l-4 border-emerald-500",
        type === "error" && "bg-white text-slate-900 ring-red-200 border-l-4 border-red-500",
        type === "info" && "bg-white text-slate-900 ring-primary-200 border-l-4 border-primary-500"
      )}
    >
      {type === "success" && <CheckCircle2 className="h-5 w-5 text-emerald-500 shrink-0 mt-0.5" />}
      {type === "error" && <AlertCircle className="h-5 w-5 text-red-500 shrink-0 mt-0.5" />}
      {type === "info" && <Info className="h-5 w-5 text-primary-600 shrink-0 mt-0.5" />}

      <div className="flex-1 text-sm">
        {title && <h5 className="font-semibold text-slate-900">{title}</h5>}
        <p className="text-slate-600 text-xs mt-0.5 leading-relaxed">{message}</p>
      </div>

      <button
        onClick={() => onDismiss(id)}
        className="text-slate-400 hover:text-slate-600 transition-colors"
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  );
};
