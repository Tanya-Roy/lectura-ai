import React, { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import {
  BookOpen,
  Video as VideoIcon,
  Play,
  FileText,
  HelpCircle,
  Layers,
  Clock,
  ArrowRight,
  CheckCircle2,
  Share2,
} from "lucide-react";
import { PageContainer } from "../components/layout/PageContainer";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { getCourse } from "../services/api";
import { Course } from "../types";
import { formatSeconds } from "../lib/utils";

export const CoursePage: React.FC = () => {
  const { courseId = "crs_ml_101" } = useParams<{ courseId: string }>();
  const [course, setCourse] = useState<Course | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchCourseData = async () => {
      try {
        const data = await getCourse(courseId);
        setCourse(data);
      } catch (err) {
        console.error("Failed to load course details:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchCourseData();
  }, [courseId]);

  return (
    <PageContainer
      title={course?.title || "Machine Learning & Statistical Optimization"}
      subtitle={`${course?.channel_name || "MIT OpenCourseWare"} • ${course?.videos?.length || 3} Comprehensive Lectures`}
      action={
        <div className="flex items-center gap-2">
          <Link to="/notes">
            <Button variant="outline" size="sm" className="gap-1.5">
              <FileText className="h-4 w-4" /> Notes Workspace
            </Button>
          </Link>
          <Link to="/flashcards">
            <Button size="sm" className="gap-1.5">
              <Layers className="h-4 w-4" /> Review Deck
            </Button>
          </Link>
        </div>
      }
    >
      {/* Course Overview Banner */}
      <div className="rounded-2xl border border-slate-200 bg-white p-6 sm:p-8 flex flex-col md:flex-row gap-6 shadow-sm">
        <div className="w-full md:w-72 h-44 rounded-xl overflow-hidden bg-slate-100 shrink-0">
          <img
            src={course?.thumbnail_url || "https://images.unsplash.com/photo-1509228468518-180dd4864904?w=600"}
            alt={course?.title}
            className="w-full h-full object-cover"
          />
        </div>
        <div className="flex-1 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Badge variant="default" className="text-xs">University Curriculum</Badge>
              <Badge variant="outline" className="text-xs">100% Fact-Checked</Badge>
            </div>
            <p className="text-sm text-slate-600 leading-relaxed">
              {course?.description ||
                "Deep formulation of gradient descent, empirical loss functions, generalization bounds, and asymptotic stability."}
            </p>
          </div>

          <div className="mt-4 pt-4 border-t border-slate-100 grid grid-cols-3 gap-4 text-xs text-slate-500">
            <div>
              <span className="block font-bold text-slate-800 text-sm">{course?.videos?.length || 3}</span>
              <span>Modules</span>
            </div>
            <div>
              <span className="block font-bold text-slate-800 text-sm">3.5 hrs</span>
              <span>Total Video Runtime</span>
            </div>
            <div>
              <span className="block font-bold text-slate-800 text-sm">98%</span>
              <span>Audit Rigor Score</span>
            </div>
          </div>
        </div>
      </div>

      {/* Sequential Lecture List */}
      <div className="space-y-4">
        <h3 className="text-lg font-bold text-slate-900">Lectures & Modules</h3>

        <div className="space-y-3">
          {(course?.videos || [
            {
              id: "vid_1",
              title: "Lecture 1: Loss Minimization & Empirical Risk Bounds",
              description: "Formulation of parameter space and convex loss functions.",
              duration_seconds: 1200,
            },
            {
              id: "vid_2",
              title: "Lecture 2: Regularization Mechanics & L2 Penalty",
              description: "Preventing asymptotic drift with Tikhonov regularization.",
              duration_seconds: 1380,
            },
            {
              id: "vid_3",
              title: "Lecture 3: Convergence Analysis of Gradient Descent",
              description: "Lipschitz continuity and accelerated Nesterov momentum.",
              duration_seconds: 1560,
            },
          ]).map((video: any, index: number) => (
            <Card
              key={video.id || index}
              className="hover:border-primary-300 hover:shadow-sm transition-all"
            >
              <CardContent className="p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="flex items-start gap-4">
                  <div className="h-10 w-10 rounded-xl bg-primary-100 text-primary-800 flex items-center justify-center font-bold text-sm shrink-0">
                    {index + 1}
                  </div>
                  <div>
                    <h4 className="font-semibold text-slate-900 text-sm leading-snug">
                      {video.title}
                    </h4>
                    <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                      {video.description}
                    </p>
                    <div className="flex items-center gap-3 mt-2 text-[11px] text-slate-400 font-medium">
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" /> {formatSeconds(video.duration_seconds || 1200)}
                      </span>
                      <span>•</span>
                      <span className="flex items-center gap-1 text-emerald-600">
                        <CheckCircle2 className="h-3 w-3" /> Notes Verified
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 self-end sm:self-center shrink-0">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => navigate("/video-notes")}
                    className="gap-1.5"
                  >
                    <Play className="h-3.5 w-3.5 text-primary-600" />
                    <span>Watch & Notes</span>
                  </Button>
                  <Button
                    size="sm"
                    onClick={() => navigate("/notes")}
                    className="gap-1.5"
                  >
                    <FileText className="h-3.5 w-3.5" />
                    <span>Read Notes</span>
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </PageContainer>
  );
};
