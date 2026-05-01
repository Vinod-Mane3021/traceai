import { useNavigate } from "@tanstack/react-router";
import { useAuthStore } from "@/features/auth/store/auth-store";
import { LogOut } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "./theme-toggle";
import { GoogleTranslateSelector } from "@/features/google-internationalization/components/google-translate-selector";

export function Topbar({ title, subtitle }: { title: React.ReactNode; subtitle?: React.ReactNode }) {
  const user = useAuthStore((s) => s.user);
  const clear = useAuthStore((s) => s.clearSession);
  const navigate = useNavigate();

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
          <GoogleTranslateSelector />
          <ThemeToggle />
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
                  navigate({ to: "/login" });
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
