import { jsx } from "react/jsx-runtime";
import { forwardRef } from "react";
import { Typography } from "./index.js";
export const Small = forwardRef(
  (props, ref) => {
    return /* @__PURE__ */ jsx(Typography, { as: "small", mondwest: true, variant: "sm", ...{ ref, ...props } });
  }
);
