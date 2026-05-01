import { Moon, Sun } from "lucide-react";
import { useTheme } from "./theme-provider";

export const ThemeToggle = () => {
  const { theme, setTheme } = useTheme();
  return (
    <button
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
      className="grid h-8 w-8 cursor-pointer place-items-center rounded-md border border-border text-muted-foreground hover:bg-accent hover:text-accent-foreground transition"
      aria-label="Toggle theme"
    >
      {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
    </button>
  );
};
