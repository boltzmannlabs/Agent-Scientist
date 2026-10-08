"use client";
import { jsx, jsxs } from "react/jsx-runtime";
import { useCallback, useState } from "react";
import { cn } from "../../utils/index.js";
import { Small } from "./typography/small.js";
export function CopyButton({
  children,
  className,
  copiedLabel = "Copied!",
  label = "Copy",
  resetDelayMs = 2e3,
  text
}) {
  const [copied, setCopied] = useState(false);
  const handleCopy = useCallback(() => {
    void navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), resetDelayMs);
    });
  }, [resetDelayMs, text]);
  return /* @__PURE__ */ jsx(
    "button",
    {
      className: cn(
        "font-courier text-display cursor-pointer border-none bg-transparent text-xs",
        "tracking-widest",
        "hover:text-midground tap-highlight-transparent transition-colors",
        "flex items-center justify-center",
        copied ? "text-midground" : "text-text-secondary",
        className
      ),
      onClick: handleCopy,
      type: "button",
      children: children ?? (copied ? copiedLabel : label)
    }
  );
}
export function CommandBlock({ className, code, label }) {
  return /* @__PURE__ */ jsxs("div", { className: cn("flex flex-col gap-1", className), children: [
    /* @__PURE__ */ jsxs("div", { className: "flex items-center justify-between", children: [
      /* @__PURE__ */ jsx(Small, { className: "opacity-50", children: label }),
      /* @__PURE__ */ jsx(CopyButton, { text: code })
    ] }),
    /* @__PURE__ */ jsx(
      "div",
      {
        className: cn(
          "bg-background/40 font-courier border border-current/20",
          "px-3 py-2 text-[0.6875rem] leading-relaxed lowercase"
        ),
        children: /* @__PURE__ */ jsx("code", { className: "break-all", children: code })
      }
    )
  ] });
}
