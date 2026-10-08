"use client";
import { jsx } from "react/jsx-runtime";
import { forwardRef } from "react";
import { Checkbox as CheckboxPrimitive } from "radix-ui";
import { cn } from "../../utils/index.js";
import { CheckIcon } from "./icons/check.js";
export const Checkbox = forwardRef(function Checkbox2({ className, ...props }, ref) {
  return /* @__PURE__ */ jsx(
    CheckboxPrimitive.Root,
    {
      className: cn(
        "peer flex h-4 w-4 shrink-0 cursor-pointer items-center justify-center border transition-colors outline-none",
        "focus-visible:ring-1 focus-visible:ring-midground/30",
        "disabled:cursor-not-allowed disabled:opacity-50",
        "data-[state=unchecked]:border-midground/20 data-[state=unchecked]:bg-background",
        "data-[state=unchecked]:hover:border-midground/30",
        "data-[state=checked]:border-midground/30 data-[state=checked]:bg-midground/15",
        "data-[state=indeterminate]:border-midground/30 data-[state=indeterminate]:bg-midground/15",
        className
      ),
      ref,
      ...props,
      children: /* @__PURE__ */ jsx(CheckboxPrimitive.Indicator, { className: "flex items-center justify-center text-current", children: /* @__PURE__ */ jsx(CheckIcon, { className: "h-3 w-3 text-midground" }) })
    }
  );
});
