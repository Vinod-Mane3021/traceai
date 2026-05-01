# Setting up Internationalization (i18n) in TanStack Start

This guide explains how to implement a robust, URL-based internationalization system in a TanStack Start application, following the architecture used in this project.

## Architecture Overview

The implementation follows these principles:
- **URL-based Routing**: The locale is part of the URL (e.g., `/en/dashboard`, `/es/dashboard`).
- **Shared Configuration**: Centralized definition of supported locales and routing rules.
- **Lazy-loaded Namespaces**: Translation messages are split into namespaces (e.g., `common`, `auth`, `billing`) and loaded only when needed.
- **Type-safe Translations**: (Optional but recommended) using TypeScript to ensure keys exist.

---

## Step 1: Directory Structure

Organize your i18n logic into a shared package (if using a monorepo) or a dedicated directory in your app.

```text
features/i18n-internationalization/
├── lib/
│   ├── locales.ts         # Supported locales definition
│   ├── routing.ts         # Routing configuration
│   ├── load-messages.ts   # Logic to fetch JSON messages
│   └── provider.tsx       # React Context Provider
├── messages/              # Translation files
│   ├── en/
│   │   ├── common.json
│   │   └── auth.json
│   └── es/
│       ├── common.json
│       └── auth.json

```

---

## Step 2: Define Locales and Routing

Create a centralized configuration for your locales.

```typescript
// features/i18n-internationalization/lib/locales.ts
export const locales = ['en', 'es', 'fr'] as const;
export type Locale = (typeof locales)[number];
export const defaultLocale: Locale = 'en';

// features/i18n-internationalization/lib/routing.ts
export const routing = {
  locales,
  defaultLocale,
  localePrefix: 'as-needed', // 'always' or 'as-needed'
};
```

---

## Step 3: Translation Messages

Split your translations into logical namespaces.

**Example: `features/i18n-internationalization/messages/en/common.json`**
```json
{
  "greeting": "Hello, {name}!",
  "actions": {
    "save": "Save",
    "cancel": "Cancel"
  }
}
```

---

## Step 4: Implement Message Loading

Create a utility to load messages dynamically. In TanStack Start, you can use `import.meta.glob` (if using Vite) to load these files.

```typescript
// features/i18n-internationalization/lib/load-messages.ts
import { Locale } from './locales';

export async function loadMessages(locale: string) {
  const namespaces = ['common', 'auth', 'account'];
  const messages: Record<string, any> = {};

  await Promise.all(
    namespaces.map(async (ns) => {
      try {
        // Example for Vite/TanStack Start
        const module = await import(`../messages/${locale}/${ns}.json`);
        messages[ns] = module.default;
      } catch (e) {
        console.warn(`Failed to load namespace ${ns} for locale ${locale}`);
      }
    })
  );

  return messages;
}
```

---

## Step 5: TanStack Start Route Integration

In TanStack Start, you should wrap your routes with a `$locale` parameter.

### 1. Root Route Configuration

Modify your root route to handle the locale parameter and provide it to the context.

```typescript
// app/routes/__root.tsx
import { createRootRouteWithContext } from '@tanstack/react-router';
import { I18nProvider } from '@kit/i18n/provider';

interface MyRouterContext {
  locale: string;
  messages: any;
}

export const Route = createRootRouteWithContext<MyRouterContext>()({
  component: RootComponent,
});

function RootComponent() {
  const { locale, messages } = Route.useRouteContext();

  return (
    <I18nProvider locale={locale} messages={messages}>
      {/* Your app components */}
      <Outlet />
    </I18nProvider>
  );
}
```

### 2. The Locale Wrapper Route

Create a route that captures the locale and loads the messages.

```typescript
// app/routes/$locale.tsx
import { createFileRoute, redirect } from '@tanstack/react-router';
import { loadMessages } from '@kit/i18n/load-messages';
import { locales, defaultLocale } from '@kit/i18n/locales';

export const Route = createFileRoute('/$locale')({
  beforeLoad: ({ params }) => {
    // Validate locale
    if (!locales.includes(params.locale as any)) {
      throw redirect({
        to: '/$locale',
        params: { locale: defaultLocale },
        replace: true,
      });
    }
  },
  loader: async ({ params }) => {
    const messages = await loadMessages(params.locale);
    return {
      messages,
    };
  },
  context: ({ params, loaderData }) => {
    return {
      locale: params.locale,
      messages: loaderData.messages,
    };
  },
});
```

---

## Step 6: Create the I18n Provider

Use a library like `react-i18next` or a simple custom context to provide translation functions.

```typescript
// features/i18n-internationalization/lib/provider.tsx
import React, { createContext, useContext, useMemo } from 'react';

const I18nContext = createContext<{
  t: (key: string, params?: Record<string, string>) => string;
  locale: string;
} | null>(null);

export function I18nProvider({ locale, messages, children }) {
  const value = useMemo(() => ({
    locale,
    t: (key: string, params?: Record<string, string>) => {
      // Simple translation logic
      const [ns, ...rest] = key.split('.');
      let val = messages[ns];
      for (const k of rest) val = val?.[k];
      
      if (!val) return key;
      
      if (params) {
        Object.entries(params).forEach(([k, v]) => {
          val = val.replace(`{${k}}`, v);
        });
      }
      return val;
    }
  }), [locale, messages]);

  return (
    <I18nContext.Provider value={value}>
      {children}
    </I18nContext.Provider>
  );
}

export const useTranslation = () => {
  const context = useContext(I18nContext);
  if (!context) throw new Error('useTranslation must be used within I18nProvider');
  return context;
};
```

---

## Step 7: Locale-Aware Navigation

To make navigation easier, create a wrapper around TanStack Router's `Link`.

```typescript
// features/i18n-internationalization/lib/navigation.tsx
import { Link as RouterLink, useNavigate as useRouterNavigate } from '@tanstack/react-router';
import { useTranslation } from './provider';

export function Link({ to, params, ...props }) {
  const { locale } = useTranslation();
  return <RouterLink to={to} params={{ locale, ...params }} {...props} />;
}

export function useNavigate() {
  const navigate = useRouterNavigate();
  const { locale } = useTranslation();
  
  return (opts) => navigate({
    ...opts,
    params: { locale, ...opts.params }
  });
}
```

---

## Step 8: Handling the Root Path (Redirection)

In your `app/routes/index.tsx`, redirect users to their preferred or default locale.

```typescript
// app/routes/index.tsx
import { createFileRoute, redirect } from '@tanstack/react-router';
import { defaultLocale } from '@kit/i18n/locales';

export const Route = createFileRoute('/')({
  beforeLoad: () => {
    // In a real app, detect browser language or check cookies here
    throw redirect({
      to: '/$locale',
      params: { locale: defaultLocale },
    });
  },
});
```

---

## Summary of Benefits

1.  **SEO Friendly**: Every locale has its own URL.
2.  **Performance**: Messages are loaded on the server and hydrated on the client. Namespaces allow for smaller initial bundles.
3.  **Maintainability**: Shared package keeps i18n logic consistent across multiple apps/packages.
4.  **Developer Experience**: Locale-aware navigation components prevent accidental language switching during navigation.
