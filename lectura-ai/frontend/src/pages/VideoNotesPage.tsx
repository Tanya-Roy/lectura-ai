import React, { useState } from "react";
import { Link } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeKatex from "rehype-katex";
import {
  Play,
  FileText,
  Clock,
  Sparkles,
  ArrowLeft,
  Share2,
  ExternalLink,
  ShieldCheck,
  CheckCircle2,
} from "lucide-react";
import { PageContainer } from "../components/layout/PageContainer";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Badge } from "../components/ui/badge";

export const VideoNotesPage: React.FC = () => {
  const [currentTimestamp, setCurrentTimestamp] = useState<number>(0);
  const videoId = "dQw4w9WgXcQ"; // Default fallback YouTube video embed

  const timestamps = [
    { label: "00:00 - Introduction & Motivation", time: 0 },
    { label: "03:45 - Empirical Risk Formulation", time: 225 },
    { label: "07:15 - Tikhonov Regularization Proof", time: 435 },
    { label: "11:20 - Gradient Dynamics & Stability", time: 680 },
  ];

  return (
    <PageContainer
      title="Interactive Split Workspace"
      subtitle="Watch lecture video synchronized alongside verified academic notes."
      action={
        <Link to="/notes">
          <Button variant="outline" size="sm" className="gap-1.5">
            <ArrowLeft className="h-4 w-4" /> Full Note Canvas
          </Button>
        </Link>
      }
    >
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-[calc(100vh-14rem)]">
        {/* Left Column (5 cols): Embedded Video & Key Timestamps */}
        <div className="lg:col-span-6 flex flex-col gap-4">
          <Card className="border-slate-200 overflow-hidden bg-black aspect-video rounded-xl shadow-md">
            <iframe
              src={`https://www.youtube.com/embed/${videoId}?autoplay=0&enablejsapi=1`}
              title="YouTube Lecture Player"
              className="w-full h-full border-0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            />
          </Card>

          {/* Timestamps Seeking Navigation */}
          <Card className="border-slate-200 flex-1 overflow-hidden flex flex-col">
            <div className="p-3.5 border-b border-slate-100 flex items-center justify-between bg-slate-50">
              <span className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
                <Clock className="h-3.5 w-3.5 text-primary-700" />
                <span>Lecture Jump Points</span>
              </span>
              <Badge variant="secondary" className="text-[10px]">
                4 Chapters Indexed
              </Badge>
            </div>
            <div className="p-3 overflow-y-auto space-y-1.5 flex-1">
              {timestamps.map((t, idx) => (
                <button
                  key={idx}
                  onClick={() => setCurrentTimestamp(t.time)}
                  className="w-full text-left p-2.5 rounded-lg hover:bg-primary-50 text-slate-700 hover:text-primary-800 transition-colors flex items-center justify-between text-xs"
                >
                  <span className="font-medium line-clamp-1">{t.label}</span>
                  <Play className="h-3 w-3 text-primary-600 shrink-0 ml-2" />
                </button>
              ))}
            </div>
          </Card>
        </div>

        {/* Right Column (6 cols): Synchronized Notes */}
        <div className="lg:col-span-6 h-full flex flex-col">
          <Card className="border-slate-200 flex-1 overflow-hidden flex flex-col bg-white">
            <div className="p-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
              <div className="flex items-center gap-2">
                <FileText className="h-4 w-4 text-primary-700" />
                <span className="text-sm font-bold text-slate-800">
                  Synchronized Lecture Guide
                </span>
              </div>
              <Badge variant="success" className="text-[10px] gap-1">
                <CheckCircle2 className="h-3 w-3" />
                Verified
              </Badge>
            </div>

            <div className="p-6 overflow-y-auto flex-1 prose prose-sm max-w-none prose-p:leading-relaxed prose-headings:font-bold">
              <h3>1. Mathematical Foundations & Empirical Risk</h3>
              <p>
                In standard empirical risk minimization (ERM), the learner chooses hypothesis
                parameters $\theta \in \Theta$ that minimize sample loss:
              </p>
              <div className="p-3 bg-slate-50 border rounded-lg text-center font-mono text-xs text-primary-900">
                $$\widehat{\mathcal{R}}_N(\theta) = \frac{1}{N}\sum_{i=1}^N \ell(f(x_i; \theta), y_i)$$
              </div>
              <p>
                Because sample variance in high dimensions causes parameters to explode, we enforce
                Tikhonov $L_2$ regularization:
              </p>
              <div className="p-3 bg-slate-50 border rounded-lg text-center font-mono text-xs text-primary-900">
                $$\min_{\theta} \left\{ \widehat{\mathcal{R}}_N(\theta) + \frac{\lambda}{2}\|\theta\|_2^2 \right\}$$
              </div>
              <h3>2. Stability Analysis</h3>
              <p>
                When $\lambda &gt; 0$, the curvature of the Hessian is bounded strictly away from
                singular values, which eliminates flat saddle surfaces and accelerates convergence.
              </p>
            </div>
          </Card>
        </div>
      </div>
    </PageContainer>
  );
};
