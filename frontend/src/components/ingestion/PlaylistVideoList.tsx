import React from "react";
import { Film, CheckCircle2, Loader2, AlertCircle, Clock } from "lucide-react";
import { Badge } from "../ui/badge";
import { PlaylistVideoItem } from "../../types";

interface PlaylistVideoListProps {
  videos: PlaylistVideoItem[];
  processingStatuses?: Record<string, string>; // video_id -> "pending" | "in_progress" | "completed" | "failed"
  onSelectVideo?: (videoId: string) => void;
  selectedVideoId?: string;
  className?: string;
}

export const PlaylistVideoList: React.FC<PlaylistVideoListProps> = ({
  videos,
  processingStatuses = {},
  onSelectVideo,
  selectedVideoId,
  className = "",
}) => {
  if (!videos || videos.length === 0) {
    return (
      <div className="p-8 text-center text-slate-400 text-xs border border-dashed border-slate-200 rounded-lg">
        No playlist lectures detected.
      </div>
    );
  }

  const getStatusBadge = (videoId: string) => {
    const status = processingStatuses[videoId];
    if (status === "completed") {
      return (
        <Badge variant="outline" className="text-emerald-600 border-emerald-200 bg-emerald-50 text-[10px] gap-1 py-0 h-5">
          <CheckCircle2 className="h-3 w-3" /> Ready
        </Badge>
      );
    }
    if (status === "in_progress") {
      return (
        <Badge variant="outline" className="text-indigo-600 border-indigo-200 bg-indigo-50 text-[10px] gap-1 py-0 h-5 animate-pulse">
          <Loader2 className="h-3 w-3 animate-spin" /> Ingesting
        </Badge>
      );
    }
    if (status === "failed") {
      return (
        <Badge variant="outline" className="text-red-600 border-red-200 bg-red-50 text-[10px] gap-1 py-0 h-5">
          <AlertCircle className="h-3 w-3" /> Failed
        </Badge>
      );
    }
    return (
      <Badge variant="outline" className="text-slate-400 border-slate-200 text-[10px] py-0 h-5">
        Queued
      </Badge>
    );
  };

  return (
    <div className={`space-y-2 max-h-96 overflow-y-auto pr-1 ${className}`}>
      {videos.map((vid, index) => {
        const isSelected = selectedVideoId === vid.video_id;
        return (
          <div
            key={vid.video_id || index}
            onClick={() => onSelectVideo?.(vid.video_id)}
            className={`flex items-center gap-3 p-2.5 rounded-lg border transition-all text-left ${
              onSelectVideo ? "cursor-pointer" : ""
            } ${
              isSelected
                ? "border-indigo-500 bg-indigo-50/40 shadow-sm"
                : "border-slate-100 hover:border-slate-200 hover:bg-slate-50/80 bg-white"
            }`}
          >
            {/* Position badge */}
            <div className="w-6 text-center font-mono font-bold text-xs text-slate-400 shrink-0">
              #{index + 1}
            </div>

            {/* Thumbnail */}
            <div className="relative w-20 h-12 rounded bg-slate-900 overflow-hidden shrink-0">
              <img
                src={vid.thumbnail_url || `https://img.youtube.com/vi/${vid.video_id}/default.jpg`}
                alt={vid.title}
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-black/10 flex items-center justify-center">
                <Film className="h-3.5 w-3.5 text-white/80" />
              </div>
            </div>

            {/* Details */}
            <div className="flex-1 min-w-0">
              <h5 className="font-medium text-xs text-slate-800 truncate leading-snug">
                {vid.title}
              </h5>
              {vid.channel_name && (
                <p className="text-[11px] text-slate-400 truncate mt-0.5">
                  {vid.channel_name}
                </p>
              )}
            </div>

            {/* Status */}
            <div className="shrink-0">{getStatusBadge(vid.video_id)}</div>
          </div>
        );
      })}
    </div>
  );
};
