import React, { useState, useEffect } from "react";
import {
  RotateCcw,
  Sparkles,
  ChevronLeft,
  ChevronRight,
  Layers,
  CheckCircle2,
  HelpCircle,
  Flame,
} from "lucide-react";
import { PageContainer } from "../components/layout/PageContainer";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Progress } from "../components/ui/progress";
import { getFlashcards, reviewFlashcard } from "../services/api";
import { Flashcard } from "../types";

export const FlashcardsPage: React.FC = () => {
  const [cards, setCards] = useState<Flashcard[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [loading, setLoading] = useState(true);
  const [completed, setCompleted] = useState(false);

  useEffect(() => {
    const fetchDeck = async () => {
      try {
        const data = await getFlashcards();
        setCards(data);
      } catch (err) {
        console.error("Failed to load flashcards:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchDeck();
  }, []);

  const handleNext = () => {
    setIsFlipped(false);
    if (currentIndex < cards.length - 1) {
      setCurrentIndex((prev) => prev + 1);
    } else {
      setCompleted(true);
    }
  };

  const handleRate = async (rating: number) => {
    const currentCard = cards[currentIndex];
    if (currentCard) {
      try {
        await reviewFlashcard(currentCard.id, rating);
      } catch (err) {
        console.error("Review rating error:", err);
      }
    }
    handleNext();
  };

  const handleReset = () => {
    setCurrentIndex(0);
    setIsFlipped(false);
    setCompleted(false);
  };

  const currentCard = cards[currentIndex];
  const progressPct = cards.length > 0 ? ((currentIndex + 1) / cards.length) * 100 : 0;

  return (
    <PageContainer
      title="Spaced-Repetition Flashcards"
      subtitle="Supercharge active recall with SM-2 spaced intervals."
      action={
        <Button variant="outline" size="sm" onClick={handleReset} className="gap-1.5">
          <RotateCcw className="h-4 w-4" /> Restart Deck
        </Button>
      }
    >
      <div className="max-w-2xl mx-auto space-y-6">
        {/* Progress Bar & Index */}
        <div className="space-y-2">
          <div className="flex justify-between text-xs font-semibold text-slate-600">
            <span>
              Card {cards.length > 0 ? currentIndex + 1 : 0} of {cards.length}
            </span>
            <span>{Math.round(progressPct)}% Completed</span>
          </div>
          <Progress value={progressPct} className="h-2" />
        </div>

        {/* Deck Completed View */}
        {completed ? (
          <Card className="border-slate-200 text-center p-12 bg-white shadow-sm space-y-4">
            <div className="h-16 w-16 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto">
              <CheckCircle2 className="h-8 w-8" />
            </div>
            <h3 className="text-2xl font-bold text-slate-900">Deck Review Complete!</h3>
            <p className="text-sm text-slate-600 max-w-sm mx-auto">
              Great session! All cards have been scheduled according to your retention ratings.
            </p>
            <div className="pt-4 flex justify-center gap-3">
              <Button onClick={handleReset} variant="outline" className="gap-2">
                <RotateCcw className="h-4 w-4" /> Practice Again
              </Button>
              <Button onClick={() => (window.location.href = "/quizzes")} className="gap-2">
                <HelpCircle className="h-4 w-4" /> Take Quiz
              </Button>
            </div>
          </Card>
        ) : currentCard ? (
          /* Interactive Flip Card */
          <div className="space-y-6">
            <div
              onClick={() => setIsFlipped(!isFlipped)}
              className="cursor-pointer select-none perspective-1000 min-h-[300px] sm:min-h-[340px]"
            >
              <Card
                className={`relative w-full h-full min-h-[300px] sm:min-h-[340px] p-8 flex flex-col justify-between transition-all duration-300 border-2 ${
                  isFlipped
                    ? "border-primary-400 bg-purple-50/40 shadow-md"
                    : "border-slate-200 bg-white hover:border-slate-300 shadow-sm"
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <Badge variant="outline" className="text-xs">
                      {currentCard.topic || "Core Concept"}
                    </Badge>
                    <span className="text-[11px] font-semibold text-slate-400">
                      {isFlipped ? "Answer" : "Question (Click to flip)"}
                    </span>
                  </div>

                  <h3 className="text-lg sm:text-xl font-bold text-slate-900 leading-snug">
                    {isFlipped ? currentCard.back : currentCard.front}
                  </h3>
                </div>

                <div className="pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-400">
                  <span>Difficulty: Level {currentCard.difficulty || 2}</span>
                  <span className="text-primary-700 font-semibold flex items-center gap-1">
                    <RotateCcw className="h-3 w-3" /> Flip card
                  </span>
                </div>
              </Card>
            </div>

            {/* SM-2 Recall Rating Buttons */}
            {isFlipped ? (
              <div className="space-y-2">
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block text-center">
                  How well did you recall this?
                </span>
                <div className="grid grid-cols-4 gap-2.5">
                  <Button
                    variant="outline"
                    onClick={() => handleRate(1)}
                    className="border-red-200 hover:bg-red-50 text-red-700 font-medium"
                  >
                    1: Again
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => handleRate(2)}
                    className="border-amber-200 hover:bg-amber-50 text-amber-700 font-medium"
                  >
                    2: Hard
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => handleRate(3)}
                    className="border-blue-200 hover:bg-blue-50 text-blue-700 font-medium"
                  >
                    3: Good
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => handleRate(5)}
                    className="border-emerald-200 hover:bg-emerald-50 text-emerald-700 font-medium"
                  >
                    4: Easy
                  </Button>
                </div>
              </div>
            ) : (
              <div className="flex justify-center">
                <Button onClick={() => setIsFlipped(true)} size="lg" className="w-full max-w-sm">
                  Show Answer
                </Button>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-12 text-slate-400 text-sm">
            No flashcards available. Ingest a lecture to generate a deck.
          </div>
        )}
      </div>
    </PageContainer>
  );
};
