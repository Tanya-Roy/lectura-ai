import React, { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeKatex from "rehype-katex";
import {
  FileText,
  ListTree,
  ShieldCheck,
  Download,
  Copy,
  Check,
  Share2,
  Sparkles,
  Layers,
  Zap,
  HelpCircle,
  MessageSquare,
  Clock,
} from "lucide-react";
import { PageContainer } from "../components/layout/PageContainer";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Tabs, TabsList, TabsTrigger } from "../components/ui/tabs";
import { getNote, getNotes } from "../services/api";
import { Note, NoteType } from "../types";
import { useNavigate } from "react-router-dom";

export const NotesPage: React.FC = () => {
  const [selectedType, setSelectedType] = useState<NoteType>("comprehensive");
  const [note, setNote] = useState<Note | null>(null);
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchNoteData = async () => {
      setLoading(true);
      try {
        let noteId = "nt_comp_001";
        if (selectedType === "revision") noteId = "nt_rev_002";
        if (selectedType === "last_minute") noteId = "nt_last_003";

        const data = await getNote(noteId);
        setNote(data);
      } catch (err) {
        console.error("Failed to load note:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchNoteData();
  }, [selectedType]);

  const handleCopy = () => {
    if (note?.markdown_content) {
      navigator.clipboard.writeText(note.markdown_content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleDownload = () => {
    if (!note?.markdown_content) return;
    const blob = new Blob([note.markdown_content], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `lectura_notes_${selectedType}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <PageContainer
      title="Study Notes Workspace"
      subtitle="Master concepts with verified multi-tiered academic synthesis."
      action={
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={handleCopy} className="gap-1.5">
            {copied ? <Check className="h-4 w-4 text-emerald-600" /> : <Copy className="h-4 w-4" />}
            <span>{copied ? "Copied" : "Copy Markdown"}</span>
          </Button>

          <Button variant="outline" size="sm" onClick={handleDownload} className="gap-1.5">
            <Download className="h-4 w-4" />
            <span>Export .md</span>
          </Button>

          <Button size="sm" onClick={() => navigate("/chat")} className="gap-1.5 shadow-sm">
            <MessageSquare className="h-4 w-4" />
            <span>Ask Lecture AI</span>
          </Button>
        </div>
      }
    >
      {/* Note Type Selector Tabs & Verification Report Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2">
        <Tabs value={selectedType} onValueChange={(val) => setSelectedType(val as NoteType)}>
          <TabsList className="bg-slate-200/70 p-1 rounded-xl">
            <TabsTrigger value="comprehensive" className="gap-2 text-xs font-semibold">
              <FileText className="h-3.5 w-3.5" /> Comprehensive Notes
            </TabsTrigger>
            <TabsTrigger value="revision" className="gap-2 text-xs font-semibold">
              <Layers className="h-3.5 w-3.5" /> Revision Cheat Sheet
            </TabsTrigger>
            <TabsTrigger value="last_minute" className="gap-2 text-xs font-semibold">
              <Zap className="h-3.5 w-3.5" /> Last-Minute Prep ⚡
            </TabsTrigger>
          </TabsList>
        </Tabs>

        {/* Verification Pill */}
        <div className="flex items-center gap-2">
          <Badge variant="success" className="gap-1.5 text-xs py-1 px-3">
            <ShieldCheck className="h-4 w-4 text-emerald-700" />
            <span>Fact-Check Score: 98% (16 Claims Audited)</span>
          </Badge>
        </div>
      </div>

      {/* Main Two-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Left: Outline & Navigation Tree */}
        <div className="lg:col-span-1 space-y-5">
          <Card className="border-slate-200 sticky top-24">
            <CardContent className="p-4 space-y-4">
              <div className="flex items-center gap-2 text-xs font-bold text-slate-700 uppercase tracking-wider pb-2 border-b border-slate-100">
                <ListTree className="h-4 w-4 text-primary-700" />
                <span>Outline Navigation</span>
              </div>

              <div className="space-y-1 text-xs">
                {(note?.outline || [
                  { title: "1. Mathematical Foundations & Formulation", timestamp: 0.0 },
                  { title: "2. Regularization & Asymptotic Bounds", timestamp: 240.0 },
                  { title: "3. Algorithmic Implementation Steps", timestamp: 560.0 },
                ]).map((item, idx) => (
                  <button
                    key={idx}
                    className="w-full text-left p-2 rounded-lg hover:bg-slate-100 text-slate-700 hover:text-primary-800 transition-colors flex items-center justify-between group"
                  >
                    <span className="line-clamp-1 font-medium">{item.title}</span>
                    <span className="text-[10px] text-slate-400 font-mono group-hover:text-primary-600 shrink-0 ml-1">
                      {item.timestamp !== undefined ? `${Math.floor(item.timestamp / 60)}:00` : ""}
                    </span>
                  </button>
                ))}
              </div>

              <div className="pt-3 border-t border-slate-100">
                <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-2">
                  Key Takeaways
                </span>
                <ul className="space-y-2 text-xs text-slate-600">
                  {(note?.key_takeaways || [
                    "Strong convexity guarantees unique global minima with L2 penalty.",
                    "Bias-variance tradeoff depends directly on regularization factor lambda.",
                  ]).map((point, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-primary-600 font-bold">•</span>
                      <span className="leading-relaxed">{point}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="pt-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => navigate("/video-notes")}
                  className="w-full text-xs gap-1.5"
                >
                  <Clock className="h-3.5 w-3.5 text-primary-600" />
                  <span>Open Split Video View</span>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right: Markdown Notes Canvas */}
        <div className="lg:col-span-3">
          <Card className="border-slate-200 bg-white shadow-sm">
            <CardContent className="p-6 sm:p-10">
              <article className="prose prose-slate max-w-none prose-headings:font-bold prose-h1:text-2xl prose-h1:text-slate-900 prose-h2:text-xl prose-h2:text-slate-800 prose-h3:text-lg prose-p:text-slate-700 prose-p:leading-relaxed prose-code:text-primary-900 prose-code:bg-primary-50 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-pre:bg-slate-900 prose-pre:text-slate-100">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  rehypePlugins={[rehypeKatex]}
                >
                  {note?.markdown_content || "# Loading Lecture Notes..."}
                </ReactMarkdown>
              </article>
            </CardContent>
          </Card>
        </div>
      </div>
    </PageContainer>
  );
};
