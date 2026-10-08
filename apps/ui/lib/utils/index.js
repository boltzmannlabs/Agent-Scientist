import { clsx } from "clsx";
import sanitize from "sanitize-html";
import { twMerge } from "tailwind-merge";
import * as THREE from "three";
import { hexToRgb, rgbToHex } from "./color.js";
import { polyRef } from "./poly.js";
export { hexToRgb, polyRef, rgbToHex };
export const cn = (...inputs) => twMerge(clsx(inputs));
export const clamp = (v, min = 0, max = 1) => Math.min(max, Math.max(min, Number.isFinite(v) ? v : min));
export const smoothstep = (edge0, edge1, x) => {
  const t = clamp((x - edge0) / (edge1 - edge0));
  return t * t * (3 - 2 * t);
};
export const hexToVec3 = (hex) => {
  const [r, g, b] = hexToRgb(hex);
  return new THREE.Vector3(r / 255, g / 255, b / 255);
};
export const truncate = (text, options) => text.length > options.length ? `${text.slice(0, options.length)}...` : text;
export const stripWpStyles = (html) => sanitize(html, {
  allowedAttributes: {
    a: ["href", "target", "rel", "name"],
    audio: ["src", "controls"],
    iframe: ["src", "width", "height", "frameborder", "allowfullscreen"],
    img: ["src", "alt", "width", "height", "loading"],
    source: ["src", "type", "srcset"],
    td: ["colspan", "rowspan"],
    th: ["colspan", "rowspan"],
    video: ["src", "controls", "width", "height", "poster"]
  },
  allowedIframeHostnames: [
    "www.youtube.com",
    "youtube.com",
    "player.vimeo.com"
  ],
  allowedSchemes: ["http", "https", "mailto"],
  allowedTags: [
    ...sanitize.defaults.allowedTags,
    "img",
    "figure",
    "figcaption",
    "iframe",
    "video",
    "audio",
    "source",
    "picture"
  ]
});
