"use client";
import { jsx, jsxs } from "react/jsx-runtime";
import { cn } from "../../utils/index.js";
export function Segmented({
  className,
  onChange,
  options,
  size = "sm",
  value
}) {
  return /* @__PURE__ */ jsx(
    "div",
    {
      className: cn(
        "inline-flex border border-midground/15 bg-background/30",
        className
      ),
      role: "radiogroup",
      children: options.map((opt) => {
        const active = opt.value === value;
        return /* @__PURE__ */ jsx(
          "button",
          {
            "aria-checked": active,
            className: cn(
              "font-mondwest text-display tracking-[0.1em]",
              "transition-colors cursor-pointer whitespace-nowrap",
              "border-r border-midground/15 last:border-r-0",
              "focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-midground/30",
              size === "sm" && "h-7 px-2.5 text-xs",
              size === "md" && "h-8 px-3 text-xs",
              active ? "bg-midground text-background" : "text-text-secondary hover:bg-midground/10 hover:text-midground"
            ),
            onClick: () => onChange(opt.value),
            role: "radio",
            type: "button",
            children: opt.label
          },
          opt.value
        );
      })
    }
  );
}
export function FilterGroup({ children, className, label }) {
  return /* @__PURE__ */ jsxs("div", { className: cn("flex items-center gap-2", className), children: [
    /* @__PURE__ */ jsx("span", { className: "font-mondwest text-display text-xs tracking-[0.12em] text-text-tertiary", children: label }),
    children
  ] });
}
