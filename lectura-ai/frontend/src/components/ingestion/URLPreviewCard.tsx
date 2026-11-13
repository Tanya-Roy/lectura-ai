import React, { useEffect } from "react";
import {
  Youtube,
  Layers,
  Clock,
  User,
  AlertCircle,
  CheckCircle2,
  ExternalLink,
  Film,
} from "lucide-react";
import { Card, CardContent } from "../ui/card";
import { Badge } from "../ui/badge";
import { useURLPreview } from "../../hooks/useURLPreview";
import { PlaylistMetadata, URLPreviewResponse, VideoMetadata } from "../../types";

interface URLPreviewCardProps {
  url: string;
  onValidated?: (result: URLPreviewResponse) => void;
  className?: string;
}

function formatDuration(seconds: number): string {
  if (!seconds || seconds <= 0) return "0:00";
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  if (mins >= 60) {
    const hours = Math.floor(mins / 60);
    const remMins = mins % 60;
    return `${hours}h ${remMins}m`;
  }
  return `${mins}:${secs < 10 ? "0" : ""}${secs}`;
}

export const URLPreviewCard: React.FC<URLPreviewCardProps> = ({
  url,
  onValidated,
  className = "",
}) => {
  const { preview, isLoading, error } = useURLPreview(url, 700);

  useEffect(() => {
    if (preview && onValidated) {
      onValidated(preview);
    }
  }, [preview, onValidated]);

  if (!url.trim()) {
    return null;
  }

  // Loading skeleton state
  if (isLoading) {
    return (
      <Card className={`border border-slate-200 bg-slate-50/50 animate-pulse ${className}`}>
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row gap-4 items-start">
            <div className="w-full sm:w-44 h-28 bg-slate-200 rounded-lg shrink-0" />
            <div className="flex-1 space-y-2.5 w-full">
              <div className="h-4 bg-slate-200 rounded w-3/4" />
              <div className="h-3 bg-slate-200 rounded w-1/2" />
              <div className="h-3 bg-slate-200 rounded w-1/4 mt-4" />
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Error state
  if (error || (preview && !preview.valid)) {
    return (
      <Card className={`border border-red-200 bg-red-50/40 text-red-900 ${className}`}>
        <CardContent className="p-4 flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-red-500 shrink-0 mt-0.5" />
          <div className="space-y-1 text-sm">
            <p className="font-semibold text-red-800">Invalid YouTube Link</p>
            <p className="text-red-700 text-xs">
              {error || preview?.error || "We could not find this video. Check the URL and try again."}
            </p>
            <p className="text-xs text-red-600/80 mt-1">
              Accepted formats: <code className="bg-red-100/80 px-1 py-0.5 rounded">youtube.com/watch?v=...</code>,{" "}
              <code className="bg-red-100/80 px-1 py-0.5 rounded">youtu.be/...</code>, or{" "}
              <code className="bg-red-100/80 px-1 py-0.5 rounded">youtube.com/playlist?list=...</code>
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!preview || !preview.metadata) {
    return null;
  }

  const isPlaylist = preview.url_type === "playlist";

  // Playlist Preview Card
  if (isPlaylist) {
    const plMeta = preview.metadata as PlaylistMetadata;
    const previewVideos = plMeta.videos || [];

    return (
      <Card className={`border border-slate-200 shadow-sm bg-white overflow-hidden ${className}`}>
        <CardContent className="p-4 space-y-3">
          <div className="flex flex-col sm:flex-row gap-4 items-start">
            <div className="relative w-full sm:w-48 h-32 bg-slate-900 rounded-lg overflow-hidden shrink-0 group">
              <img
                src={plMeta.thumbnail_url || "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400"}
                alt={plMeta.title}
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
              />
              <div className="absolute inset-0 bg-black/30 flex items-center justify-center">
                <Layers className="h-8 w-8 text-white/90 drop-shadow" />
              </div>
              <div className="absolute bottom-2 right-2 bg-black/80 backdrop-blur-sm text-white text-[11px] font-medium px-2 py-0.5 rounded flex items-center gap-1">
                <Film className="h-3 w-3" />
                <span>{plMeta.video_count || previewVideos.length} lectures</span>
              </div>
            </div>

            <div className="flex-1 space-y-1.5 min-w-0">
              <div className="flex items-center gap-2">
                <Badge variant="outline" className="text-indigo-600 border-indigo-200 bg-indigo-50/50 gap-1 text-[11px]">
                  <Layers className="h-3 w-3" /> Course Playlist
                </Badge>
                <Badge variant="outline" className="text-emerald-600 border-emerald-200 bg-emerald-50/50 gap-1 text-[11px]">
                  <CheckCircle2 className="h-3 w-3" /> Verified Link
                </Badge>
              </div>

              <h4 className="font-semibold text-slate-900 text-base leading-snug line-clamp-2">
                {plMeta.title}
              </h4>

              <div className="flex items-center gap-2 text-xs text-slate-500">
                <User className="h-3.5 w-3.5" />
                <span>{plMeta.channel_name || "Course Instructor"}</span>
              </div>

              {plMeta.description && (
                <p className="text-xs text-slate-600 line-clamp-2 pt-1">
                  {plMeta.description}
                </p>
              )}
            </div>
          </div>

          {/* Mini video thumbnails row */}
          {previewVideos.length > 0 && (
            <div className="pt-2 border-t border-slate-100">
              <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-2">
                Included Lectures ({previewVideos.length} shown)
              </p>
              <div className="flex gap-2 overflow-x-auto pb-1">
                {previewVideos.slice(0, 5).map((vid, idx) => (
                  <div
                    key={vid.video_id || idx}
                    className="w-24 shrink-0 rounded border border-slate-100 overflow-hidden bg-slate-50 text-[10px]"
                    title={vid.title}
                  >
                    <img
                      src={vid.thumbnail_url}
                      alt={vid.title}
                      className="w-full h-14 object-cover"
                    />
                    <div className="p-1 truncate font-medium text-slate-700">
                      #{idx + 1} {vid.title}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    );
  }

  // Single Video Preview Card
  const vMeta = preview.metadata as VideoMetadata;

  return (
    <Card className={`border border-slate-200 shadow-sm bg-white overflow-hidden ${className}`}>
      <CardContent className="p-4">
        <div className="flex flex-col sm:flex-row gap-4 items-start">
          <div className="relative w-full sm:w-48 h-28 bg-slate-900 rounded-lg overflow-hidden shrink-0 group">
            <img
              src={vMeta.thumbnail_url}
              alt={vMeta.title}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            />
            <div className="absolute inset-0 bg-black/20 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
              <Youtube className="h-8 w-8 text-red-500 drop-shadow" />
            </div>
            {vMeta.duration_seconds > 0 && (
              <div className="absolute bottom-1.5 right-1.5 bg-black/80 backdrop-blur-sm text-white text-[11px] font-medium px-1.5 py-0.5 rounded flex items-center gap-1">
                <Clock className="h-3 w-3" />
                <span>{formatDuration(vMeta.duration_seconds)}</span>
              </div>
            )}
          </div>

          <div className="flex-1 space-y-1.5 min-w-0">
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="text-red-600 border-red-200 bg-red-50/50 gap-1 text-[11px]">
                <Youtube className="h-3 w-3" /> YouTube Lecture
              </Badge>
              <Badge variant="outline" className="text-emerald-600 border-emerald-200 bg-emerald-50/50 gap-1 text-[11px]">
                <CheckCircle2 className="h-3 w-3" /> Verified Link
              </Badge>
            </div>

            <h4 className="font-semibold text-slate-900 text-base leading-snug line-clamp-2">
              {vMeta.title}
            </h4>

            <div className="flex items-center gap-2 text-xs text-slate-500">
              <User className="h-3.5 w-3.5" />
              <span>{vMeta.channel_name || "Academic Channel"}</span>
            </div>

            {vMeta.description && (
              <p className="text-xs text-slate-600 line-clamp-2 pt-1">
                {vMeta.description}
              </p>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
