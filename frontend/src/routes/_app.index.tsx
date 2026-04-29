import { createFileRoute } from "@tanstack/react-router";
import { Topbar } from "@/components/topbar";
import { StatCard } from "@/components/stat-card";
import { GitBranch, ShieldAlert, FileSearch, AlertOctagon, ListChecks } from "lucide-react";
import { useAnalyticsOverview } from "@/features/analytics/api/use-analytics-overview";
import { VulnerabilityFeed } from "@/features/analytics/components/vulnerability-feed";
import { Skeleton } from "@/components/skeleton-block";
import { env } from "@/lib/env";

export const Route = createFileRoute("/_app/")({
  head: () => ({
    meta: [
      { title: `Overview — ${env.appName}` },
      { name: "description", content: "Security overview dashboard" },
    ],
  }),
  component: OverviewPage,
});

function OverviewPage() {
  const { data, isLoading } = useAnalyticsOverview();

  return (
    <>
      <Topbar title="Overview" subtitle="Security signals across all connected repositories" />
      <main className="mx-auto w-full max-w-7xl flex-1 px-5 py-6 lg:px-8 lg:py-8">
        <section className="grid grid-cols-2 lg:grid-cols-5 gap-3 lg:gap-4">
          {isLoading || !data ? (
            Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-28 rounded-xl" />)
          ) : (
            <>
              <StatCard index={0} label="Repositories" value={data.total_repositories} icon={GitBranch} hint="Connected" />
              <StatCard index={1} label="Vulnerabilities" value={data.total_vulnerabilities} icon={ShieldAlert} hint="All-time" />
              <StatCard index={2} label="Open" value={data.open_vulnerabilities} icon={ListChecks} tone="warning" hint="Need attention" />
              <StatCard index={3} label="Critical" value={data.critical_vulnerabilities} icon={AlertOctagon} tone="critical" hint="Highest priority" />
              <StatCard index={4} label="Scanned PRs" value={data.scanned_prs} icon={FileSearch} tone="success" hint="Past 30 days" />
            </>
          )}
        </section>

        <section className="mt-8">
          <VulnerabilityFeed limit={8} />
        </section>
      </main>
    </>
  );
}
