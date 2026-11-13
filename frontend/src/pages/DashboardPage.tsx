import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  BookOpen,
  Video as VideoIcon,
  FileText,
  Layers,
  Sparkles,
  ArrowRight,
  Plus,
  Clock,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  Flame,
} from "lucide-react";
import { PageContainer } from "../components/layout/PageContainer";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { getCourses, getProgressSummary } from "../services/api";
import { Course } from "../types";
import { useStore } from "../store/useStore";

export const DashboardPage: React.FC = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const { currentUser, activeJob } = useStore();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [courseList, progressData] = await Promise.all([
          getCourses(),
          getProgressSummary(),
        ]);
        setCourses(courseList);
        setSummary(progressData);
      } catch (err) {
        console.error("Dashboard fetch error:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  return (
    <PageContainer
      title={`Welcome back, ${currentUser?.full_name?.split(" ")[0] || "Scholar"} 👋`}
      subtitle="Here is your learning trajectory, recent courses, and active synthesis jobs."
      action={
        <Link to="/import">
          <Button className="gap-2 shadow-sm">
            <Plus className="h-4 w-4" />
            <span>Import New Lecture</span>
          </Button>
        </Link>
      }
    >
      {/* Quick Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <Card className="border-slate-200">
          <CardContent className="p-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Courses</p>
              <h3 className="text-2xl font-bold text-slate-900 mt-1">{courses.length}</h3>
              <p className="text-xs text-slate-400 mt-1">2 playlists enrolled</p>
            </div>
            <div className="h-11 w-11 rounded-xl bg-primary-100 flex items-center justify-center text-primary-700">
              <BookOpen className="h-5 w-5" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-slate-200">
          <CardContent className="p-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Flashcards</p>
              <h3 className="text-2xl font-bold text-slate-900 mt-1">
                {summary?.flashcards_mastered || 48}
              </h3>
              <p className="text-xs text-emerald-600 font-medium mt-1">12 due for review</p>
            </div>
            <div className="h-11 w-11 rounded-xl bg-purple-100 flex items-center justify-center text-purple-700">
              <Layers className="h-5 w-5" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-slate-200">
          <CardContent className="p-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Quiz Accuracy</p>
              <h3 className="text-2xl font-bold text-slate-900 mt-1">
                {summary?.average_quiz_accuracy || 92.4}%
              </h3>
              <p className="text-xs text-slate-400 mt-1">Across 12 assessments</p>
            </div>
            <div className="h-11 w-11 rounded-xl bg-emerald-100 flex items-center justify-center text-emerald-700">
              <CheckCircle2 className="h-5 w-5" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-slate-200">
          <CardContent className="p-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Active Streak</p>
              <h3 className="text-2xl font-bold text-slate-900 mt-1">
                {summary?.active_streak_days || 7} Days
              </h3>
              <p className="text-xs text-amber-600 font-medium mt-1">Top 5% of learners</p>
            </div>
            <div className="h-11 w-11 rounded-xl bg-amber-100 flex items-center justify-center text-amber-700">
              <Flame className="h-5 w-5" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Active Synthesis Job Banner if any */}
      {activeJob && (
        <Card className="border-primary-200 bg-primary-50/50">
          <CardContent className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-3.5">
              <div className="h-10 w-10 rounded-xl bg-primary-700 flex items-center justify-center text-white shrink-0">
                <Sparkles className="h-5 w-5 animate-pulse" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="font-semibold text-slate-900 text-sm">Background Agent Pipeline Running</h4>
                  <Badge variant="default" className="text-[10px] bg-primary-700">
                    {activeJob.progress_percentage}% Done
                  </Badge>
                </div>
                <p className="text-xs text-slate-500 mt-0.5">
                  Currently executing: <strong>{activeJob.current_node || "Synthesis"}</strong>. Fact-checking formulas and structuring outlines.
                </p>
              </div>
            </div>
            <Link to="/import">
              <Button size="sm" variant="outline" className="gap-1.5 shrink-0">
                <span>View Job Details</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </Button>
            </Link>
          </CardContent>
        </Card>
      )}

      {/* Recent Courses Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-slate-900">Enrolled Courses & Lectures</h2>
          <Link to="/courses" className="text-xs font-semibold text-primary-700 hover:underline">
            View All Courses
          </Link>
        </div>

        {courses.length === 0 && !loading ? (
          <Card className="border-dashed border-slate-300 p-12 text-center">
            <BookOpen className="h-12 w-12 text-slate-300 mx-auto mb-3" />
            <h4 className="text-base font-semibold text-slate-700">No courses processed yet</h4>
            <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
              Paste your first YouTube lecture link to start generating university-level notes.
            </p>
            <Link to="/import">
              <Button size="sm" className="mt-4 gap-1.5">
                <Plus className="h-4 w-4" /> Import First Lecture
              </Button>
            </Link>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {courses.map((course) => (
              <Card
                key={course.id}
                className="overflow-hidden group hover:border-primary-400 hover:shadow-md transition-all cursor-pointer flex flex-col"
                onClick={() => navigate(`/courses/${course.id}`)}
              >
                <div className="relative h-44 w-full bg-slate-100 overflow-hidden">
                  <img
                    src={course.thumbnail_url || "https://images.unsplash.com/photo-1509228468518-180dd4864904?w=600"}
                    alt={course.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  <div className="absolute top-3 right-3">
                    <Badge variant="secondary" className="bg-slate-900/80 text-white backdrop-blur-sm text-[10px]">
                      {course.is_playlist ? "Full Playlist" : "Single Lecture"}
                    </Badge>
                  </div>
                </div>

                <CardContent className="p-5 flex-1 flex flex-col justify-between">
                  <div>
                    <span className="text-xs font-semibold text-primary-700">{course.channel_name}</span>
                    <h4 className="text-base font-bold text-slate-900 mt-1 leading-snug line-clamp-2">
                      {course.title}
                    </h4>
                    <p className="text-xs text-slate-500 mt-1.5 line-clamp-2 leading-relaxed">
                      {course.description}
                    </p>
                  </div>

                  <div className="mt-4 pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                    <span className="flex items-center gap-1">
                      <VideoIcon className="h-3.5 w-3.5 text-slate-400" />
                      {course.video_count || 1} Lectures
                    </span>
                    <span className="flex items-center gap-1 font-semibold text-primary-700">
                      Study Notes <ArrowRight className="h-3.5 w-3.5" />
                    </span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Quick Study Actions */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5 pt-4">
        <Card
          className="hover:border-primary-300 transition-all cursor-pointer"
          onClick={() => navigate("/notes")}
        >
          <CardContent className="p-5 flex items-start gap-4">
            <div className="h-10 w-10 rounded-xl bg-purple-50 text-purple-700 flex items-center justify-center shrink-0">
              <FileText className="h-5 w-5" />
            </div>
            <div>
              <h4 className="font-semibold text-slate-900 text-sm">Study Master Notes</h4>
              <p className="text-xs text-slate-500 mt-1">Read comprehensive LaTeX lecture write-ups.</p>
            </div>
          </CardContent>
        </Card>

        <Card
          className="hover:border-primary-300 transition-all cursor-pointer"
          onClick={() => navigate("/flashcards")}
        >
          <CardContent className="p-5 flex items-start gap-4">
            <div className="h-10 w-10 rounded-xl bg-amber-50 text-amber-700 flex items-center justify-center shrink-0">
              <Layers className="h-5 w-5" />
            </div>
            <div>
              <h4 className="font-semibold text-slate-900 text-sm">Flashcard Practice</h4>
              <p className="text-xs text-slate-500 mt-1">Spaced-repetition review of key definitions.</p>
            </div>
          </CardContent>
        </Card>

        <Card
          className="hover:border-primary-300 transition-all cursor-pointer"
          onClick={() => navigate("/quizzes")}
        >
          <CardContent className="p-5 flex items-start gap-4">
            <div className="h-10 w-10 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center shrink-0">
              <HelpCircle className="h-5 w-5" />
            </div>
            <div>
              <h4 className="font-semibold text-slate-900 text-sm">Diagnostic Quizzes</h4>
              <p className="text-xs text-slate-500 mt-1">Test your mastery with concept assessments.</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </PageContainer>
  );
};
