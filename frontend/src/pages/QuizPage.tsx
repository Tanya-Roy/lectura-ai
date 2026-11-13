import React, { useState, useEffect } from "react";
import {
  HelpCircle,
  CheckCircle2,
  XCircle,
  RotateCcw,
  Clock,
  ArrowRight,
  Award,
  Sparkles,
} from "lucide-react";
import { PageContainer } from "../components/layout/PageContainer";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Progress } from "../components/ui/progress";
import { getQuiz, submitQuiz } from "../services/api";
import { Quiz, QuizQuestion } from "../types";

export const QuizPage: React.FC = () => {
  const [quiz, setQuiz] = useState<Quiz | null>(null);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, number>>({});
  const [submitted, setSubmitted] = useState(false);
  const [score, setScore] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchQuizData = async () => {
      try {
        const data = await getQuiz("qz_101");
        setQuiz(data);
      } catch (err) {
        console.error("Failed to load quiz:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchQuizData();
  }, []);

  const handleSelect = (questionId: string, optionIndex: number) => {
    if (submitted) return; // Prevent changing after submit
    setSelectedAnswers((prev) => ({
      ...prev,
      [questionId]: optionIndex,
    }));
  };

  const handleSubmit = async () => {
    if (!quiz) return;
    try {
      const result = await submitQuiz(quiz.id, selectedAnswers);
      setScore(result.score_percentage);
      setSubmitted(true);
    } catch (err) {
      console.error("Quiz submission error:", err);
      // Fallback calculation locally
      let correct = 0;
      quiz.questions.forEach((q) => {
        if (selectedAnswers[q.id] === q.correct_option_index) correct++;
      });
      setScore(Math.round((correct / quiz.questions.length) * 100));
      setSubmitted(true);
    }
  };

  const handleRetake = () => {
    setSelectedAnswers({});
    setSubmitted(false);
    setScore(null);
  };

  const totalQuestions = quiz?.questions.length || 0;
  const answeredCount = Object.keys(selectedAnswers).length;

  return (
    <PageContainer
      title={quiz?.title || "Mastery Check: Convex Optimization"}
      subtitle={quiz?.description || "3 rigorous diagnostic questions testing your conceptual comprehension."}
      action={
        submitted && (
          <Button variant="outline" size="sm" onClick={handleRetake} className="gap-1.5">
            <RotateCcw className="h-4 w-4" /> Retake Assessment
          </Button>
        )
      }
    >
      <div className="max-w-3xl mx-auto space-y-8">
        {/* Score Banner when submitted */}
        {submitted && score !== null && (
          <Card className="border-primary-200 bg-gradient-to-r from-primary-50 to-purple-50 p-6 shadow-sm">
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-center sm:text-left">
              <div className="flex items-center gap-4">
                <div className="h-14 w-14 rounded-2xl bg-primary-700 text-white flex items-center justify-center font-extrabold text-xl shadow-md">
                  {score}%
                </div>
                <div>
                  <h3 className="text-lg font-bold text-slate-900">
                    {score >= 80 ? "Superb Academic Mastery! 🎉" : "Good Attempt! Keep Practicing"}
                  </h3>
                  <p className="text-xs text-slate-600 mt-0.5">
                    Review the detailed solutions and timestamp references below.
                  </p>
                </div>
              </div>
              <Button size="sm" onClick={handleRetake} className="gap-2 shrink-0">
                <RotateCcw className="h-4 w-4" /> Try Again
              </Button>
            </div>
          </Card>
        )}

        {/* Question List */}
        <div className="space-y-6">
          {quiz?.questions.map((q: QuizQuestion, index: number) => {
            const isAnswered = selectedAnswers[q.id] !== undefined;
            const chosenOption = selectedAnswers[q.id];
            const isCorrect = chosenOption === q.correct_option_index;

            return (
              <Card
                key={q.id}
                className={`border-2 transition-all ${
                  submitted
                    ? isCorrect
                      ? "border-emerald-300 bg-emerald-50/20"
                      : "border-red-300 bg-red-50/20"
                    : "border-slate-200 bg-white"
                }`}
              >
                <CardContent className="p-6 space-y-4">
                  <div className="flex items-start justify-between gap-4">
                    <span className="text-xs font-bold uppercase tracking-wider text-primary-700">
                      Question {index + 1} of {totalQuestions}
                    </span>
                    {submitted && (
                      <Badge variant={isCorrect ? "success" : "destructive"} className="text-xs">
                        {isCorrect ? "Correct" : "Incorrect"}
                      </Badge>
                    )}
                  </div>

                  <h3 className="text-base font-semibold text-slate-900 leading-snug">
                    {q.question_text}
                  </h3>

                  {/* Options List */}
                  <div className="space-y-2.5 pt-2">
                    {q.options.map((opt: string, optIdx: number) => {
                      const isSelected = chosenOption === optIdx;
                      const isOptionCorrect = q.correct_option_index === optIdx;

                      let btnStyle = "border-slate-200 hover:bg-slate-50 text-slate-700";
                      if (submitted) {
                        if (isOptionCorrect) {
                          btnStyle = "border-emerald-500 bg-emerald-50 text-emerald-900 font-semibold";
                        } else if (isSelected && !isCorrect) {
                          btnStyle = "border-red-500 bg-red-50 text-red-900 line-through";
                        }
                      } else if (isSelected) {
                        btnStyle = "border-primary-600 bg-primary-50 text-primary-900 font-medium";
                      }

                      return (
                        <div
                          key={optIdx}
                          onClick={() => handleSelect(q.id, optIdx)}
                          className={`p-3.5 rounded-xl border text-sm cursor-pointer transition-all flex items-center justify-between ${btnStyle}`}
                        >
                          <span>{opt}</span>
                          {submitted && isOptionCorrect && (
                            <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0" />
                          )}
                          {submitted && isSelected && !isCorrect && (
                            <XCircle className="h-4 w-4 text-red-600 shrink-0" />
                          )}
                        </div>
                      );
                    })}
                  </div>

                  {/* Explanation & Timestamp Reference */}
                  {submitted && q.explanation && (
                    <div className="mt-4 p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700 space-y-1.5">
                      <span className="font-bold text-slate-900 block">Explanation:</span>
                      <p className="leading-relaxed">{q.explanation}</p>
                      {q.timestamp_reference && (
                        <div className="pt-1 flex items-center gap-1.5 text-primary-700 font-medium">
                          <Clock className="h-3.5 w-3.5" />
                          <span>
                            Timestamp citation: {Math.floor(q.timestamp_reference / 60)}:
                            {Math.floor(q.timestamp_reference % 60) < 10 ? "0" : ""}
                            {Math.floor(q.timestamp_reference % 60)} in lecture
                          </span>
                        </div>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Submit Action */}
        {!submitted && (
          <div className="sticky bottom-6 flex justify-end">
            <Button
              size="lg"
              disabled={answeredCount === 0}
              onClick={handleSubmit}
              className="gap-2 px-8 shadow-lg shadow-primary-700/20"
            >
              <span>Submit Assessment ({answeredCount}/{totalQuestions})</span>
              <ArrowRight className="h-4 w-4" />
            </Button>
          </div>
        )}
      </div>
    </PageContainer>
  );
};
