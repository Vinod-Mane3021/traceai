import * as React from "react";
import { Outlet, Link, createRootRoute, HeadContent, Scripts } from "@tanstack/react-router";
import appCss from "../styles.css?url";
import { getThemeServerFn } from "@/lib/theme";
import { ThemeProvider } from "@/components/theme-provider";
import { Trans } from "@/features/i18n-internationalization/components/trans";

const APP_NAME = "Trace.ai";
const APP_DESCRIPTION = "AI-powered security scanning for GitHub PRs";

function NotFoundComponent() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="max-w-md text-center">
        <h1 className="text-7xl font-bold text-foreground">
          <Trans i18nKey="common:not_found.title" />
        </h1>
        <h2 className="mt-4 text-xl font-semibold text-foreground">
          <Trans i18nKey="common:not_found.subtitle" />
        </h2>
        <p className="mt-2 text-sm text-muted-foreground">
          <Trans i18nKey="common:not_found.description" />
        </p>
        <div className="mt-6">
          <Link
            to="/$locale"
            params={{ locale: "en" }}
            className="inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:opacity-90 transition"
          >
            <Trans i18nKey="common:actions.go_home" />
          </Link>
        </div>
      </div>
    </div>
  );
}

export const Route = createRootRoute({
  loader: async () => {
    return {
      theme: await getThemeServerFn(),
    };
  },
  errorComponent: ({ error }) => (
    <div className="p-10 text-red-500">
      <h1 className="text-xl font-bold">
        <Trans i18nKey="common:errors.something_went_wrong" />
      </h1>
      <pre>{error.message}</pre>
    </div>
  ),
  head: () => ({
    meta: [
      { charSet: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      { title: `${APP_NAME} — ${APP_DESCRIPTION}` },
      { name: "description", content: APP_DESCRIPTION },
      { property: "og:title", content: APP_NAME },
      { property: "og:description", content: APP_DESCRIPTION },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary" },
    ],
    links: [
      { rel: "stylesheet", href: appCss },
      { rel: "preconnect", href: "https://fonts.googleapis.com" },
      { rel: "preconnect", href: "https://fonts.gstatic.com", crossOrigin: "anonymous" },
      {
        rel: "stylesheet",
        href: "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap",
      },
    ],
  }),
  shellComponent: RootShell,
  component: RootComponent,
  notFoundComponent: NotFoundComponent,
});

function RootShell({ children }: { children: React.ReactNode }) {
  const { theme } = Route.useLoaderData();

  return (
    <html lang="en" className={theme} suppressHydrationWarning>
      <head>
        <HeadContent />
      </head>
      <body>
        <ThemeProvider theme={theme}>{children}</ThemeProvider>
        <Scripts />
      </body>
    </html>
  );
}

function RootComponent() {
  return <Outlet />;
}
