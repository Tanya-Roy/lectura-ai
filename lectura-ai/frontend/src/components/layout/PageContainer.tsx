import React from "react";
import { cn } from "../../lib/utils";

interface PageContainerProps {
  title?: string;
  subtitle?: string;
  action?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}

export const PageContainer: React.FC<PageContainerProps> = ({
  title,
  subtitle,
  action,
  children,
  className,
}) => {
  return (
    <div className={cn("max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8", className)}>
      {(title || subtitle || action) && (
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-200">
          <div>
            {title && <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">{title}</h1>}
            {subtitle && <p className="text-sm text-slate-500 mt-1">{subtitle}</p>}
          </div>
          {action && <div className="flex items-center gap-3 shrink-0">{action}</div>}
        </div>
      )}
      {children}
    </div>
  );
};
