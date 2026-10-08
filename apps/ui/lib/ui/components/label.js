import { jsx } from "react/jsx-runtime";
import { cn } from "../../utils/index.js";
export function Label({
  className,
  ...props
}) {
  return /* @__PURE__ */ jsx(
    "label",
    {
      className: cn(
        "font-mondwest text-xs tracking-[0.1em] uppercase leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70",
        className
      ),
      ...props
    }
  );
}
