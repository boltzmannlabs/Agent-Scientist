"use client";
import { useCallback, useEffect, useRef, useState } from "react";
export function useToast(duration = 3e3) {
  const [toast, setToast] = useState(null);
  const timerRef = useRef(null);
  useEffect(() => {
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, []);
  const showToast = useCallback(
    (message, type) => {
      if (timerRef.current) clearTimeout(timerRef.current);
      setToast({ message, type });
      timerRef.current = setTimeout(() => setToast(null), duration);
    },
    [duration]
  );
  return { showToast, toast };
}
