import React from "react";
import { useTranslation } from "../lib/provider";

interface TransProps {
  /**
   * The i18n key to translate. Supports:
   * - "namespace:key" (e.g. "auth:login.title")
   * - "namespace.key" (e.g. "auth.login.title")
   */
  i18nKey: string | undefined;
  /**
   * Default text to use if the translation key is not found.
   */
  defaults?: React.ReactNode;
  /**
   * Values to interpolate into the translation.
   * Example: { name: 'John' } for a translation like "Hello {name}"
   */
  values?: Record<string, string>;
  /**
   * The translation namespace (optional).
   */
  ns?: string;
}

/**
 * Trans component for displaying translated text using the local i18n system.
 * Supports both i18next-style (ns:key) and dot notation.
 */
export function Trans({ i18nKey, defaults, values, ns }: TransProps) {
  const { t } = useTranslation();

  if (!i18nKey) return <>{defaults ?? null}</>;

  // Support "namespace:key" format by converting it to "namespace.key"
  // If ns is provided via prop, we use it. Otherwise we try to extract from key.
  let finalKey = i18nKey;
  if (i18nKey.includes(":")) {
    finalKey = i18nKey.replace(":", ".");
  } else if (ns && !i18nKey.startsWith(ns + ".")) {
    finalKey = `${ns}.${i18nKey}`;
  }

  const translation = t(finalKey, values);

  // If the translation returned is just the key itself (meaning not found)
  // return the defaults if provided
  if (translation === finalKey && defaults) {
    return <>{defaults}</>;
  }

  return <>{translation}</>;
}
