"use client";
import { jsx } from "react/jsx-runtime";
import { forwardRef } from "react";
import { cn } from "../../utils/index.js";
export const ListItem = forwardRef(
  function ListItem2({ active = false, children, className, type = "button", ...props }, ref) {
    return /* @__PURE__ */ jsx(
      "button",
      {
        className: cn(
          "group relative flex w-full items-center gap-2 px-3 py-2 text-left",
          "font-courier text-sm transition-colors cursor-pointer",
          "focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-midground/30",
          "disabled:cursor-not-allowed disabled:text-text-disabled",
          active ? "bg-midground/10 text-midground" : "text-text-secondary hover:text-midground hover:bg-midground/5",
          className
        ),
        "data-active": active || void 0,
        ref,
        type,
        ...props,
        children
      }
    );
  }
);
