import React, { useEffect } from "react";

declare global {
  interface Window {
    googleTranslateElementInit: () => void;
    google: any;
  }
}

export function GoogleTranslate() {
  useEffect(() => {
    // Only add the script if it doesn't exist
    if (!document.getElementById("google-translate-script")) {
      const script = document.createElement("script");
      script.id = "google-translate-script";
      script.type = "text/javascript";
      script.src = "//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit";
      document.body.appendChild(script);

      window.googleTranslateElementInit = () => {
        new window.google.translate.TranslateElement(
          {
            pageLanguage: "en",
            layout: window.google.translate.TranslateElement.InlineLayout.SIMPLE,
            autoDisplay: false,
          },
          "google_translate_element"
        );
      };
    }
  }, []);

  return (
    <div className="google-translate-container flex items-center">
      <div id="google_translate_element" className="h-8" />
      <style>{`
        .goog-te-gadget {
          font-family: inherit !important;
          font-size: 0 !important;
        }
        .goog-te-gadget .goog-te-combo {
          margin: 0 !important;
          padding: 4px 8px !important;
          border-radius: 6px !important;
          border: 1px solid var(--border) !important;
          background: var(--card) !important;
          color: var(--foreground) !important;
          font-size: 12px !important;
          font-family: inherit !important;
          outline: none !important;
          height: 32px !important;
        }
        .goog-te-banner-frame {
          display: none !important;
        }
        body {
          top: 0 !important;
        }
        .goog-logo-link {
          display: none !important;
        }
        .goog-te-gadget span {
          display: none !important;
        }
      `}</style>
    </div>
  );
}
