import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AppLayout } from "./components/layout/AppLayout";
import { LandingPage } from "./pages/LandingPage";
import { DashboardPage } from "./pages/DashboardPage";
import { ImportPage } from "./pages/ImportPage";
import { CoursePage } from "./pages/CoursePage";
import { NotesPage } from "./pages/NotesPage";
import { VideoNotesPage } from "./pages/VideoNotesPage";
import { ChatPage } from "./pages/ChatPage";
import { FlashcardsPage } from "./pages/FlashcardsPage";
import { QuizPage } from "./pages/QuizPage";
import { AnalyticsPage } from "./pages/AnalyticsPage";

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Landing Page */}
        <Route path="/" element={<LandingPage />} />

        {/* Protected App Workspace Layout */}
        <Route element={<AppLayout />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/import" element={<ImportPage />} />
          <Route path="/courses" element={<DashboardPage />} />
          <Route path="/courses/:courseId" element={<CoursePage />} />
          <Route path="/notes" element={<NotesPage />} />
          <Route path="/video-notes" element={<VideoNotesPage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/flashcards" element={<FlashcardsPage />} />
          <Route path="/quizzes" element={<QuizPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
