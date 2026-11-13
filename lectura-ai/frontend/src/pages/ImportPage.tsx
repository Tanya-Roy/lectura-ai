import React, { useState, useEffect, useRef } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import {
  Youtube,
  Layers,
  Upload,
  Sparkles,
  CheckCircle2,
  Loader2,
  ArrowRight,
  Terminal,
  ShieldCheck,
  BookOpen,
  Clock,
  FileText,
  AlertCircle,
  HelpCircle,
  Check,
} from "lucide-react";
import { PageContainer } from "../components/layout/PageContainer";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "../components/ui/tabs";
import { Progress } from "../components/ui/progress";
import { Badge } from "../components/ui/badge";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "../components/ui/tooltip";
import { URLPreviewCard } from "../components/ingestion/URLPreviewCard";
import { PlaylistVideoList } from "../components/ingestion/PlaylistVideoList";
import { TranscriptViewer } from "../components/ingestion/TranscriptViewer";
import { processVideo, processPlaylist, uploadTranscript } from "../services/api";
import { useJobPolling } from "../hooks/useJobPolling";
import { useStore } from "../store/useStore";
import {
  PlaylistMetadata,
  TranscriptUploadResponse,
  URLPreviewResponse,
  VideoMetadata,
} from "../types";

// Validation schema
const videoFormSchema = z.object({
  url: z
    .string()
    .min(1, "Please enter a YouTube video URL")
    .refine(
      (val) =>
        /(?:youtube\.com\/(?:watch\?v=|embed\/|shorts\/|live\/)|youtu\.be\/)[a-zA-Z0-9_-]{11}/i.test(
          val
        ),
      "Please enter a valid YouTube video URL"
    ),
  generateFlashcards: z.boolean().default(true),
  generateQuizzes: z.boolean().default(true),
  enableVerification: z.boolean().default(true),
});

type VideoFormData = z.infer<typeof videoFormSchema>;

