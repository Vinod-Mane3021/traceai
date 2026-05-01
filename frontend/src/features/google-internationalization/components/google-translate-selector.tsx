import React, { useEffect, useState } from "react";
import { Languages, Check, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

declare global {
  interface Window {
    googleTranslateElementInit: () => void;
    google: any;
  }
}

const LANGUAGES = [
  { label: "English", code: "en" },
  { label: "Spanish (Español)", code: "es" },
  { label: "French (Français)", code: "fr" },
  { label: "German (Deutsch)", code: "de" },
  { label: "Chinese (中文)", code: "zh-CN" },
  { label: "Hindi (हिन्दी)", code: "hi" },
];

export function GoogleTranslateSelector() {
  const [currentLang, setCurrentLang] = useState("en");
  const [isInitializing, setIsInitializing] = useState(true);

  useEffect(() => {
    // 1. Initialize Google Translate if not already there
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
            autoDisplay: false,
          },
          "google_translate_element_hidden"
        );
        setIsInitializing(false);
      };
    } else {
      setIsInitializing(false);
    }

    // 2. Sync state with cookie if exists
    const getCookie = (name: string) => {
      const value = `; ${document.cookie}`;
      const parts = value.split(`; ${name}=`);
      if (parts.length === 2) return parts.pop()?.split(";").shift();
    };

    const googtrans = getCookie("googtrans");
    if (googtrans) {
      const lang = googtrans.split("/").pop();
      if (lang) setCurrentLang(lang);
    }
  }, []);

  const changeLanguage = (langCode: string) => {
    // Google Translate works by looking at the 'googtrans' cookie
    // Format: /auto/lang_code
    document.cookie = `googtrans=/en/${langCode}; path=/`;
    document.cookie = `googtrans=/en/${langCode}; path=/; domain=.${window.location.hostname}`;
    
    // Refresh to apply translation (Google Translate widget requires a reload or complex JS trigger)
    window.location.reload();
  };

  return (
    <>
      {/* Hidden default Google widget */}
      <div id="google_translate_element_hidden" style={{ display: "none" }} />
      
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground relative">
            {isInitializing ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Languages className="h-4 w-4" />
            )}
            <span className="sr-only">Translate page</span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-40 notranslate">
          {LANGUAGES.map((lang) => (
            <DropdownMenuItem
              key={lang.code}
              onClick={() => changeLanguage(lang.code)}
              className="flex items-center justify-between"
            >
              {lang.label}
              {currentLang === lang.code && <Check className="h-3.5 w-3.5 text-primary" />}
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>

      <style>{`
        /* Hide the Google Translate top banner */
        .goog-te-banner-frame { display: none !important; }
        body { top: 0 !important; }
        .skiptranslate { display: none !important; }
      `}</style>
    </>
  );
}
