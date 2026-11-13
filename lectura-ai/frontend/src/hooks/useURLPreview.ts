import { useState, useEffect } from "react";
import { previewYouTubeURL } from "../services/api";
import { URLPreviewResponse } from "../types";

const YT_REGEX = /(?:youtube\.com\/(?:watch\?v=|embed\/|v\/|shorts\/|live\/|playlist\?list=)|youtu\.be\/)([a-zA-Z0-9_-]{11}|(?:[a-zA-Z0-9_-]+))/i;

export function useURLPreview(url: string, debounceMs: number = 800) {
  const [debouncedUrl, setDebouncedUrl] = useState<string>(url.trim());
  const [preview, setPreview] = useState<URLPreviewResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Debounce the input URL
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedUrl(url.trim());
    }, debounceMs);

    return () => clearTimeout(handler);
  }, [url, debounceMs]);

  // Fetch preview when debounced URL is valid-looking
  useEffect(() => {
    if (!debouncedUrl) {
      setPreview(null);
      setError(null);
      setIsLoading(false);
      return;
    }

    if (!YT_REGEX.test(debouncedUrl)) {
      setPreview(null);
      setError("Please enter a valid YouTube video or playlist link.");
      setIsLoading(false);
      return;
    }

    let isMounted = true;
    setIsLoading(true);
    setError(null);

    previewYouTubeURL(debouncedUrl)
      .then((data) => {
        if (!isMounted) return;
        setPreview(data);
        if (!data.valid && data.error) {
          setError(data.error);
        } else {
          setError(null);
        }
      })
      .catch((err: any) => {
        if (!isMounted) return;
        const msg = err.response?.data?.detail || err.message || "Failed to fetch YouTube preview.";
        setError(msg);
        setPreview(null);
      })
      .finally(() => {
        if (isMounted) {
          setIsLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [debouncedUrl]);

  return {
    preview,
    isLoading,
    error,
    isValid: Boolean(preview?.valid),
  };
}
