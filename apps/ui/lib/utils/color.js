export const hexToRgb = (hex) => [
  parseInt(hex.slice(1, 3), 16),
  parseInt(hex.slice(3, 5), 16),
  parseInt(hex.slice(5, 7), 16)
];
export const rgbToHex = (r, g, b) => `#${[r, g, b].map((v) => v.toString(16).padStart(2, "0")).join("")}`;
export const colorDodge = (base, blend) => {
  const [br, bg, bb] = hexToRgb(base);
  const [lr, lg, lb] = hexToRgb(blend);
  const d = (b, l) => l === 255 ? 255 : Math.min(255, Math.floor(b * 255 / (255 - l)));
  return rgbToHex(d(br, lr), d(bg, lg), d(bb, lb));
};
export const colorMix = (color, alpha) => `color-mix(in srgb, ${color} ${Math.round(alpha * 100)}%, transparent)`;
