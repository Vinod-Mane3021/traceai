import { useNavigate } from "@/features/i18n-internationalization/lib/navigation";
import { useAuthStore } from "@/features/auth/store/auth-store";
import { LogOut, Sun, Moon } from "lucide-react";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";

export function Topbar({ title, subtitle }: { title: string; subtitle?: string }) {
  const user = useAuthStore((s) => s.user);
  const clear = useAuthStore((s) => s.clearSession);
  const navigate = useNavigate();
  const [dark, setDark] = useState(true);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
  }, [dark]);

  return (
    <header className="sticky top-0 z-10 border-b border-border bg-background/80 backdrop-blur">
      <div className="flex h-14 items-center gap-4 px-5 lg:px-8">
        <div className="min-w-0">
          <h1 className="truncate text-sm font-semibold tracking-tight">{title}</h1>
          {subtitle && (
            <p className="truncate text-xs text-muted-foreground">{subtitle}</p>
          )}
        </div>
        <div className="ml-auto flex items-center gap-2">
          <button
            onClick={() => setDark((d) => !d)}
            className="grid h-8 w-8 place-items-center rounded-md border border-border text-muted-foreground hover:bg-accent hover:text-accent-foreground transition"
            aria-label="Toggle theme"
          >
            {dark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </button>
          {user && (
            <>
              <div className="flex items-center gap-2 rounded-full border border-border bg-card pl-1 pr-3 py-1">
                <img
                  src={user.avatar_url}
                  alt={user.username}
                  className="h-6 w-6 rounded-full"
                />
                <span className="text-xs font-medium">{user.username}</span>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  clear();
                  navigate({ to: "/$locale/login" });
                }}
              >
                <LogOut className="h-4 w-4" />
              </Button>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
