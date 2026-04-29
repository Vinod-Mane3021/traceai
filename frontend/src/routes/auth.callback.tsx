import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect, useRef } from "react";
import { Loader2, ShieldAlert } from "lucide-react";
import { useGithubCallback } from "@/features/auth/api/use-github-callback";
import { useAuthStore } from "@/features/auth/store/auth-store";

export const Route = createFileRoute("/auth/callback")({
  validateSearch: (search: Record<string, unknown>) => ({
    code: typeof search.code === "string" ? search.code : "",
    installation_id: typeof search.installation_id === "string" ? search.installation_id : undefined,
  }),
  component: CallbackPage,
});

function CallbackPage() {
  const { code, installation_id } = Route.useSearch();
  const navigate = useNavigate();
  const callback = useGithubCallback();
  const { user, setSession, token } = useAuthStore();
  const fired = useRef(false);

  useEffect(() => {
    if (fired.current) return;
    fired.current = true;

    // Case 1: Standard OAuth flow (code present)
    if (code) {
      const redirect_uri = `${window.location.origin}/auth/callback`;
      callback.mutate(
        { code, redirect_uri },
        {
          onSuccess: () => navigate({ to: "/" }),
        },
      );
      return;
    }

    // Case 2: Post-installation redirect (no code, but installation_id present)
    if (installation_id && token && user) {
      // Update the existing session with the new installation_id
      setSession(token, {
        ...user,
        installation_id: parseInt(installation_id, 10),
      });
      navigate({ to: "/repositories" });
      return;
    }

    // Case 3: No recognizable params, or unauthenticated install
    if (!code && !installation_id) {
       navigate({ to: "/login" });
    }
  }, [code, installation_id, callback, navigate, user, setSession, token]);

  return (
    <div className="grid min-h-screen place-items-center bg-background px-4">
      <div className="text-center">
        {callback.isError ? (
          <>
            <ShieldAlert className="mx-auto h-8 w-8 text-destructive" />
            <h1 className="mt-3 text-lg font-semibold">Sign-in failed</h1>
            <p className="mt-1 text-sm text-muted-foreground max-w-sm">
              {(callback.error as Error).message}
            </p>
            <button
              onClick={() => navigate({ to: "/login" })}
              className="mt-5 inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground"
            >
              Back to sign in
            </button>
          </>
        ) : (
          <>
            <Loader2 className="mx-auto h-6 w-6 animate-spin text-primary" />
            <p className="mt-3 text-sm text-muted-foreground">Completing sign-in…</p>
          </>
        )}
      </div>
    </div>
  );
}
