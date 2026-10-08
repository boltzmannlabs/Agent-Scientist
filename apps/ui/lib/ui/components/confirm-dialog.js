"use client";
import { jsx, jsxs } from "react/jsx-runtime";
import { useRef } from "react";
import { AlertDialog as AlertDialogPrimitive } from "radix-ui";
import { cn } from "../../utils/index.js";
import { Button } from "./button.js";
function WarningTriangle({ className }) {
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
        /* @__PURE__ */ jsx("path", { d: "m10.29 3.86-8.16 14a2 2 0 0 0 1.73 3h16.28a2 2 0 0 0 1.73-3l-8.16-14a2 2 0 0 0-3.46 0z" }),
        /* @__PURE__ */ jsx("line", { x1: "12", x2: "12", y1: "9", y2: "13" }),
        /* @__PURE__ */ jsx("line", { x1: "12", x2: "12.01", y1: "17", y2: "17" })
      ]
    }
  );
}
export function ConfirmDialog({
  cancelLabel = "Cancel",
  confirmLabel = "Confirm",
  description,
  destructive = false,
  loading = false,
  onCancel,
  onConfirm,
  open,
  title
}) {
  const confirmedRef = useRef(false);
  return /* @__PURE__ */ jsx(
    AlertDialogPrimitive.Root,
    {
      onOpenChange: (v) => {
        if (!v && !confirmedRef.current) onCancel();
        confirmedRef.current = false;
      },
      open,
      children: /* @__PURE__ */ jsxs(AlertDialogPrimitive.Portal, { children: [
        /* @__PURE__ */ jsx(
          AlertDialogPrimitive.Overlay,
          {
            className: cn(
              "fixed inset-0 z-50",
              "bg-black/60 backdrop-blur-sm",
              "data-[state=open]:animate-in data-[state=open]:fade-in-0",
              "data-[state=closed]:animate-out data-[state=closed]:fade-out-0"
            )
          }
        ),
        /* @__PURE__ */ jsxs(
          AlertDialogPrimitive.Content,
          {
            className: cn(
              "fixed top-1/2 left-1/2 z-50 -translate-x-1/2 -translate-y-1/2",
              "w-[calc(100%-2rem)] max-w-md",
              "border border-midground/15 bg-background-base text-foreground-base shadow-lg outline-none",
              "data-[state=open]:animate-in data-[state=open]:fade-in-0 data-[state=open]:zoom-in-95",
              "data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95",
              "duration-150"
            ),
            children: [
              /* @__PURE__ */ jsxs("div", { className: "flex items-start gap-3 p-4 border-b border-midground/15", children: [
                destructive && /* @__PURE__ */ jsx("div", { "aria-hidden": true, className: "mt-0.5 shrink-0 text-destructive", children: /* @__PURE__ */ jsx(WarningTriangle, { className: "h-4 w-4" }) }),
                /* @__PURE__ */ jsxs("div", { className: "flex-1 min-w-0 flex flex-col gap-1", children: [
                  /* @__PURE__ */ jsx(
                    AlertDialogPrimitive.Title,
                    {
                      className: "font-expanded text-sm font-bold tracking-[0.08em] uppercase",
                      children: title
                    }
                  ),
                  description && /* @__PURE__ */ jsx(
                    AlertDialogPrimitive.Description,
                    {
                      className: "font-mondwest text-xs text-midground/60 leading-relaxed",
                      children: description
                    }
                  )
                ] })
              ] }),
              /* @__PURE__ */ jsxs("div", { className: "flex items-center justify-end gap-2 p-3", children: [
                /* @__PURE__ */ jsx(AlertDialogPrimitive.Cancel, { asChild: true, children: /* @__PURE__ */ jsx(Button, { disabled: loading, outlined: true, type: "button", children: cancelLabel }) }),
                /* @__PURE__ */ jsx(AlertDialogPrimitive.Action, { asChild: true, children: /* @__PURE__ */ jsx(
                  Button,
                  {
                    destructive,
                    disabled: loading,
                    onClick: () => {
                      confirmedRef.current = true;
                      onConfirm();
                    },
                    type: "button",
                    children: loading ? "\u2026" : confirmLabel
                  }
                ) })
              ] })
            ]
          }
        )
      ] })
    }
  );
}
