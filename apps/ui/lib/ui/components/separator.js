import { jsx } from "react/jsx-runtime";
import { cn } from "../../utils/index.js";
export function Separator({
  className,
  orientation = "horizontal",
  ...props
}) {
  return /* @__PURE__ */ jsx(
    "div",
    {
      "aria-orientation": orientation,
      role: "separator",
      className: cn(
        "shrink-0 bg-midground/15",
        orientation === "horizontal" ? "h-px w-full" : "h-full w-px",
        className
      ),
      ...props
    }
  );
}
