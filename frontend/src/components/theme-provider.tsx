import { useRouter } from "@tanstack/react-router";
import { createContext, type PropsWithChildren, use } from "react";
import { setThemeServerFn, type Theme } from "@/lib/theme";

type ThemeContextVal = { theme: Theme; setTheme: (val: Theme) => void };
const ThemeContext = createContext<ThemeContextVal | null>(null);

export function ThemeProvider({ children, theme }: PropsWithChildren<{ theme: Theme }>) {
  const router = useRouter();

  function setTheme(val: Theme) {
    setThemeServerFn({ data: val }).then(() => router.invalidate());
  }

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const val = use(ThemeContext);
  if (!val) throw new Error("useTheme called outside of ThemeProvider!");
  return val;
}
