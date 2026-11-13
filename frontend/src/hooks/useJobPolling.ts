import { useState, useEffect } from "react";
import { getJobStatus } from "../services/api";
import { JobResponse } from "../types";

export function useJobPolling(jobId: string | null, intervalMs: number = 1500) {
  const [job, setJob] = useState<JobResponse | null>(null);
  const [isPolling, setIsPolling] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) {
      setJob(null);
      setIsPolling(false);
      setError(null);
      return;
    }

    let isMounted = true;
    setIsPolling(true);
    setError(null);

    const poll = async () => {
      try {
        const data = await getJobStatus(jobId);
        if (!isMounted) return;

        setJob(data);

        if (data.status === "completed" || data.status === "failed") {
          setIsPolling(false);
        }
      } catch (err: any) {
        if (!isMounted) return;
        const msg = err.response?.data?.detail || err.message || "Failed to poll job status";
        setError(msg);
        setIsPolling(false);
      }
    };

    // First check immediately
    poll();

    const timer = setInterval(() => {
      if (job?.status === "completed" || job?.status === "failed") {
        clearInterval(timer);
        return;
      }
      poll();
    }, intervalMs);

    return () => {
      isMounted = false;
      clearInterval(timer);
    };
  }, [jobId, intervalMs]);

  const isComplete = job?.status === "completed";
  const isFailed = job?.status === "failed";

  return {
    job,
    isPolling,
    isComplete,
    isFailed,
    error,
  };
}
