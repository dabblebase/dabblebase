import { useEffect, useRef } from "react";

export function useFocusOnCondition<T extends HTMLElement>(condition: boolean) {
  const ref = useRef<T>(null);

  useEffect(() => {
    if (condition && ref.current) {
      ref.current.focus();
      if (ref.current instanceof HTMLInputElement) {
        ref.current.select();
      }
    }
  }, [condition]);

  return ref;
}
