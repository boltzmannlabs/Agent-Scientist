"use client";
import { jsx, jsxs } from "react/jsx-runtime";
import { Dialog as DialogPrimitive } from "radix-ui";
import { cn } from "../../utils/index.js";
function Dialog({ ...props }) {
  return /* @__PURE__ */ jsx(DialogPrimitive.Root, { "data-slot": "dialog", ...props });
}
function DialogTrigger({ ...props }) {
  return /* @__PURE__ */ jsx(DialogPrimitive.Trigger, { "data-slot": "dialog-trigger", ...props });
}
function DialogPortal({ ...props }) {
  return /* @__PURE__ */ jsx(DialogPrimitive.Portal, { "data-slot": "dialog-portal", ...props });
}
function DialogClose({ ...props }) {
  return /* @__PURE__ */ jsx(DialogPrimitive.Close, { "data-slot": "dialog-close", ...props });
}
function DialogOverlay({
  className,
  ...props
}) {
  return /* @__PURE__ */ jsx(
    DialogPrimitive.Overlay,
    {
      className: cn(
        "fixed inset-0 z-50",
        "bg-black/60 backdrop-blur-sm",
        "data-[state=open]:animate-in data-[state=open]:fade-in-0",
        "data-[state=closed]:animate-out data-[state=closed]:fade-out-0",
        className
      ),
      "data-slot": "dialog-overlay",
      ...props
    }
  );
}
function DialogContent({
  className,
  children,
  showCloseButton = true,
  ...props
}) {
  return /* @__PURE__ */ jsxs(DialogPortal, { children: [
    /* @__PURE__ */ jsx(DialogOverlay, {}),
    /* @__PURE__ */ jsxs(
      DialogPrimitive.Content,
      {
        className: cn(
          "fixed top-1/2 left-1/2 z-50 -translate-x-1/2 -translate-y-1/2",
          "grid w-full max-w-md gap-0",
          "border border-midground/15 bg-background-base text-foreground-base shadow-lg outline-none",
          "data-[state=open]:animate-in data-[state=open]:fade-in-0 data-[state=open]:zoom-in-95",
          "data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95",
          "duration-150",
          className
        ),
        "data-slot": "dialog-content",
        ...props,
        children: [
          children,
          showCloseButton && /* @__PURE__ */ jsxs(
            DialogPrimitive.Close,
            {
              className: cn(
                "absolute top-3 right-3",
                "flex h-6 w-6 items-center justify-center",
                "text-midground/50 transition-colors hover:text-midground",
                "focus:outline-none focus-visible:ring-1 focus-visible:ring-midground/30",
                "disabled:pointer-events-none"
              ),
              "data-slot": "dialog-close",
              children: [
                /* @__PURE__ */ jsx(XIcon, { className: "h-3.5 w-3.5" }),
                /* @__PURE__ */ jsx("span", { className: "sr-only", children: "Close" })
              ]
            }
          )
        ]
      }
    )
  ] });
}
function DialogHeader({ className, ...props }) {
  return /* @__PURE__ */ jsx(
    "div",
    {
      className: cn(
        "flex flex-col gap-1 p-4 border-b border-midground/15",
        className
      ),
      "data-slot": "dialog-header",
      ...props
    }
  );
}
function DialogFooter({ className, ...props }) {
  return /* @__PURE__ */ jsx(
    "div",
    {
      className: cn(
        "flex items-center justify-end gap-2 p-3",
        className
      ),
      "data-slot": "dialog-footer",
      ...props
    }
  );
}
function DialogTitle({
  className,
  ...props
}) {
  return /* @__PURE__ */ jsx(
    DialogPrimitive.Title,
    {
      className: cn(
        "font-expanded text-sm font-bold tracking-[0.08em] uppercase",
        className
      ),
      "data-slot": "dialog-title",
      ...props
    }
  );
}
function DialogDescription({
  className,
  ...props
}) {
  return /* @__PURE__ */ jsx(
    DialogPrimitive.Description,
    {
      className: cn(
        "font-mondwest text-xs text-midground/60 leading-relaxed",
        className
      ),
      "data-slot": "dialog-description",
      ...props
    }
  );
}
function XIcon({ className }) {
  return /* @__PURE__ */ jsxs(
    "svg",
    {
      "aria-hidden": true,
      className,
      fill: "none",
      stroke: "currentColor",
      strokeLinecap: "round",
      strokeLinejoin: "round",
      strokeWidth: 2,
      viewBox: "0 0 24 24",
      children: [
        /* @__PURE__ */ jsx("line", { x1: "18", x2: "6", y1: "6", y2: "18" }),
        /* @__PURE__ */ jsx("line", { x1: "6", x2: "18", y1: "6", y2: "18" })
      ]
    }
  );
}
export {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogOverlay,
  DialogPortal,
  DialogTitle,
  DialogTrigger
};
