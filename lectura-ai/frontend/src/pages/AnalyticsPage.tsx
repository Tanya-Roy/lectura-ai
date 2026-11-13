import React, { useState, useEffect } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
} from "recharts";
import {
  TrendingUp,
  Clock,
  Layers,
  CheckCircle2,
  Flame,
  Award,
  Sparkles,
  Calendar,
} from "lucide-react";
import { PageContainer } from "../components/layout/PageContainer";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { getProgressSummary } from "../services/api";

export const AnalyticsPage: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const stats = await getProgressSummary();
        setData(stats);
      } catch (err) {
        console.error("Analytics fetch error:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  const weeklyData = data?.weekly_activity || [
    { day: "Mon", minutes: 45, quizzes: 2 },
    { day: "Tue", minutes: 60, quizzes: 3 },
    { day: "Wed", minutes: 30, quizzes: 1 },
    { day: "Thu", minutes: 75, quizzes: 4 },
    { day: "Fri", minutes: 50, quizzes: 2 },
    { day: "Sat", minutes: 40, quizzes: 1 },
    { day: "Sun", minutes: 40, quizzes: 2 },
  ];

  const accuracyData = [
    { week: "Week 1", score: 78 },
    { week: "Week 2", score: 84 },
    { week: "Week 3", score: 89 },
    { week: "Week 4", score: 94 },
  ];

  return (
    <PageContainer
      title="Learning Mastery & Analytics"
      subtitle="Track your study velocity, retention index, and diagnostic quiz accuracy."
    >
      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <Card className="border-slate-200">
          <CardContent className="p-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Study Time</p>
              <h3 className="text-2xl font-bold text-slate-900 mt-1">
                {Math.floor((data?.total_study_minutes || 340) / 60)} hrs {(data?.total_study_minutes || 340) % 60} mins
              </h3>
              <p className="text-xs text-emerald-600 font-medium mt-1">+18% vs last week</p>
            </div>
            <div className="h-11 w-11 rounded-xl bg-purple-100 flex items-center justify-center text-primary-700">
              <Clock className="h-5 w-5" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-slate-200">
          <CardContent className="p-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Retention Score</p>
              <h3 className="text-2xl font-bold text-slate-900 mt-1">
                {data?.retention_score || 94.8}%
              </h3>
              <p className="text-xs text-slate-400 mt-1">Based on SM-2 recall</p>
            </div>
            <div className="h-11 w-11 rounded-xl bg-emerald-100 flex items-center justify-center text-emerald-700">
              <TrendingUp className="h-5 w-5" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-slate-200">
          <CardContent className="p-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Mastered Cards</p>
              <h3 className="text-2xl font-bold text-slate-900 mt-1">
                {data?.flashcards_mastered || 48}
              </h3>
              <p className="text-xs text-slate-400 mt-1">From 3 lecture decks</p>
            </div>
            <div className="h-11 w-11 rounded-xl bg-blue-100 flex items-center justify-center text-blue-700">
              <Layers className="h-5 w-5" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-slate-200">
          <CardContent className="p-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Study Streak</p>
              <h3 className="text-2xl font-bold text-slate-900 mt-1">
                {data?.active_streak_days || 7} Days
              </h3>
              <p className="text-xs text-amber-600 font-medium mt-1">Consistency badge unlocked</p>
            </div>
            <div className="h-11 w-11 rounded-xl bg-amber-100 flex items-center justify-center text-amber-700">
              <Flame className="h-5 w-5" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Two Column Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Weekly Minutes Bar Chart */}
        <Card className="border-slate-200">
          <CardHeader>
            <CardTitle className="text-base flex items-center justify-between">
              <span>Weekly Study Minutes</span>
              <Badge variant="secondary" className="text-xs font-normal">Last 7 Days</Badge>
            </CardTitle>
            <CardDescription>Daily minutes spent reviewing notes & watching lectures</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-72 w-full pt-4">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={weeklyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                  <XAxis dataKey="day" stroke="#94a3b8" fontSize={12} tickLine={false} />
                  <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#0f172a",
                      color: "#fff",
                      borderRadius: "0.5rem",
                      border: "none",
                      fontSize: "12px",
                    }}
                  />
                  <Bar dataKey="minutes" fill="#7C3AED" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Quiz Accuracy Trajectory Line Chart */}
        <Card className="border-slate-200">
          <CardHeader>
            <CardTitle className="text-base flex items-center justify-between">
              <span>Diagnostic Accuracy Trajectory</span>
              <Badge variant="secondary" className="text-xs font-normal">Trailing 4 Weeks</Badge>
            </CardTitle>
            <CardDescription>Average performance across conceptual assessments</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-72 w-full pt-4">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={accuracyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                  <XAxis dataKey="week" stroke="#94a3b8" fontSize={12} tickLine={false} />
                  <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} domain={[60, 100]} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#0f172a",
                      color: "#fff",
                      borderRadius: "0.5rem",
                      border: "none",
                      fontSize: "12px",
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="score"
                    stroke="#10b981"
                    strokeWidth={3}
                    dot={{ fill: "#10b981", r: 4 }}
                    activeDot={{ r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>
    </PageContainer>
  );
};
