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
   * Components to use for rich text interpolation.
   * Example: { b: <strong /> } for "Hello <b>John</b>"
   */
  components?: Record<string, React.ReactElement | ((chunks: React.ReactNode) => React.ReactNode)>;
  /**
   * The translation namespace (optional).
   */
  ns?: string;
}

/**
 * Trans component for displaying translated text using the local i18n system.
 * Supports both i18next-style (ns:key) and dot notation.
 * Supports basic rich text via 'components' prop.
 */
export function Trans({ i18nKey, defaults, values, components, ns }: TransProps) {
  const { t } = useTranslation();

  if (!i18nKey) return <>{defaults ?? null}</>;

  // Support "namespace:key" format
  let finalKey = i18nKey;
  if (i18nKey.includes(":")) {
    finalKey = i18nKey.replace(":", ".");
  } else if (ns && !i18nKey.startsWith(ns + ".")) {
    finalKey = `${ns}.${i18nKey}`;
  }

  const translation = t(finalKey, values);

  // If translation not found
  if (translation === finalKey && defaults) {
    return <>{defaults}</>;
  }

  // Handle rich text interpolation if components are provided
  if (components) {
    return <>{renderRichText(translation, components)}</>;
  }

  return <>{translation}</>;
}

/**
 * Simple parser for <tag>content</tag> style rich text.
 */
function renderRichText(
  text: string,
  components: Record<string, React.ReactElement | ((chunks: React.ReactNode) => React.ReactNode)>
): React.ReactNode[] {
  const regex = /<(\w+)>(.*?)<\/\1>/g;
  const parts: React.ReactNode[] = [];
  let lastIndex = 0;
  let match;

  while ((match = regex.exec(text)) !== null) {
    const [fullMatch, tagName, content] = match;
    const index = match.index;

    // Push text before the match
    if (index > lastIndex) {
      parts.push(text.substring(lastIndex, index));
    }

    const component = components[tagName];
    if (component) {
      if (typeof component === "function") {
        parts.push(component(content));
      } else {
        parts.push(React.cloneElement(component, { key: index }, content));
      }
    } else {
      parts.push(fullMatch); // Fallback to raw tag if component not found
    }

    lastIndex = regex.lastIndex;
  }

  // Push remaining text
  if (lastIndex < text.length) {
    parts.push(text.substring(lastIndex));
  }

  return parts.length > 0 ? parts : [text];
}
