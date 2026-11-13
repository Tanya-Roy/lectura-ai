import React, { useState, useEffect, useMemo } from "react";
import {
  FileText,
  Clock,
  Search,
  Copy,
  Check,
  AlertTriangle,
  Sparkles,
  Download,
  BookOpen,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../ui/card";
import { Badge } from "../ui/badge";
import { Input } from "../ui/input";
import { Button } from "../ui/button";
import { getVideoTranscript } from "../../services/api";
import { Transcript, TranscriptChunk } from "../../types";

interface TranscriptViewerProps {
  videoId: string;
  videoTitle?: string;
  initialChunks?: TranscriptChunk[];
  className?: string;
}

function formatTimestamp(seconds: number): string {
  if (!seconds || seconds < 0) return "0:00";
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs < 10 ? "0" : ""}${secs}`;
}

export const TranscriptViewer: React.FC<TranscriptViewerProps> = ({
  videoId,
  videoTitle,
  initialChunks,
  className = "",
}) => {
  const [transcript, setTranscript] = useState<Transcript | null>(null);
  const [loading, setLoading] = useState<boolean>(!initialChunks);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [copied, setCopied] = useState<boolean>(false);

  useEffect(() => {
    if (initialChunks && initialChunks.length > 0) {
      setTranscript({
        id: `trn_${videoId}`,
        video_id: videoId,
        language: "en",
        is_generated: false,
        raw_text: initialChunks.map((c) => c.text).join(" "),
        chunks: initialChunks,
      });
      setLoading(false);
      return;
    }

    if (!videoId) return;

    let isMounted = true;
    setLoading(true);
    setError(null);

    getVideoTranscript(videoId)
      .then((data) => {
        if (!isMounted) return;
        setTranscript(data);
      })
      .catch((err: any) => {
        if (!isMounted) return;
        const msg = err.response?.data?.detail || err.message || "Failed to load transcript.";
        setError(msg);
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [videoId, initialChunks]);

  const chunks = transcript?.chunks || [];

  // Filter chunks matching search query
  const filteredChunks = useMemo(() => {
    if (!searchQuery.trim()) return chunks;
    const q = searchQuery.toLowerCase();
    return chunks.filter(
      (c) =>
        c.text.toLowerCase().includes(q) ||
        (c.topic_hint && c.topic_hint.toLowerCase().includes(q))
    );
  }, [chunks, searchQuery]);

  const handleCopyAll = () => {
    if (!transcript) return;
    const fullText = chunks
      .map(
        (c) =>
          `[${formatTimestamp(c.start_time)} - ${formatTimestamp(c.end_time)}] ${
            c.topic_hint ? `[${c.topic_hint}] ` : ""
          }${c.text}`
      )
      .join("\n\n");
    navigator.clipboard.writeText(fullText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadTxt = () => {
    if (!transcript) return;
    const fullText = chunks
      .map(
        (c) =>
          `[${formatTimestamp(c.start_time)} - ${formatTimestamp(c.end_time)}] ${c.text}`
      )
      .join("\n\n");
    const blob = new Blob([fullText], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `transcript-${videoId}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <Card className={`border border-slate-200 bg-white ${className}`}>
        <CardContent className="p-8 space-y-4">
          <div className="flex items-center gap-3">
            <div className="h-5 w-5 bg-indigo-200 rounded animate-pulse" />
            <div className="h-5 bg-slate-200 rounded w-1/3 animate-pulse" />
          </div>
          <div className="space-y-3 pt-4">
            {[1, 2, 3].map((n) => (
              <div key={n} className="p-4 rounded-lg border border-slate-100 bg-slate-50 space-y-2 animate-pulse">
                <div className="h-4 bg-slate-200 rounded w-24" />
                <div className="h-3 bg-slate-200 rounded w-full" />
                <div className="h-3 bg-slate-200 rounded w-4/5" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={`border border-amber-200 bg-amber-50/50 ${className}`}>
        <CardContent className="p-6 text-center space-y-2">
          <AlertTriangle className="h-8 w-8 text-amber-500 mx-auto" />
          <h4 className="font-semibold text-amber-900 text-sm">Transcript Unavailable</h4>
          <p className="text-xs text-amber-700 max-w-md mx-auto">{error}</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={`border border-slate-200 bg-white shadow-sm overflow-hidden ${className}`}>
      <CardHeader className="p-5 border-b border-slate-100 bg-slate-50/50">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-indigo-600" />
              <CardTitle className="text-base font-bold text-slate-900">
                Extracted Lecture Transcript
              </CardTitle>
            </div>
            {videoTitle && (
              <CardDescription className="text-xs text-slate-500 mt-1 line-clamp-1">
                {videoTitle}
              </CardDescription>
            )}
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            <Badge variant="outline" className="text-slate-600 border-slate-200 text-xs">
              Language: {transcript?.language?.toUpperCase() || "EN"}
            </Badge>
            {transcript?.is_generated ? (
              <Badge variant="outline" className="text-amber-600 border-amber-200 bg-amber-50/50 text-xs">
                Auto-generated
              </Badge>
            ) : (
              <Badge variant="outline" className="text-emerald-600 border-emerald-200 bg-emerald-50/50 text-xs">
                Official Captions
              </Badge>
            )}
            <Badge variant="secondary" className="text-xs bg-indigo-50 text-indigo-700 border-indigo-100">
              {chunks.length} Topic Chunks
            </Badge>
          </div>
        </div>

        {/* Search bar and actions */}
        <div className="flex flex-col sm:flex-row gap-2 pt-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
            <Input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search transcript phrases, equations, or concepts..."
              className="pl-9 h-9 text-xs"
            />
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleCopyAll}
              className="h-9 text-xs gap-1.5"
            >
              {copied ? <Check className="h-3.5 w-3.5 text-emerald-600" /> : <Copy className="h-3.5 w-3.5" />}
              {copied ? "Copied" : "Copy"}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleDownloadTxt}
              className="h-9 text-xs gap-1.5"
            >
              <Download className="h-3.5 w-3.5" />
              Export
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="p-4 max-h-[500px] overflow-y-auto space-y-3">
        {transcript?.is_generated && (
          <div className="p-2.5 rounded-lg border border-amber-200/60 bg-amber-50/40 text-amber-800 text-xs flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-amber-600 shrink-0" />
            <span>
              Auto-generated transcript detected. Minor phonetic ambiguities will be normalized by the Phase 3 Agent Verifier.
            </span>
          </div>
        )}

        {filteredChunks.length === 0 ? (
          <div className="text-center py-12 text-slate-400 text-xs">
            {searchQuery ? `No transcript chunks matched "${searchQuery}"` : "No transcript chunks available."}
          </div>
        ) : (
          filteredChunks.map((chunk, idx) => {
            const hasTopic = Boolean(chunk.topic_hint);
            return (
              <div
                key={chunk.id || chunk.chunk_id || idx}
                className="group p-3.5 rounded-lg border border-slate-100 hover:border-slate-200 bg-white hover:bg-slate-50/50 transition-all space-y-1.5"
              >
                <div className="flex items-center justify-between gap-2 flex-wrap text-xs">
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-semibold text-indigo-600 bg-indigo-50/80 px-2 py-0.5 rounded text-[11px] flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {formatTimestamp(chunk.start_time)} – {formatTimestamp(chunk.end_time)}
                    </span>
                    {hasTopic && (
                      <span className="font-medium text-slate-800 flex items-center gap-1 text-xs">
                        <Sparkles className="h-3 w-3 text-amber-500" />
                        {chunk.topic_hint}
                      </span>
                    )}
                  </div>
                  {chunk.word_count ? (
                    <span className="text-[11px] text-slate-400">
                      {chunk.word_count} words
                    </span>
                  ) : null}
                </div>

                <p className="text-xs text-slate-700 leading-relaxed font-sans">
                  {chunk.text}
                </p>
              </div>
            );
          })
        )}
      </CardContent>
    </Card>
  );
};
