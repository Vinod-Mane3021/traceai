import { useState, useEffect } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { Topbar } from "@/components/topbar";
import { useRepositories } from "@/features/repositories/api/use-repositories";
import { RuleList } from "@/features/rules/components/rule-list";
import { Skeleton } from "@/components/skeleton-block";
import { env } from "@/lib/env";
import { cn } from "@/lib/utils";
import { Lock, Globe2 } from "lucide-react";

export const Route = createFileRoute("/$locale/_app/rules")({
  head: () => ({
    meta: [
      { title: `Custom rules — ${env.appName}` },
      { name: "description", content: "Manage repository-specific custom security rules" },
    ],
  }),
  component: RulesPage,
});

function RulesPage() {
  const { data: repos, isLoading } = useRepositories();
  const [selected, setSelected] = useState<number | null>(null);

  useEffect(() => {
    if (selected == null && repos && repos.length > 0) {
      setSelected(repos[0].id);
    }
  }, [repos, selected]);

  return (
    <>
      <Topbar title="Custom Rules" subtitle="Per-repository security policies enforced by the scanner" />
      <main className="mx-auto w-full max-w-7xl flex-1 px-5 py-6 lg:px-8 lg:py-8">
        <div className="grid gap-6 lg:grid-cols-[280px_minmax(0,1fr)]">
          <aside className="space-y-2">
            <div className="px-1 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
              Repository
            </div>
            {isLoading || !repos ? (
              <div className="grid gap-2">
                {Array.from({ length: 4 }).map((_, i) => (
                  <Skeleton key={i} className="h-12 w-full" />
                ))}
              </div>
            ) : (
              <div className="grid gap-1">
                {repos.map((repo) => {
                  const active = selected === repo.id;
                  return (
                    <button
                      key={repo.id}
                      onClick={() => setSelected(repo.id)}
                      className={cn(
                        "flex items-center gap-2 rounded-md border px-2.5 py-2 text-left text-sm transition-colors",
                        active
                          ? "border-primary/40 bg-primary/10 text-foreground"
                          : "border-border bg-card hover:bg-accent/40",
                      )}
                    >
                      <img
                        src={repo.owner.avatar_url}
                        alt=""
                        className="h-6 w-6 rounded"
                      />
                      <span className="truncate flex-1">{repo.name}</span>
                      {repo.private ? (
                        <Lock className="h-3 w-3 text-muted-foreground" />
                      ) : (
                        <Globe2 className="h-3 w-3 text-muted-foreground" />
                      )}
                    </button>
                  );
                })}
              </div>
            )}
          </aside>

          <section>
            {selected == null ? (
              <div className="rounded-xl border border-dashed border-border bg-card/40 p-10 text-center">
                <p className="text-sm text-muted-foreground">Select a repository to manage its rules.</p>
              </div>
            ) : (
              <RuleList repositoryId={selected} />
            )}
          </section>
        </div>
      </main>
    </>
  );
}
