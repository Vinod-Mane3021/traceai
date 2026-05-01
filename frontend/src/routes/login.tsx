import * as React from "react";
import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useEffect } from "react";
import { Github, ShieldCheck, Sparkles, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/features/auth/store/auth-store";
import { useGithubCallback } from "@/features/auth/api/use-github-callback";
import { env } from "@/lib/env";

export const Route = createFileRoute("/login")({
  head: () => ({
    meta: [
      { title: `Sign in — ${env.appName}` },
      { name: "description", content: `Sign in to ${env.appName}` },
    ],
  }),
  component: LoginPage,
});

function LoginPage() {
  const token = useAuthStore((s) => s.token);
  const navigate = useNavigate();
  const callback = useGithubCallback();

  useEffect(() => {
    if (token) navigate({ to: "/" });
  }, [token, navigate]);

  const handleSignIn = () => {
    if (env.mockApi || !env.githubClientId) {
      // Demo / mock path
      callback.mutate(
        { code: "mock-code", redirect_uri: `${window.location.origin}/auth/callback` },
        {
          onSuccess: () => navigate({ to: "/" }),
        },
      );
      return;
    }
    const redirect = `${window.location.origin}/auth/callback`;
    const url = `https://github.com/login/oauth/authorize?client_id=${env.githubClientId}&redirect_uri=${encodeURIComponent(redirect)}&scope=read:user`;
    window.location.href = url;
  };

  return (
    <div className="relative min-h-screen overflow-hidden bg-background">
      <div className="pointer-events-none absolute inset-0 grid-bg opacity-40" />
      <div
        className="pointer-events-none absolute -top-40 left-1/2 h-[520px] w-[820px] -translate-x-1/2 rounded-full blur-3xl"
        style={{
          background:
            "radial-gradient(closest-side, color-mix(in oklab, var(--primary) 35%, transparent), transparent)",
        }}
      />

      <div className="relative mx-auto grid min-h-screen w-full max-w-6xl grid-cols-1 lg:grid-cols-2">
        {/* Brand panel */}
        <div className="hidden lg:flex flex-col justify-between p-10">
          <Link to="/" className="flex items-center gap-2 w-fit">
            <div className="grid h-9 w-9 place-items-center rounded-md bg-primary/15 text-primary ring-1 ring-primary/30">
              <span className="font-mono text-sm font-bold">T</span>
            </div>
            <div className="leading-tight">
              <div className="text-sm font-semibold">{env.appName}</div>
              <div className="text-[11px] text-muted-foreground">
                security console
              </div>
            </div>
          </Link>

          <div className="space-y-6 max-w-md">
            <h2 className="text-3xl font-semibold tracking-tight">
              Catch vulnerabilities <span className="text-primary">before</span> they ship.
            </h2>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Trace.ai connects to your GitHub installations and runs AI-powered security analysis on every pull request — surfacing critical issues with the context your team actually needs.
            </p>
            <ul className="space-y-3 text-sm">
              <li className="flex items-start gap-3">
                <ShieldCheck className="h-4 w-4 mt-0.5 text-primary" />
                Continuous security scanning
              </li>
              <li className="flex items-start gap-3">
                <Sparkles className="h-4 w-4 mt-0.5 text-primary" />
                AI-powered vulnerability insights
              </li>
              <li className="flex items-start gap-3">
                <Zap className="h-4 w-4 mt-0.5 text-primary" />
                Automated SOC2 compliance reports
              </li>
            </ul>
          </div>

          <p className="text-xs text-muted-foreground">
            © {new Date().getFullYear()} {env.appName}
          </p>
        </div>

        {/* Form panel */}
        <div className="flex items-center justify-center p-6 sm:p-10">
          <div className="w-full max-w-sm rounded-2xl border border-border bg-card p-7 shadow-2xl shadow-black/30">
            <div className="lg:hidden mb-6 flex items-center gap-2">
              <div className="grid h-8 w-8 place-items-center rounded-md bg-primary/15 text-primary ring-1 ring-primary/30">
                <span className="font-mono text-sm font-bold">T</span>
              </div>
              <span className="text-sm font-semibold">{env.appName}</span>
            </div>
            <h1 className="text-xl font-semibold tracking-tight">
              Welcome back
            </h1>
            <p className="mt-1 text-sm text-muted-foreground">
              Connect your GitHub account to get started.
            </p>

            <Button className="mt-6 w-full h-10" onClick={handleSignIn} disabled={callback.isPending}>
              <Github className="h-4 w-4" />
              <span className="ml-2">
                {callback.isPending ? "Signing in..." : "Continue with GitHub"}
              </span>
            </Button>

            {callback.isError && (
              <p className="mt-3 text-xs text-destructive">{(callback.error as Error).message}</p>
            )}

            <p className="mt-6 text-[11px] leading-relaxed text-muted-foreground">
              By signing in, you agree to allow Trace.ai to access your GitHub account (read:user).
            </p>

            {env.mockApi && (
              <div className="mt-5 rounded-md border border-border bg-muted/40 px-3 py-2 text-[11px] text-muted-foreground">
                Note: Running in mock mode. Any GitHub account will work.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

