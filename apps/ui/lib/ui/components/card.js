import { jsx } from "react/jsx-runtime";
import { cn } from "../../utils/index.js";
const CARD_STYLE = {
  background: "var(--component-card-background)",
  borderImage: "var(--component-card-border-image)",
  boxShadow: "var(--component-card-box-shadow)",
  clipPath: "var(--component-card-clip-path)"
};
export function Card({
  className,
  style,
  ...props
}) {
  return /* @__PURE__ */ jsx(
    "div",
    {
      className: cn(
        "border border-midground/15 bg-background-base/80 text-midground w-full",
        className
      ),
      style: { ...CARD_STYLE, ...style },
      ...props
    }
  );
}
export function CardHeader({
  className,
  ...props
}) {
  return /* @__PURE__ */ jsx(
    "div",
    {
      className: cn(
        "flex flex-col gap-1.5 p-4 border-b border-midground/15",
        className
      ),
      ...props
    }
  );
}
export function CardTitle({
  className,
  ...props
}) {
  return /* @__PURE__ */ jsx(
    "h3",
    {
      className: cn(
        "font-expanded text-sm font-bold tracking-[0.08em] uppercase",
        className
      ),
      ...props
    }
  );
}
export function CardDescription({
  className,
  ...props
}) {
  return /* @__PURE__ */ jsx(
    "p",
    {
      className: cn("font-mondwest text-xs text-midground/60", className),
      ...props
    }
  );
}
export function CardContent({
  className,
  ...props
}) {
  return /* @__PURE__ */ jsx("div", { className: cn("p-4", className), ...props });
}
