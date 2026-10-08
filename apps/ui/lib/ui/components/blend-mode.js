"use client";
import { Fragment, jsx } from "react/jsx-runtime";
import { useStore } from "@nanostores/react";
import { createElement, useMemo } from "react";
import { getControlAtom } from "../../hooks/use-smooth-controls.js";
import { cn, polyRef } from "../../utils/index.js";
import { colorDodge, colorMix } from "../../utils/color.js";
const LAYER_KEYS = { bg: "bgColor", fg: "fgColor", mg: "mgColor" };
const parseSpec = (spec) => {
  const [layer, alpha] = spec.split("/");
  return [layer, alpha ? parseFloat(alpha) : void 0];
};
const useControlColor = (key, fallback) => {
  const atom = getControlAtom("Lens", key);
  return (atom ? useStore(atom) : void 0) ?? fallback;
};
const useBlend = (against, spec) => {
  const layerKey = spec?.split("/")[0];
  const isLayerSpec = layerKey && layerKey in LAYER_KEYS;
  const [target, alpha] = isLayerSpec ? parseSpec(spec) : [void 0, void 0];
  const againstColor = useControlColor(LAYER_KEYS[against], "#041c1c");
  const fgColor = useControlColor(LAYER_KEYS.fg, "#ffe6cb");
  const mgColor = useControlColor(LAYER_KEYS.mg, "#ffe6cb");
  const bgColor = useControlColor(LAYER_KEYS.bg, "#ffe6cb");
  const targetColor = target ? target === "fg" ? fgColor : target === "mg" ? mgColor : bgColor : spec;
  return useMemo(() => {
    if (!spec || !targetColor) {
      return void 0;
    }
    const result = colorDodge(againstColor, targetColor);
    return alpha != null ? colorMix(result, alpha) : result;
  }, [spec, againstColor, targetColor, alpha]);
};
export const useBlendMode = (opts = {}) => {
  const { against = "bg", background, color } = opts;
  return {
    backgroundColor: useBlend(against, background),
    color: useBlend(against, color)
  };
};
export const withBlendMode = (Component, opts) => {
  const Wrapped = (props) => {
    const { against, background, color, ...rest } = props;
    const colors = useBlendMode({
      against: against ?? opts?.against,
      background: background ?? opts?.background,
      color: color ?? opts?.color
    });
    return /* @__PURE__ */ jsx(Component, { ...rest, ...colors });
  };
  Wrapped.displayName = `withBlendMode(${Component.displayName ?? Component.name ?? "Component"})`;
  return Wrapped;
};
export const BlendMode = polyRef(
  ({ against, as, background, children, className, color, style, ...rest }, ref) => {
    const colors = useBlendMode({ against, background, color });
    if (typeof children === "function") {
      return /* @__PURE__ */ jsx(Fragment, { children: children(colors) });
    }
    return createElement(as ?? "div", {
      ...rest,
      children,
      className: cn(className),
      ref,
      style: { ...colors, ...style }
    });
  }
);
