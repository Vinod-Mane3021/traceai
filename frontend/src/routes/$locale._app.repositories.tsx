import { createFileRoute } from "@tanstack/react-router";
import { Topbar } from "@/components/topbar";
import { RepositoryList } from "@/features/repositories/components/repository-list";
import { env } from "@/lib/env";

export const Route = createFileRoute("/$locale/_app/repositories")({
  head: () => ({
    meta: [
      { title: `Repositories — ${env.appName}` },
      { name: "description", content: "Connected GitHub repositories" },
    ],
  }),
  component: RepositoriesPage,
});

function RepositoriesPage() {
  return (
    <>
      <Topbar title="Repositories" subtitle="Connected via GitHub App installations" />
      <main className="mx-auto w-full max-w-7xl flex-1 px-5 py-6 lg:px-8 lg:py-8">
        <RepositoryList />
      </main>
    </>
  );
}
