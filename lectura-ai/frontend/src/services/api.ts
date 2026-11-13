import axios from "axios";
import {
  ChatResponse,
  Course,
  Flashcard,
  JobResponse,
  Note,
  PlaylistMetadata,
  Quiz,
  QuizAttempt,
  Transcript,
  TranscriptUploadResponse,
  URLPreviewResponse,
  Video,
} from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 45000,
});

// Interceptor to inject JWT token if stored
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("lectura_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor to gracefully handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      "An unexpected error occurred.";
    console.error("[Lectura API Error]:", message, error.response?.data);
    return Promise.reject(error);
  }
);

// --- API Service Methods ---

// Courses
export const getCourses = async (): Promise<Course[]> => {
  const { data } = await apiClient.get<Course[]>("/courses");
  return data;
};

export const getCourse = async (courseId: string): Promise<Course> => {
  const { data } = await apiClient.get<Course>(`/courses/${courseId}`);
  return data;
};

// Videos
export const processVideo = async (payload: {
  url: string;
  course_id?: string;
  generate_flashcards?: boolean;
  generate_quizzes?: boolean;
}): Promise<JobResponse> => {
  const { data } = await apiClient.post<JobResponse>("/videos/process", payload);
  return data;
};

export const previewYouTubeURL = async (url: string): Promise<URLPreviewResponse> => {
  const { data } = await apiClient.get<URLPreviewResponse>("/videos/preview", {
    params: { url },
  });
  return data;
};

export const getVideo = async (videoId: string): Promise<Video> => {
  const { data } = await apiClient.get<Video>(`/videos/${videoId}`);
  return data;
};

export const getVideoTranscript = async (videoId: string): Promise<Transcript> => {
  const { data } = await apiClient.get<Transcript>(`/videos/${videoId}/transcript`);
  return data;
};

export const uploadTranscript = async (
  videoId: string,
  file: File
): Promise<TranscriptUploadResponse> => {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await apiClient.post<TranscriptUploadResponse>(
    `/videos/${videoId}/transcript/upload`,
    formData,
    {
      headers: { "Content-Type": "multipart/form-data" },
    }
  );
  return data;
};

// Playlists
export const processPlaylist = async (payload: {
  url: string;
  max_videos?: number;
  generate_flashcards?: boolean;
  generate_quizzes?: boolean;
}): Promise<JobResponse> => {
  const { data } = await apiClient.post<JobResponse>("/playlists/process", payload);
  return data;
};

export const previewPlaylistURL = async (url: string): Promise<any> => {
  const { data } = await apiClient.get<any>("/playlists/preview", {
    params: { url },
  });
  return data;
};

// Notes
export const getNotes = async (params?: {
  course_id?: string;
  video_id?: string;
}): Promise<Note[]> => {
  const { data } = await apiClient.get<Note[]>("/notes", { params });
  return data;
};

export const getNote = async (noteId: string): Promise<Note> => {
  const { data } = await apiClient.get<Note>(`/notes/${noteId}`);
  return data;
};

// Quizzes & Flashcards
export const getQuizzes = async (params?: {
  course_id?: string;
  video_id?: string;
}): Promise<Quiz[]> => {
  const { data } = await apiClient.get<Quiz[]>("/quizzes", { params });
  return data;
};

export const getQuiz = async (quizId: string): Promise<Quiz> => {
  const { data } = await apiClient.get<Quiz>(`/quizzes/${quizId}`);
  return data;
};

export const submitQuiz = async (
  quizId: string,
  answers: Record<string, number>
): Promise<QuizAttempt> => {
  const { data } = await apiClient.post<QuizAttempt>(`/quizzes/${quizId}/submit`, {
    answers,
  });
  return data;
};

export const getFlashcards = async (params?: {
  course_id?: string;
  video_id?: string;
}): Promise<Flashcard[]> => {
  const { data } = await apiClient.get<Flashcard[]>("/flashcards", { params });
  return data;
};

export const reviewFlashcard = async (
  flashcardId: string,
  rating: number
): Promise<Flashcard> => {
  const { data } = await apiClient.post<Flashcard>(`/flashcards/${flashcardId}/review`, {
    rating,
  });
  return data;
};

// Jobs
export const getJobStatus = async (jobId: string): Promise<JobResponse> => {
  const { data } = await apiClient.get<JobResponse>(`/jobs/${jobId}`);
  return data;
};

// Progress & Summary
export const getProgressSummary = async (): Promise<any> => {
  const { data } = await apiClient.get<any>("/progress/summary");
  return data;
};

// Chat
export const sendChatMessage = async (payload: {
  message: string;
  video_id?: string;
  course_id?: string;
  history?: any[];
}): Promise<ChatResponse> => {
  const { data } = await apiClient.post<ChatResponse>("/chat", payload);
  return data;
};
