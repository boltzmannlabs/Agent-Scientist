import { jsx } from "react/jsx-runtime";
import { cn } from "../../utils/index.js";
export function Input({
  className,
  ...props
}) {
  return /* @__PURE__ */ jsx(
    "input",
    {
      className: cn(
        "flex h-9 w-full border border-midground/15 bg-background/40 px-3 py-1 font-courier text-sm transition-colors",
        "placeholder:text-midground/50",
        "focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-midground/30 focus-visible:border-midground/25",
        "disabled:cursor-not-allowed disabled:opacity-50",
        className
      ),
      ...props
    }
  );
}
