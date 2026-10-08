"use client";
import { jsx } from "react/jsx-runtime";
import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { cn } from "../../utils/index.js";
export function Toast({ toast }) {
  const [visible, setVisible] = useState(false);
  const [current, setCurrent] = useState(toast);
  useEffect(() => {
    if (toast) {
      setCurrent(toast);
      setVisible(true);
    } else {
      setVisible(false);
      const timer = setTimeout(() => setCurrent(null), 200);
      return () => clearTimeout(timer);
    }
  }, [toast]);
  if (!current || typeof document === "undefined") return null;
  return createPortal(
    /* @__PURE__ */ jsx(
      "div",
      {
        "aria-live": "polite",
        className: cn(
          "fixed top-16 right-4 z-50 border px-4 py-2.5 font-courier text-xs tracking-wider uppercase backdrop-blur-sm",
          current.type === "success" ? "bg-success/15 text-success border-success/30" : "bg-destructive/15 text-destructive border-destructive/30"
        ),
        role: "status",
        style: {
          animation: visible ? "toast-in 200ms ease-out forwards" : "toast-out 200ms ease-in forwards"
        },
        children: current.message
      }
    ),
    document.body
  );
}