export const ImportPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { setActiveJob } = useStore();

  const [activeTab, setActiveTab] = useState<string>("video");
  const [jobId, setJobId] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Single video form
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<VideoFormData>({
    resolver: zodResolver(videoFormSchema),
    defaultValues: {
      url: searchParams.get("url") || "",
      generateFlashcards: true,
      generateQuizzes: true,
      enableVerification: true,
    },
  });

  const videoUrlInput = watch("url");

  // Playlist tab state
  const [playlistUrl, setPlaylistUrl] = useState<string>("");
  const [playlistPreview, setPlaylistPreview] = useState<PlaylistMetadata | null>(null);
  const [playlistSubmitting, setPlaylistSubmitting] = useState<boolean>(false);

  // Upload tab state
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [associatedUrl, setAssociatedUrl] = useState<string>("");
  const [uploadSubmitting, setUploadSubmitting] = useState<boolean>(false);
  const [uploadResult, setUploadResult] = useState<TranscriptUploadResponse | null>(null);
  const [isDragOver, setIsDragOver] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  // Transcript viewer toggle
  const [showTranscriptViewer, setShowTranscriptViewer] = useState<boolean>(false);
  const [activeVideoId, setActiveVideoId] = useState<string | null>(null);
  const [activeVideoTitle, setActiveVideoTitle] = useState<string | null>(null);

  // Job Polling
  const { job, isPolling, isComplete, isFailed } = useJobPolling(jobId, 1500);

  // Auto-fill URL from query parameter
  useEffect(() => {
    const urlParam = searchParams.get("url");
    if (urlParam) {
      if (urlParam.includes("list=") && !urlParam.includes("watch?v=")) {
        setActiveTab("playlist");
        setPlaylistUrl(urlParam);
      } else {
        setValue("url", urlParam);
      }
    }
  }, [searchParams, setValue]);

  // Sync active job to Zustand store
  useEffect(() => {
    if (job) {
      setActiveJob(job);
      if (job.video_id) {
        setActiveVideoId(job.video_id);
      }
    }
  }, [job, setActiveJob]);

  // Auto show transcript viewer when job completes
  useEffect(() => {
    if (isComplete && job?.video_id) {
      setShowTranscriptViewer(true);
    }
  }, [isComplete, job]);

  // Single video submission
  const onSubmitVideo = async (data: VideoFormData) => {
    setSubmitting(true);
    setErrorMsg(null);
    setUploadResult(null);
    try {
      const response = await processVideo({
        url: data.url,
        generate_flashcards: data.generateFlashcards,
        generate_quizzes: data.generateQuizzes,
      });
      setJobId(response.job_id);
      setActiveJob(response);
      if (response.video_id) {
        setActiveVideoId(response.video_id);
      }
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || "Failed to initiate video processing.";
      setErrorMsg(msg);
    } finally {
      setSubmitting(false);
    }
  };

  // Playlist submission
  const onSubmitPlaylist = async () => {
    if (!playlistUrl.trim() || !playlistUrl.includes("list=")) {
      setErrorMsg("Please enter a valid YouTube playlist URL containing 'list='.");
      return;
    }
    setPlaylistSubmitting(true);
    setErrorMsg(null);
    try {
      const response = await processPlaylist({
        url: playlistUrl.trim(),
        max_videos: 50,
        generate_flashcards: true,
        generate_quizzes: true,
      });
      setJobId(response.job_id);
      setActiveJob(response);
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || "Failed to initiate playlist processing.";
      setErrorMsg(msg);
    } finally {
      setPlaylistSubmitting(false);
    }
  };

  // File upload handling
  const handleFileDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      const ext = file.name.split(".").pop()?.toLowerCase();
      if (["srt", "vtt", "txt"].includes(ext || "")) {
        setSelectedFile(file);
        setErrorMsg(null);
      } else {
        setErrorMsg("Please upload a .srt, .vtt, or .txt file.");
      }
    }
  };

  const handleUploadSubmit = async () => {
    if (!selectedFile) {
      setErrorMsg("Please choose a subtitle file to upload.");
      return;
    }
    setUploadSubmitting(true);
    setErrorMsg(null);
    try {
      const vidId = associatedUrl.match(/[a-zA-Z0-9_-]{11}/)?.[0] || `upl_${Date.now()}`;
      const result = await uploadTranscript(vidId, selectedFile);
      setUploadResult(result);
      setActiveVideoId(result.video_id);
      setActiveVideoTitle(selectedFile.name);
      setShowTranscriptViewer(true);
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || "Failed to process subtitle upload.";
      setErrorMsg(msg);
    } finally {
      setUploadSubmitting(false);
    }
  };

  // Callback from URLPreviewCard when video or playlist metadata is validated
  const handleVideoValidated = (result: URLPreviewResponse) => {
    if (result.valid && result.metadata) {
      setActiveVideoTitle((result.metadata as VideoMetadata).title || null);
      if (result.video_id) {
        setActiveVideoId(result.video_id);
      }
    }
  };

  const handlePlaylistValidated = (result: URLPreviewResponse) => {
    if (result.valid && result.url_type === "playlist" && result.metadata) {
      setPlaylistPreview(result.metadata as PlaylistMetadata);
    }
  };

  return (
    <PageContainer
      title="Lecture Ingestion Engine"
      subtitle="Extract rich metadata, subtitle transcripts, and semantic topic chunks from any YouTube lecture or course playlist."
    >
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Input Forms & Previews (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          <Card className="border-slate-200 shadow-sm bg-white">
            <CardHeader className="pb-4">
              <CardTitle className="text-lg font-bold text-slate-900">
                Choose Ingestion Source
              </CardTitle>
              <CardDescription className="text-xs text-slate-500">
                Process an individual lecture, an entire university course playlist, or upload custom subtitles.
              </CardDescription>
            </CardHeader>

            <CardContent>
              <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                <TabsList className="grid grid-cols-3 w-full mb-6 bg-slate-100 p-1 rounded-lg">
                  <TabsTrigger value="video" className="gap-2 text-xs font-semibold">
                    <Youtube className="h-4 w-4 text-red-500" /> Single Video
                  </TabsTrigger>
                  <TabsTrigger value="playlist" className="gap-2 text-xs font-semibold">
                    <Layers className="h-4 w-4 text-indigo-600" /> Course Playlist
                  </TabsTrigger>
                  <TabsTrigger value="upload" className="gap-2 text-xs font-semibold">
                    <Upload className="h-4 w-4 text-emerald-600" /> Upload File
                  </TabsTrigger>
                </TabsList>

                {/* Error Banner */}
                {errorMsg && (
                  <div className="mb-4 p-3 rounded-lg border border-red-200 bg-red-50 text-red-800 text-xs flex items-start gap-2.5">
                    <AlertCircle className="h-4 w-4 text-red-500 shrink-0 mt-0.5" />
                    <div className="flex-1 font-medium">{errorMsg}</div>
                  </div>
                )}

                {/* TAB 1: Single Video */}
                <TabsContent value="video" className="space-y-5 mt-0">
                  <form onSubmit={handleSubmit(onSubmitVideo)} className="space-y-5">
                    <div>
                      <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                        YouTube Video URL
                      </label>
                      <div className="relative">
                        <Youtube className="absolute left-3.5 top-1/2 -translate-y-1/2 h-5 w-5 text-red-500" />
                        <Input
                          placeholder="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
                          className="pl-11 h-11 text-sm bg-white"
                          {...register("url")}
                        />
                      </div>
                      {errors.url && (
                        <p className="text-xs text-red-600 mt-1.5 font-medium">
                          {errors.url.message}
                        </p>
                      )}
                    </div>

                    {/* Instant URL Preview Card */}
                    {videoUrlInput && (
                      <URLPreviewCard
                        url={videoUrlInput}
                        onValidated={handleVideoValidated}
                      />
                    )}

                    {/* Options Checklist */}
                    <div className="pt-3 border-t border-slate-100 space-y-3">
                      <span className="text-xs font-semibold text-slate-700 uppercase tracking-wider block">
                        Synthesis Capabilities
                      </span>

                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                        <label className="flex items-center gap-2 p-2.5 rounded-lg border border-slate-200 bg-slate-50/50 hover:bg-slate-50 cursor-pointer transition-colors">
                          <input
                            type="checkbox"
                            {...register("generateFlashcards")}
                            className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                          />
                          <span className="text-xs font-medium text-slate-700">
                            Spaced Flashcards
                          </span>
                        </label>

                        <label className="flex items-center gap-2 p-2.5 rounded-lg border border-slate-200 bg-slate-50/50 hover:bg-slate-50 cursor-pointer transition-colors">
                          <input
                            type="checkbox"
                            {...register("generateQuizzes")}
                            className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                          />
                          <span className="text-xs font-medium text-slate-700">
                            Self-Test Quizzes
                          </span>
                        </label>

                        <label className="flex items-center gap-2 p-2.5 rounded-lg border border-slate-200 bg-slate-50/50 hover:bg-slate-50 cursor-pointer transition-colors sm:col-span-2">
                          <input
                            type="checkbox"
                            {...register("enableVerification")}
                            className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                          />
                          <div className="flex items-center gap-1.5">
                            <span className="text-xs font-medium text-slate-700">
                              Agentic Verification (Phase 3)
                            </span>
                            <ShieldCheck className="h-3.5 w-3.5 text-emerald-600" />
                          </div>
                        </label>
                      </div>
                    </div>

                    <Button
                      type="submit"
                      disabled={submitting || isPolling}
                      className="w-full h-11 bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-sm gap-2"
                    >
                      {submitting ? (
                        <>
                          <Loader2 className="h-4 w-4 animate-spin" />
                          Initiating Pipeline...
                        </>
                      ) : (
                        <>
                          <Sparkles className="h-4 w-4" />
                          Start Lecture Ingestion
                        </>
                      )}
                    </Button>
                  </form>
                </TabsContent>

                {/* TAB 2: Course Playlist */}
                <TabsContent value="playlist" className="space-y-5 mt-0">
                  <div className="space-y-4">
                    <div>
                      <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                        YouTube Playlist URL
                      </label>
                      <div className="relative">
                        <Layers className="absolute left-3.5 top-1/2 -translate-y-1/2 h-5 w-5 text-indigo-600" />
                        <Input
                          value={playlistUrl}
                          onChange={(e) => setPlaylistUrl(e.target.value)}
                          placeholder="https://www.youtube.com/playlist?list=PLUl4u3cNGP63oMNUHXqIUcrkS2PivhN3k"
                          className="pl-11 h-11 text-sm bg-white"
                        />
                      </div>
                    </div>

                    {/* Instant Playlist Preview */}
                    {playlistUrl && (
                      <URLPreviewCard
                        url={playlistUrl}
                        onValidated={handlePlaylistValidated}
                      />
                    )}

                    {/* Estimated processing indicator */}
                    {playlistPreview && playlistPreview.video_count > 0 && (
                      <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs flex items-center justify-between">
                        <div className="flex items-center gap-2 text-slate-600">
                          <Clock className="h-4 w-4 text-indigo-600" />
                          <span>Estimated synthesis time:</span>
                        </div>
                        <span className="font-semibold text-slate-900">
                          ~{Math.max(1, Math.ceil(playlistPreview.video_count * 0.5))} -{" "}
                          {Math.max(2, Math.ceil(playlistPreview.video_count * 1.5))} mins
                        </span>
                      </div>
                    )}

                    <Button
                      onClick={onSubmitPlaylist}
                      disabled={playlistSubmitting || isPolling || !playlistUrl.trim()}
                      className="w-full h-11 bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-sm gap-2"
                    >
                      {playlistSubmitting ? (
                        <>
                          <Loader2 className="h-4 w-4 animate-spin" />
                          Queuing Playlist Pipeline...
                        </>
                      ) : (
                        <>
                          <Layers className="h-4 w-4" />
                          Process Full Course Playlist
                        </>
                      )}
                    </Button>
                  </div>
                </TabsContent>

                {/* TAB 3: Upload Transcript */}
                <TabsContent value="upload" className="space-y-5 mt-0">
                  <div className="space-y-4">
                    {/* Drag and Drop Zone */}
                    <div
                      onDragOver={(e) => {
                        e.preventDefault();
                        setIsDragOver(true);
                      }}
                      onDragLeave={() => setIsDragOver(false)}
                      onDrop={handleFileDrop}
                      onClick={() => fileInputRef.current?.click()}
                      className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
                        isDragOver
                          ? "border-indigo-500 bg-indigo-50/50"
                          : selectedFile
                          ? "border-emerald-400 bg-emerald-50/20"
                          : "border-slate-200 hover:border-indigo-400 hover:bg-slate-50/50"
                      }`}
                    >
                      <input
                        ref={fileInputRef}
                        type="file"
                        accept=".srt,.vtt,.txt"
                        className="hidden"
                        onChange={(e) => {
                          if (e.target.files?.[0]) {
                            setSelectedFile(e.target.files[0]);
                            setErrorMsg(null);
                          }
                        }}
                      />

                      <div className="flex flex-col items-center justify-center space-y-2">
                        {selectedFile ? (
                          <>
                            <CheckCircle2 className="h-10 w-10 text-emerald-500" />
                            <p className="font-semibold text-slate-800 text-sm">
                              {selectedFile.name}
                            </p>
                            <p className="text-xs text-slate-500">
                              {(selectedFile.size / 1024).toFixed(1)} KB — Click to change file
                            </p>
                          </>
                        ) : (
                          <>
                            <Upload className="h-10 w-10 text-slate-400" />
                            <p className="font-semibold text-slate-700 text-sm">
                              Drag and drop your subtitle or transcript file
                            </p>
                            <p className="text-xs text-slate-400">
                              Supports standard SubRip (.srt), WebVTT (.vtt), and raw text (.txt)
                            </p>
                          </>
                        )}
                      </div>
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                        Associated YouTube URL (Optional)
                      </label>
                      <Input
                        value={associatedUrl}
                        onChange={(e) => setAssociatedUrl(e.target.value)}
                        placeholder="https://www.youtube.com/watch?v=... (for timestamp alignment)"
                        className="h-10 text-xs bg-white"
                      />
                    </div>

                    <Button
                      onClick={handleUploadSubmit}
                      disabled={uploadSubmitting || !selectedFile}
                      className="w-full h-11 bg-emerald-600 hover:bg-emerald-700 text-white font-medium text-sm gap-2"
                    >
                      {uploadSubmitting ? (
                        <>
                          <Loader2 className="h-4 w-4 animate-spin" />
                          Parsing Subtitles & Chunking...
                        </>
                      ) : (
                        <>
                          <FileText className="h-4 w-4" />
                          Parse & Ingest Transcript
                        </>
                      )}
                    </Button>
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Real-time Job Progress & Status (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          <Card className="border-slate-200 shadow-sm bg-white overflow-hidden">
            <CardHeader className="pb-3 border-b border-slate-100 bg-slate-50/50 flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <Terminal className="h-4 w-4 text-indigo-600" />
                  Real-Time Pipeline Status
                </CardTitle>
                <CardDescription className="text-xs text-slate-500">
                  {jobId ? `Tracking Job: ${jobId}` : "Waiting for submission"}
                </CardDescription>
              </div>

              {job && (
                <Badge
                  variant="outline"
                  className={`text-xs capitalize font-semibold ${
                    job.status === "completed"
                      ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                      : job.status === "failed"
                      ? "bg-red-50 text-red-700 border-red-200"
                      : "bg-indigo-50 text-indigo-700 border-indigo-200"
                  }`}
                >
                  {job.status === "in_progress" && (
                    <Loader2 className="h-3 w-3 animate-spin mr-1 inline" />
                  )}
                  {job.status.replace("_", " ")}
                </Badge>
              )}
            </CardHeader>

            <CardContent className="p-4 space-y-4">
              {/* Progress Bar */}
              <div>
                <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1.5">
                  <span>Current Step: {job?.current_node || "Idle"}</span>
                  <span>{job?.progress_percentage || 0}%</span>
                </div>
                <Progress value={job?.progress_percentage || 0} className="h-2 bg-slate-100" />
              </div>

              {/* Terminal Logs Viewer */}
              <div className="rounded-lg bg-slate-950 text-slate-200 p-3.5 font-mono text-xs h-64 overflow-y-auto space-y-2 border border-slate-800 shadow-inner">
                {!job || job.logs.length === 0 ? (
                  <div className="text-slate-500 h-full flex flex-col items-center justify-center text-center p-4">
                    <Terminal className="h-8 w-8 text-slate-700 mb-2" />
                    <p>No active pipeline job.</p>
                    <p className="text-[11px] text-slate-600 mt-1">
                      Paste a YouTube lecture link on the left to start streaming live extraction logs.
                    </p>
                  </div>
                ) : (
                  job.logs.map((log, i) => (
                    <div key={i} className="flex items-start gap-2 leading-relaxed">
                      <span className="text-slate-500 select-none shrink-0">
                        [{log.timestamp.slice(11, 19)}]
                      </span>
                      <span
                        className={`font-semibold shrink-0 ${
                          log.level === "error"
                            ? "text-red-400"
                            : log.level === "warning"
                            ? "text-amber-400"
                            : "text-indigo-400"
                        }`}
                      >
                        [{log.node}]
                      </span>
                      <span
                        className={`${
                          log.level === "error"
                            ? "text-red-300"
                            : log.level === "warning"
                            ? "text-amber-200"
                            : "text-slate-200"
                        }`}
                      >
                        {log.message}
                      </span>
                    </div>
                  ))
                )}
              </div>

              {/* Success / Completion Card */}
              {isComplete && (
                <div className="p-4 rounded-xl border border-emerald-200 bg-emerald-50/60 text-emerald-950 space-y-3">
                  <div className="flex items-center gap-2 font-bold text-sm text-emerald-900">
                    <CheckCircle2 className="h-5 w-5 text-emerald-600" />
                    <span>Lecture Transcript Ready!</span>
                  </div>
                  <p className="text-xs text-emerald-800 leading-relaxed">
                    All audio segments have been extracted, filler words normalized, and semantic topic chunks indexed for agentic study note generation.
                  </p>

                  <div className="flex items-center gap-2 pt-1 flex-wrap">
                    <Button
                      size="sm"
                      onClick={() => setShowTranscriptViewer((prev) => !prev)}
                      className="bg-emerald-700 hover:bg-emerald-800 text-white text-xs gap-1.5 h-8"
                    >
                      <FileText className="h-3.5 w-3.5" />
                      {showTranscriptViewer ? "Hide Transcript" : "View Transcript"}
                    </Button>

                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <div>
                            <Button
                              size="sm"
                              disabled
                              variant="outline"
                              className="text-xs text-slate-400 border-slate-300 h-8 gap-1.5 cursor-not-allowed opacity-75"
                            >
                              <Sparkles className="h-3.5 w-3.5" />
                              Generate Notes
                            </Button>
                          </div>
                        </TooltipTrigger>
                        <TooltipContent side="top">
                          <p>Multi-Agent Note Synthesis arrives in Phase 3</p>
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  </div>
                </div>
              )}

              {/* Upload Success Card */}
              {uploadResult && (
                <div className="p-4 rounded-xl border border-emerald-200 bg-emerald-50/60 text-emerald-950 space-y-3">
                  <div className="flex items-center gap-2 font-bold text-sm text-emerald-900">
                    <CheckCircle2 className="h-5 w-5 text-emerald-600" />
                    <span>File Parsed Successfully</span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="bg-white/80 p-2 rounded border border-emerald-100">
                      <span className="text-slate-500 block">Segments:</span>
                      <span className="font-bold text-slate-800">
                        {uploadResult.segment_count}
                      </span>
                    </div>
                    <div className="bg-white/80 p-2 rounded border border-emerald-100">
                      <span className="text-slate-500 block">Topic Chunks:</span>
                      <span className="font-bold text-slate-800">
                        {uploadResult.chunk_count}
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Bottom Section: Transcript Viewer (When Toggled or Completed) */}
      {showTranscriptViewer && activeVideoId && (
        <div className="mt-8 pt-6 border-t border-slate-200">
          <TranscriptViewer
            videoId={activeVideoId}
            videoTitle={activeVideoTitle || undefined}
            initialChunks={uploadResult?.chunks}
          />
        </div>
      )}
    </PageContainer>
  );
};
