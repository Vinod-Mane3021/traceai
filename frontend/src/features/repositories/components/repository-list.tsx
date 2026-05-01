import { useRepositories } from "../api/use-repositories";
import { useSoc2PdfReport } from "@/features/analytics/api/use-soc2-pdf";
import { Skeleton } from "@/components/skeleton-block";
import { Lock, Globe2, Download, ExternalLink, Loader2 } from "lucide-react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { env } from "@/lib/env";

export function RepositoryList() {
  const { data, isLoading, isError } = useRepositories();
  const pdf = useSoc2PdfReport();

  if (isLoading) {
    return (
      <div className="grid gap-3">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-20 w-full" />
        ))}
      </div>
    );
  }
  if (isError) {
    return (
      <p className="text-sm text-destructive">
        Failed to load repositories.
      </p>
    );
  }

  if (data?.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-border bg-muted/30 p-12 text-center">
        <div className="grid h-12 w-12 place-items-center rounded-full bg-primary/10 text-primary">
          <Globe2 className="h-6 w-6" />
        </div>
        <h3 className="mt-4 text-base font-semibold">
          No repositories connected
        </h3>
        <p className="mt-2 max-w-xs text-sm text-muted-foreground">
          Install the Trace.ai GitHub App to start monitoring your repositories.
        </p>
        <Button className="mt-6" asChild>
          <a href={env.githubPublicLink} target="_blank" rel="noreferrer">
            Install GitHub App
          </a>
        </Button>
      </div>
    );
  }

  return (
    <div className="grid gap-3">
      {data?.map((repo, i) => (
        <motion.div
          key={repo.id}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.04 }}
          className="rounded-xl border border-border bg-card p-4 sm:p-5 hover:border-primary/40 transition-colors"
        >
          <div className="flex items-start gap-4">
            <img src={repo.owner.avatar_url} alt={repo.owner.login} className="h-9 w-9 rounded-md" />
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <h3 className="truncate text-sm font-semibold">{repo.full_name}</h3>
                <span className="inline-flex items-center gap-1 rounded-full border border-border bg-muted/50 px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide text-muted-foreground">
                  {repo.private ? <Lock className="h-3 w-3" /> : <Globe2 className="h-3 w-3" />}
                  {repo.private ? "Private" : "Public"}
                </span>
              </div>
              {repo.description && (
                <p className="mt-1 text-sm text-muted-foreground truncate">{repo.description}</p>
              )}
            </div>
            <div className="flex items-center gap-2">
              <a
                href={repo.html_url}
                target="_blank"
                rel="noreferrer"
                className="grid h-8 w-8 place-items-center rounded-md border border-border text-muted-foreground hover:bg-accent hover:text-accent-foreground transition"
                aria-label="Open on GitHub"
              >
                <ExternalLink className="h-4 w-4" />
              </a>
              <Button
                size="sm"
                variant="outline"
                onClick={() => pdf.mutate(repo.id)}
                disabled={pdf.isPending && pdf.variables === repo.id}
              >
                {pdf.isPending && pdf.variables === repo.id ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Download className="h-4 w-4" />
                )}
                <span className="ml-1.5 hidden sm:inline">
                  SOC2 PDF
                </span>
              </Button>
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  );
}

