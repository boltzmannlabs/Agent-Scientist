"use client";
import gsap from "gsap";
import { buttonGroup, useControls } from "leva";
import { atom } from "nanostores";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
const atomRegistry = /* @__PURE__ */ new Map();
const val = (v) => v && typeof v === "object" && "value" in v ? v.value : v;
const isHex = (v) => /color/i.test(v?.type) || /^#[0-9a-f]{3,8}$/i.test(val(v));
const randHex = () => `#${Math.floor(Math.random() * 16777215).toString(16).padStart(6, "0")}`;
const randNum = (v) => typeof v === "object" && ("min" in v || "max" in v) ? gsap.utils.random(v.min ?? 0, v.max ?? 1, v.step ?? 0.01) : gsap.utils.random(0, 1);
export function useSmoothControls(label, initialArgs, options, dependencies) {
  const entries = useMemo(
    () => Object.entries(initialArgs ?? {}),
    [initialArgs]
  );
  const values = useMemo(
    () => entries.filter(([, v]) => !/button|folder/i.test(v?.type)),
    [entries]
  );
  const mountedRef = useRef(false);
  const atoms = useMemo(() => {
    const map = atomRegistry.get(label) ?? /* @__PURE__ */ new Map();
    if (!atomRegistry.has(label)) {
      atomRegistry.set(label, map);
    }
    const freshMount = !mountedRef.current;
    entries.forEach(([k, v]) => {
      if (v?.schema) {
        Object.keys(v.schema).forEach((sk) => {
          const key = `${k}.${sk}`;
          if (!map.has(key)) {
            map.set(key, atom(val(v.schema[sk])));
          } else if (freshMount) {
            map.get(key).set(val(v.schema[sk]));
          }
        });
      } else if (!map.has(k)) {
        map.set(k, atom(val(v)));
      } else if (freshMount) {
        map.get(k).set(val(v));
      }
    });
    return map;
  }, [label, entries]);
  useEffect(() => {
    mountedRef.current = true;
  }, []);
  const hydrate = useCallback(
    () => Object.fromEntries(
      entries.flatMap(
        ([k, v]) => v?.schema ? Object.entries(v.schema).map(([k0, v0]) => [
          k0,
          atoms.get(`${k}.${k0}`)?.get() ?? val(v0)
        ]) : [[k, atoms.get(k)?.get() ?? val(v)]]
      )
    ),
    [entries, atoms]
  );
  const [args, update] = useState(hydrate);
  const setRef = useRef(null);
  const atomVals = useRef({});
  const fromAtom = useRef(false);
  const fromControl = useRef(/* @__PURE__ */ new Set());
  useEffect(() => {
    if (Object.keys(args).length !== Object.keys(initialArgs).length) {
      update(hydrate);
    }
  }, [initialArgs, args]);
  useEffect(() => {
    if (!setRef.current) {
      return;
    }
    const unsubs = [];
    let ready = false;
    const initTimeout = setTimeout(() => ready = true, 100);
    const subscribe = (fullKey, updateFn) => {
      const a = atoms.get(fullKey);
      if (!a) {
        return;
      }
      unsubs.push(
        a.subscribe((v) => {
          const prev = atomVals.current[fullKey];
          atomVals.current[fullKey] = v;
          if (setRef.current && ready && prev !== v && !fromControl.current.has(fullKey)) {
            fromAtom.current = true;
            try {
              updateFn(v);
            } catch {
            }
            setTimeout(() => fromAtom.current = false, 0);
          }
        })
      );
      atomVals.current[fullKey] = a.get();
    };
    entries.forEach(([k, v]) => {
      if (v?.schema) {
        Object.keys(v.schema).forEach((sk) => {
          subscribe(`${k}.${sk}`, (v2) => {
            try {
              setRef.current({
                [k]: { ...args[k] ?? {}, [sk]: v2 }
              });
            } catch {
            }
            update((st) => ({
              ...st,
              [k]: { ...st[k] ?? {}, [sk]: v2 }
            }));
          });
        });
      } else {
        subscribe(k, (v2) => {
          try {
            setRef.current({ [k]: v2 });
          } catch {
          }
          update((st) => ({ ...st, [k]: v2 }));
        });
      }
    });
    return () => {
      clearTimeout(initTimeout);
      unsubs.forEach((fn) => fn());
    };
  }, [label, entries, atoms, args]);
  const onChange = (k, orig) => (e, k0) => {
    if (fromAtom.current) {
      return orig?.(e, k0);
    }
    const key = k0?.split(".")?.pop() ?? k;
    const fullKey = k0 ?? k;
    const a = atoms.get(fullKey);
    fromControl.current.add(fullKey);
    const sync = (v) => {
      update((st) => ({ ...st, [key]: v }));
      a?.set(v);
      orig?.(v, k0);
    };
    if (typeof e === "number" && args[key] !== e) {
      gsap.to(args, {
        duration: options?.duration ?? 0.35,
        ease: "circ.out",
        [key]: e,
        onComplete: () => void fromControl.current.delete(fullKey),
        onUpdate: () => {
          fromControl.current.add(fullKey);
          sync(args[key]);
          setTimeout(() => fromControl.current.delete(fullKey), 0);
        }
      });
    } else {
      sync(e);
      setTimeout(() => fromControl.current.delete(fullKey), 0);
    }
  };
  const [, set] = useControls(
    label,
    () => ({
      ...Object.fromEntries(
        entries.map(
          ([k, v]) => v?.schema ? [
            k,
            {
              ...v,
              schema: Object.fromEntries(
                Object.entries(v.schema).map(([sk, sv]) => [
                  sk,
                  { ...sv, onChange: onChange(k, sv?.onChange) }
                ])
              )
            }
          ] : [k, { ...v, onChange: onChange(k, v?.onChange) }]
        )
      ),
      " ": buttonGroup({
        flatten: () => void set(Object.fromEntries(values.map(([k]) => [k, 0]))),
        randomize: () => {
          set(
            Object.fromEntries(
              values.map(([k, v]) => [k, isHex(v) ? randHex() : randNum(v)])
            )
          );
          options?.onRandomize?.();
        },
        reset: () => {
          set(Object.fromEntries(values.map(([k, v]) => [k, val(v)])));
          options?.onReset?.();
        }
      })
    }),
    { collapsed: true, ...options },
    dependencies ?? []
  );
  setRef.current = set;
  return args;
}
export const getControlAtom = (label, key) => atomRegistry.get(label)?.get(key);
export const setControlValue = (label, key, value, options) => {
  const a = getControlAtom(label, key);
  if (!a) {
    return;
  }
  if (options?.animate && typeof value === "number" && typeof a.get() === "number") {
    const t = { v: a.get() };
    gsap.to(t, {
      duration: options.duration ?? 0.35,
      ease: "circ.out",
      onUpdate: () => a.set(t.v),
      v: value
    });
  } else {
    a.set(value);
  }
};
