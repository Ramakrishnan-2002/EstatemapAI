import React from "react";
import Link from "next/link";
import { Database, MapPin } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-border/80 bg-card py-8 text-xs text-muted-foreground">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center justify-between gap-4 md:flex-row">
          {/* Brand & Tagline */}
          <div className="flex flex-col items-center gap-1 md:items-start">
            <div className="flex items-center gap-2">
              <span className="font-bold text-sm text-foreground">EstateMap AI</span>
              <span className="rounded bg-primary/10 px-1.5 py-0.5 text-[10px] font-semibold text-primary">
                v0.1.0
              </span>
            </div>
            <p className="text-muted-foreground">
              Location-first real estate discovery engine powered by FastAPI, PostGIS, and mapcn.
            </p>
          </div>

          {/* Technology Badges */}
          <div className="flex items-center gap-3">
            <span className="inline-flex items-center gap-1 rounded border border-border bg-background px-2 py-1 text-[11px] font-medium">
              <Database className="h-3 w-3 text-primary" /> PostGIS 3.4
            </span>
            <span className="inline-flex items-center gap-1 rounded border border-border bg-background px-2 py-1 text-[11px] font-medium">
              <MapPin className="h-3 w-3 text-emerald-600" /> MapLibre GL
            </span>
          </div>

          {/* Quick Links */}
          <div className="flex items-center gap-4 text-xs">
            <Link href="/search" className="hover:text-foreground">
              Explore Map
            </Link>
            <Link href="/favorites" className="hover:text-foreground">
              Saved
            </Link>
            <Link href="/dashboard" className="hover:text-foreground">
              Dashboard
            </Link>
          </div>
        </div>

        <div className="mt-6 border-t border-border/60 pt-4 text-center text-[11px] text-muted-foreground/80">
          © {new Date().getFullYear()} EstateMap AI. Architectural Portfolio Reference Implementation.
        </div>
      </div>
    </footer>
  );
}
