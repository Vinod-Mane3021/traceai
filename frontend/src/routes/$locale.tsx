import * as React from "react";
import { createFileRoute, Outlet } from "@tanstack/react-router";
import { loadMessages } from "../features/i18n-internationalization/lib/load-messages";
import I18nProvider from "../features/i18n-internationalization/lib/provider";

export const Route = createFileRoute("/$locale")({
  loader: async ({ params }) => {
    const messages = await loadMessages(params.locale);
    return {
      messages,
    };
  },
  component: LocaleLayout,
  errorComponent: ({ error }: { error: any }) => (
    <div className="p-4 border border-red-500 bg-red-50 text-red-900">
      <h1 className="font-bold">Locale Route Error</h1>
      <pre className="text-xs">{error instanceof Error ? error.message : String(error)}</pre>
    </div>
  ),
});

function LocaleLayout() {
  const { locale } = Route.useParams();
  const { messages } = Route.useLoaderData();

  return (
    <I18nProvider locale={locale} messages={messages || {}}>
      <Outlet />
    </I18nProvider>
  );
}
