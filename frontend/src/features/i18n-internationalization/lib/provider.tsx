import React, { createContext, useContext, useMemo } from "react";

interface I18nContextType {
  t: (key: string, params?: Record<string, string>) => string;
  locale: string;
}

const I18nContext = createContext<I18nContextType | null>(null);

export default function I18nProvider({
  locale,
  messages,
  children,
}: {
  locale: string;
  messages: any;
  children: React.ReactNode;
}) {
  const value = useMemo(
    () => ({
      locale: locale || "en",
      t: (key: string, params?: Record<string, string>) => {
        if (!messages) return key;

        // Try to find the key. Support optional namespace prefix or assume 'common'
        let parts = key.split(".");
        let ns = parts[0];
        let rest = parts.slice(1);

        let val = messages[ns];

        // If not found in namespace, try in 'common' namespace
        if (!val && ns !== "common" && messages["common"]) {
          val = messages["common"];
          // Don't shift parts if we are assuming common
          rest = parts;
        }

        if (!val) return key;

        for (const k of rest) {
          val = val?.[k];
        }

        if (typeof val !== "string") return key;

        if (params) {
          let translated = val;
          Object.entries(params).forEach(([k, v]) => {
            translated = translated.replace(`{${k}}`, v);
          });
          return translated;
        }
        return val;
      },
    }),
    [locale, messages]
  );

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export const useTranslation = () => {
  const context = useContext(I18nContext);
  if (!context) {
    // Return a dummy context instead of throwing to avoid blank page
    return {
      t: (key: string) => key,
      locale: "en",
    };
  }
  return context;
};
