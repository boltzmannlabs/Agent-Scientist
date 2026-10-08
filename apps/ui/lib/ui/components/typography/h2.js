import { jsx } from "react/jsx-runtime";
import { forwardRef } from "react";
import { cn } from "../../../utils/index.js";
import { Typography } from "./index.js";
export const H2 = forwardRef(
  ({ className, ...props }, ref) => {
    return /* @__PURE__ */ jsx(
      Typography,
      {
        as: "h2",
        className: cn("font-bold", className),
        variant: "lg",
        ...{ ref, ...props }
      }
    );
  }
);
