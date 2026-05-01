import { createFileRoute } from "@tanstack/react-router";
import { Topbar } from "@/components/topbar";
import { StatCard } from "@/components/stat-card";
import { GitBranch, ShieldAlert, FileSearch, AlertOctagon, ListChecks } from "lucide-react";
import { useAnalyticsOverview } from "@/features/analytics/api/use-analytics-overview";
import { VulnerabilityFeed } from "@/features/analytics/components/vulnerability-feed";
import { Skeleton } from "@/components/skeleton-block";
import { env } from "@/lib/env";
import { Trans } from "@/features/i18n-internationalization/components/trans";

export const Route = createFileRoute("/$locale/_app/")({
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

  const criticalCount =
    data?.severity_distribution.find((d) => d.severity.toUpperCase() === "CRITICAL")?.count ?? 0;

  return (
    <>
      <Topbar
        title={<Trans i18nKey="analytics:overview.title" />}
        subtitle={<Trans i18nKey="analytics:overview.subtitle" />}
      />
      <main className="mx-auto w-full max-w-7xl flex-1 px-5 py-6 lg:px-8 lg:py-8">
        <section className="grid grid-cols-2 lg:grid-cols-5 gap-3 lg:gap-4">
          {isLoading || !data ? (
            Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-28 rounded-xl" />)
          ) : (
            <>
              <StatCard
                index={0}
                label={<Trans i18nKey="analytics:overview.repos_label" />}
                value={data.summary.total_repos_monitored}
                icon={GitBranch}
                hint={<Trans i18nKey="analytics:overview.repos_hint" />}
              />
              <StatCard
                index={1}
                label={<Trans i18nKey="analytics:overview.vuln_label" />}
                value={data.summary.total_vulnerabilities}
                icon={ShieldAlert}
                hint={<Trans i18nKey="analytics:overview.vuln_hint" />}
              />
              <StatCard
                index={2}
                label={<Trans i18nKey="analytics:overview.open_label" />}
                value={data.summary.open_vulnerabilities}
                icon={ListChecks}
                tone="warning"
                hint={<Trans i18nKey="analytics:overview.open_hint" />}
              />
              <StatCard
                index={3}
                label={<Trans i18nKey="analytics:overview.critical_label" />}
                value={criticalCount}
                icon={AlertOctagon}
                tone="critical"
                hint={<Trans i18nKey="analytics:overview.critical_hint" />}
              />
              <StatCard
                index={4}
                label={<Trans i18nKey="analytics:overview.scanned_prs_label" />}
                value={data.summary.total_prs_scanned}
                icon={FileSearch}
                tone="success"
                hint={<Trans i18nKey="analytics:overview.scanned_prs_hint" />}
              />
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

