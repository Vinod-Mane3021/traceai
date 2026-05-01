import { createFileRoute } from "@tanstack/react-router";
import { Topbar } from "@/components/topbar";
import { useApiInfo } from "@/api/use-api-info";
import { useHealth } from "@/api/use-health";
import { env } from "@/lib/env";

export const Route = createFileRoute("/$locale/_app/settings")({
  head: () => ({ meta: [{ title: `Settings — ${env.appName}` }] }),
  component: SettingsPage,
});

function SettingsPage() {
  const info = useApiInfo();
  const health = useHealth();

  return (
    <>
      <Topbar title="Settings" subtitle="Workspace and connection details" />
      <main className="mx-auto w-full max-w-3xl flex-1 px-5 py-6 lg:px-8 lg:py-8 space-y-4">
        <Card title="Application">
          <Row k="Name" v={env.appName} />
          <Row k="Description" v={env.appDescription} />
          <Row k="Mode" v={env.mockApi ? "Mock data" : "Live API"} />
          <Row k="API base URL" v={env.apiBaseUrl} mono />
        </Card>

        <Card title="Backend">
          <Row k="Service" v={info.data?.name ?? "—"} />
          <Row k="Version" v={info.data?.version ?? "—"} />
          <Row
            k="Health"
            v={
              <span className="inline-flex items-center gap-2">
                <span
                  className={`h-1.5 w-1.5 rounded-full ${
                    health.data?.status === "Healthy" ? "bg-success" : "bg-muted-foreground"
                  }`}
                />
                {health.data?.status ?? "unknown"}
              </span>
            }
          />
        </Card>
      </main>
    </>
  );
}

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-xl border border-border bg-card">
      <div className="border-b border-border px-5 py-3.5">
        <h2 className="text-sm font-semibold tracking-tight">{title}</h2>
      </div>
      <div className="divide-y divide-border">{children}</div>
    </div>
  );
}

function Row({ k, v, mono }: { k: string; v: React.ReactNode; mono?: boolean }) {
  return (
    <div className="flex items-center justify-between px-5 py-3 text-sm">
      <span className="text-muted-foreground">{k}</span>
      <span className={mono ? "font-mono text-xs" : "text-foreground"}>{v}</span>
    </div>
  );
}
