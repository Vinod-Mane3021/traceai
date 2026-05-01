import { createFileRoute } from "@tanstack/react-router";
import { Topbar } from "@/components/topbar";
import { VulnerabilityFeed } from "@/features/analytics/components/vulnerability-feed";
import { env } from "@/lib/env";

export const Route = createFileRoute("/$locale/_app/vulnerabilities")({
  head: () => ({
    meta: [
      { title: `Vulnerabilities — ${env.appName}` },
      { name: "description", content: "All security findings" },
    ],
  }),
  component: VulnerabilitiesPage,
});

function VulnerabilitiesPage() {
  return (
    <>
      <Topbar title="Vulnerabilities" subtitle="All security findings across repositories" />
      <main className="mx-auto w-full max-w-7xl flex-1 px-5 py-6 lg:px-8 lg:py-8">
        <VulnerabilityFeed limit={20} />
      </main>
    </>
  );
}
