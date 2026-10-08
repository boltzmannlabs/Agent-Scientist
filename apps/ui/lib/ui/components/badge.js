import { jsx } from "react/jsx-runtime";
import { cn } from "../../utils/index.js";
import { BlendMode } from "./blend-mode.js";
const BASE_CN = "inline-flex items-center font-compressed text-display px-2 py-1 leading-none tracking-[0.2em]";
const TONE_CLASSES = {
  destructive: "border border-destructive/30 bg-destructive/15 text-destructive",
  outline: "border border-midground/30 bg-transparent text-midground/80",
  secondary: "border border-midground/15 bg-midground/8 text-midground",
  success: "border border-success/30 bg-success/15 text-success",
  warning: "border border-warning/30 bg-warning/15 text-warning"
};
export const Badge = ({
  className,
  style,
  tone = "default",
  ...props
}) => {
  if (tone === "default") {
    return /* @__PURE__ */ jsx(
      BlendMode,
      {
        as: "span",
        background: "mg/0.075",
        className: cn(BASE_CN, className),
        color: "mg",
        style: { opacity: "var(--midground-alpha)", ...style },
        ...props
      }
    );
  }
  return /* @__PURE__ */ jsx(
    "span",
    {
      className: cn(BASE_CN, TONE_CLASSES[tone], className),
      style,
      ...props
    }
  );
};
