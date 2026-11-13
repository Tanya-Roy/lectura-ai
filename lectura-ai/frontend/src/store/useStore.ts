import { create } from "zustand";
import { Course, JobResponse, User, Video } from "../types";

interface AppState {
  // Current session & auth
  currentUser: User | null;
  setCurrentUser: (user: User | null) => void;

  // Selected entities
  activeCourse: Course | null;
  setActiveCourse: (course: Course | null) => void;
  activeVideo: Video | null;
  setActiveVideo: (video: Video | null) => void;

  // Background active job
  activeJob: JobResponse | null;
  setActiveJob: (job: JobResponse | null) => void;

  // Navigation & UI state
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;
}

export const useStore = create<AppState>((set) => ({
  currentUser: {
    id: "usr_demo_lectura_101",
    email: "student@lectura.ai",
    full_name: "Alex Academic",
    role: "user",
    is_active: true,
    created_at: new Date().toISOString(),
  },
  setCurrentUser: (user) => set({ currentUser: user }),

  activeCourse: null,
  setActiveCourse: (course) => set({ activeCourse: course }),

  activeVideo: null,
  setActiveVideo: (video) => set({ activeVideo: video }),

  activeJob: null,
  setActiveJob: (job) => set({ activeJob: job }),

  sidebarOpen: true,
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
}));
