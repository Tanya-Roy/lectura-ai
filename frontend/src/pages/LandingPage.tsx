import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  GraduationCap,
  Sparkles,
  ArrowRight,
  CheckCircle2,
  FileText,
  Layers,
  HelpCircle,
  ShieldCheck,
  BrainCircuit,
  Zap,
  Play,
  Youtube,
  Search,
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Badge } from "../components/ui/badge";
import { Card, CardContent } from "../components/ui/card";
import { useStore } from "../store/useStore";
import { processVideo } from "../services/api";

export const LandingPage: React.FC = () => {
  const [urlInput, setUrlInput] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();
  const { setActiveJob } = useStore();

  const handleHeroSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const trimmed = urlInput.trim();
    if (!trimmed) {
      setError("Please paste a valid YouTube video or playlist URL.");
      return;
    }

    const isYouTube = /(?:youtube\.com\/(?:watch\?v=|embed\/|playlist\?list=)|youtu\.be\/)/i.test(
      trimmed
    );

    if (!isYouTube) {
      setError("Only YouTube video or playlist links are supported currently.");
      return;
    }

    setIsSubmitting(true);
    try {
      const job = await processVideo({ url: trimmed });
      setActiveJob(job);
      navigate("/import");
    } catch (err: any) {
      // Navigate to import page anyway with the pre-filled URL
      navigate(`/import?url=${encodeURIComponent(trimmed)}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      {/* Top Navigation */}
      <header className="border-b border-slate-200 bg-white/90 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-xl bg-primary-700 flex items-center justify-center text-white shadow-md shadow-primary-700/25">
              <GraduationCap className="h-5 w-5" />
            </div>
            <div className="flex items-center gap-1.5">
              <span className="font-bold text-xl text-slate-900 tracking-tight">Lectura</span>
              <span className="text-xs font-bold text-primary-700 bg-primary-50 px-2 py-0.5 rounded-full border border-primary-200">
                AI
              </span>
            </div>
          </div>

          <div className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-600">
            <a href="#features" className="hover:text-primary-700 transition-colors">Features</a>
            <a href="#how-it-works" className="hover:text-primary-700 transition-colors">How It Works</a>
            <a href="#notes-preview" className="hover:text-primary-700 transition-colors">Sample Notes</a>
            <a href="#testimonials" className="hover:text-primary-700 transition-colors">For Students</a>
          </div>

          <div className="flex items-center gap-3">
            <Link to="/dashboard">
              <Button variant="outline" size="sm">
                Dashboard
              </Button>
            </Link>
            <Link to="/import">
              <Button size="sm" className="gap-1.5 shadow-sm">
                <Sparkles className="h-3.5 w-3.5" />
                <span>Get Started Free</span>
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative overflow-hidden pt-20 pb-24 lg:pt-28 lg:pb-32 bg-gradient-to-b from-white via-purple-50/30 to-slate-50">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary-50 border border-primary-200 text-xs font-semibold text-primary-800 mb-6 shadow-sm">
            <Sparkles className="h-3.5 w-3.5 text-primary-600" />
            <span>Agentic Multi-Stage Academic Synthesis</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold text-slate-900 tracking-tight leading-tight">
            Turn Any YouTube Lecture Into{" "}
            <span className="bg-gradient-to-r from-primary-700 to-primary-500 bg-clip-text text-transparent">
              Verified University-Grade
            </span>{" "}
            Study Notes.
          </h1>

          <p className="mt-6 text-lg sm:text-xl text-slate-600 max-w-3xl mx-auto leading-relaxed">
            Stop pausing, rewinding, and scribbling messy notes. Lectura AI parses video transcripts, verifies mathematical derivations, structures multi-tiered study summaries, and generates active recall flashcards.
          </p>

          {/* URL Input Form */}
          <div className="mt-10 max-w-2xl mx-auto">
            <form onSubmit={handleHeroSubmit} className="relative flex flex-col sm:flex-row gap-2.5 bg-white p-2.5 rounded-2xl shadow-xl shadow-primary-700/5 border border-slate-200">
              <div className="relative flex-1">
                <Youtube className="absolute left-3.5 top-1/2 -translate-y-1/2 h-5 w-5 text-red-500" />
                <Input
                  type="url"
                  placeholder="Paste YouTube video or playlist link (e.g. MIT OpenCourseWare)..."
                  className="pl-11 h-12 text-sm border-0 focus-visible:ring-0 focus-visible:ring-offset-0 bg-transparent"
                  value={urlInput}
                  onChange={(e) => setUrlInput(e.target.value)}
                />
              </div>
              <Button type="submit" size="lg" disabled={isSubmitting} className="h-12 gap-2 px-6">
                {isSubmitting ? (
                  <span>Analyzing...</span>
                ) : (
                  <>
                    <span>Generate Notes</span>
                    <ArrowRight className="h-4 w-4" />
                  </>
                )}
              </Button>
            </form>

            {error && (
              <p className="mt-2 text-xs text-red-600 text-left font-medium pl-3">{error}</p>
            )}

            <div className="mt-3 flex items-center justify-center gap-4 text-xs text-slate-500">
              <span className="flex items-center gap-1">
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" /> No sign-up required to test
              </span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" /> Full Playlists supported
              </span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" /> LaTeX Math Verified
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Showcase Grid (8 cards) */}
      <section id="features" className="py-20 bg-white border-y border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-xs font-bold uppercase tracking-wider text-primary-700 mb-2">Capabilities</h2>
            <h3 className="text-3xl font-bold text-slate-900 tracking-tight">
              Engineered specifically for serious academic and technical learning
            </h3>
            <p className="mt-3 text-slate-600 text-sm">
              Standard AI summarizers produce vague bullet points. Lectura AI uses specialized multi-agent workflows to preserve mathematical rigor and deep hierarchical outlines.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                icon: Layers,
                title: "3-Tiered Note Synthesis",
                desc: "Get Comprehensive textbook guides, Executive revision cheat sheets, and 5-minute Last-Minute exam summaries.",
              },
              {
                icon: ShieldCheck,
                title: "Academic Fact-Checking Agent",
                desc: "An independent verification agent audits formulas against standard proofs and checks claims for hallucinations.",
              },
              {
                icon: BrainCircuit,
                title: "LaTeX & KaTeX Equations",
                desc: "Every mathematical formulation is parsed into clean KaTeX equations with variable definitions and units.",
              },
              {
                icon: Play,
                title: "Playlist Ingestion",
                desc: "Input entire 40-lecture semester playlists. Lectura builds a structured course hierarchy with synchronized navigation.",
              },
              {
                icon: Zap,
                title: "Spaced-Repetition Flashcards",
                desc: "Automatically extracts high-yield definitions into SM-2 flashcard decks with active recall scoring.",
              },
              {
                icon: HelpCircle,
                title: "Self-Testing Quizzes",
                desc: "Multiple-choice diagnostic quizzes with detailed explanations linked back to the exact video timestamp.",
              },
              {
                icon: Search,
                title: "Timestamped Citations",
                desc: "Click any note paragraph or quiz question to immediately jump to the exact second in the lecture video.",
              },
              {
                icon: FileText,
                title: "Export to Markdown & PDF",
                desc: "Download high-resolution study guides formatted for Obsidian, Notion, Anki, or printable exam binders.",
              },
            ].map((f, i) => {
              const Icon = f.icon;
              return (
                <Card key={i} className="hover:border-primary-300 hover:shadow-md transition-all">
                  <CardContent className="p-6">
                    <div className="h-10 w-10 rounded-xl bg-primary-100 flex items-center justify-center text-primary-700 mb-4">
                      <Icon className="h-5 w-5" />
                    </div>
                    <h4 className="font-semibold text-slate-900 mb-1.5">{f.title}</h4>
                    <p className="text-xs text-slate-500 leading-relaxed">{f.desc}</p>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      </section>

      {/* How It Works (3 Steps) */}
      <section id="how-it-works" className="py-20 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-xs font-bold uppercase tracking-wider text-primary-700 mb-2">Workflow</h2>
            <h3 className="text-3xl font-bold text-slate-900 tracking-tight">How Lectura AI Works</h3>
            <p className="text-slate-600 text-sm mt-2">
              Transform hours of video lectures into actionable knowledge in 3 seamless steps.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-white p-8 rounded-2xl border border-slate-200 relative shadow-sm">
              <div className="text-4xl font-extrabold text-primary-200 mb-4">01</div>
              <h4 className="text-lg font-bold text-slate-900 mb-2">Ingest & Transcribe</h4>
              <p className="text-sm text-slate-600 leading-relaxed">
                Paste any YouTube lecture or playlist URL. The ingestion agent extracts high-precision transcripts and divides audio into conceptual timestamps.
              </p>
            </div>

            <div className="bg-white p-8 rounded-2xl border border-slate-200 relative shadow-sm">
              <div className="text-4xl font-extrabold text-primary-200 mb-4">02</div>
              <h4 className="text-lg font-bold text-slate-900 mb-2">Multi-Agent Synthesis</h4>
              <p className="text-sm text-slate-600 leading-relaxed">
                The extraction agent builds a hierarchical outline, while note-writer agents construct LaTeX formulas, summary tables, and flashcard recall items.
              </p>
            </div>

            <div className="bg-white p-8 rounded-2xl border border-slate-200 relative shadow-sm">
              <div className="text-4xl font-extrabold text-primary-200 mb-4">03</div>
              <h4 className="text-lg font-bold text-slate-900 mb-2">Verify & Master</h4>
              <p className="text-sm text-slate-600 leading-relaxed">
                The verification agent scores academic rigor. You study with interactive notes, quiz yourself, review flashcards, or chat with the lecture.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Example Notes Preview Section */}
      <section id="notes-preview" className="py-20 bg-white border-t border-slate-200">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <Badge variant="outline" className="mb-2 text-primary-700 border-primary-200">
              Live Sample Preview
            </Badge>
            <h3 className="text-3xl font-bold text-slate-900 tracking-tight">
              Sample Output: Convex Optimization & Risk
            </h3>
            <p className="text-slate-500 text-sm mt-1">Generated from MIT OpenCourseWare Lecture 4</p>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-slate-50/50 p-6 sm:p-8 shadow-sm">
            <div className="flex items-center justify-between pb-4 border-b border-slate-200 mb-6">
              <div className="flex items-center gap-2">
                <span className="h-3 w-3 rounded-full bg-red-400" />
                <span className="h-3 w-3 rounded-full bg-amber-400" />
                <span className="h-3 w-3 rounded-full bg-emerald-400" />
                <span className="text-xs font-mono text-slate-400 ml-2">lectura_notes_mit_ml_04.md</span>
              </div>
              <Badge variant="success" className="text-xs">
                Verified: 98% Rigor Score
              </Badge>
            </div>

            <div className="space-y-4 text-sm text-slate-800 font-sans">
              <h2 className="text-xl font-bold text-slate-900">1. Mathematical Foundations & Empirical Risk</h2>
              <p className="leading-relaxed">
                The objective is to identify a hypothesis parameter $\theta^* \in \Theta$ that minimizes true generalization risk over an unknown distribution $\mathcal{D}$:
              </p>
              <div className="p-4 bg-white rounded-xl border border-slate-200 font-mono text-xs text-primary-900 overflow-x-auto text-center">
                $$\min_{\theta \in \mathbb{R}^d} \left\{ \frac{1}{N}\sum_{i=1}^N \ell(f(x_i; \theta), y_i) + \frac{\lambda}{2} \|\theta\|_2^2 \right\}$$
              </div>
              <p className="leading-relaxed">
                <strong>Why Regularization Matters:</strong> Adding the strictly convex penalty $\frac{\lambda}{2}\|\theta\|_2^2$ forces the Hessian to remain positive definite, ensuring standard gradient descent achieves monotonic convergence at rate $\mathcal{O}(1/k)$.
              </p>
            </div>

            <div className="mt-8 pt-6 border-t border-slate-200 flex justify-between items-center">
              <span className="text-xs text-slate-500">Includes 3 Flashcards & 1 Diagnostic Quiz</span>
              <Link to="/notes">
                <Button size="sm" variant="default" className="gap-1.5">
                  <span>Open Full Interactive Workspace</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto bg-slate-900 text-slate-400 py-12 text-sm border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 rounded-lg bg-primary-700 flex items-center justify-center text-white">
              <GraduationCap className="h-4 w-4" />
            </div>
            <span className="font-bold text-white tracking-tight">Lectura AI</span>
            <span className="text-xs text-slate-500">© 2026. Production Academic Intelligence.</span>
          </div>

          <div className="flex items-center gap-6 text-xs">
            <Link to="/dashboard" className="hover:text-white transition-colors">Dashboard</Link>
            <Link to="/import" className="hover:text-white transition-colors">Import Video</Link>
            <Link to="/notes" className="hover:text-white transition-colors">Study Notes</Link>
            <Link to="/analytics" className="hover:text-white transition-colors">Progress Analytics</Link>
          </div>
        </div>
      </footer>
    </div>
  );
};
