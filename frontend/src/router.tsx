import { createRouter, useRouter } from "@tanstack/react-router";
import { QueryClientProvider } from "@tanstack/react-query";
import { routeTree } from "./routeTree.gen";
import { getQueryClient } from "./lib/query-client";
import * as React from "react";
import { Trans } from "@/features/i18n-internationalization/components/trans";

function DefaultErrorComponent({ error, reset }: { error: Error; reset: () => void }) {
  const router = useRouter();
  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="max-w-md text-center">
        <h1 className="text-2xl font-bold tracking-tight text-foreground">
          <Trans i18nKey="common:errors.something_went_wrong" />
        </h1>
        <p className="mt-2 text-sm text-muted-foreground">
          {error.message || <Trans i18nKey="common:errors.unexpected_error" />}
        </p>
        <div className="mt-6 flex items-center justify-center gap-3">
          <button
            onClick={() => {
              router.invalidate();
              reset();
            }}
            className="inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:opacity-90 transition"
          >
            <Trans i18nKey="common:actions.try_again" />
          </button>
          <a
            href="/"
            className="inline-flex items-center justify-center rounded-md border border-input bg-background px-4 py-2 text-sm font-medium hover:bg-accent transition"
          >
            <Trans i18nKey="common:actions.go_home" />
          </a>
        </div>
      </div>
    </div>
  );
}

export const getRouter = () => {
  const queryClient = getQueryClient();
  const router = createRouter({
    routeTree,
    context: {
      queryClient,
    },
    scrollRestoration: true,
    defaultPreloadStaleTime: 0,
    defaultErrorComponent: DefaultErrorComponent,
    Wrap: ({ children }) => <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>,
  });
  return router;
};
