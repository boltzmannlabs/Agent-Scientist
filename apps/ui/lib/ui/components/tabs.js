"use client";
import { jsx } from "react/jsx-runtime";
import {
  useState
} from "react";
import { cn } from "../../utils/index.js";
export function Tabs({ children, className, defaultValue }) {
  const [active, setActive] = useState(defaultValue);
  return /* @__PURE__ */ jsx("div", { className: cn("flex flex-col gap-4", className), children: children(active, setActive) });
}
export function TabsList({ className, ...props }) {
  return /* @__PURE__ */ jsx(
    "div",
    {
      className: cn(
        "inline-flex h-9 items-center justify-start border-b border-midground/15 text-text-secondary",
        className
      ),
      ...props
    }
  );
}
export function TabsTrigger({
  active,
  className,
  value: _value,
  ...props
}) {
  return /* @__PURE__ */ jsx(
    "button",
    {
      className: cn(
        "relative inline-flex items-center justify-center whitespace-nowrap px-3 py-1.5",
        "font-mondwest text-display text-xs tracking-[0.1em] transition-all cursor-pointer",
        "focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-midground/30",
        active ? "text-midground after:absolute after:bottom-0 after:left-0 after:right-0 after:h-px after:bg-midground" : "text-text-secondary hover:text-midground",
        className
      ),
      type: "button",
      ...props
    }
  );
}
