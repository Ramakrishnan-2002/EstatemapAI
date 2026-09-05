"use client";

import React from "react";
import { Sparkles, Bot, Clock, AlertTriangle, ShieldCheck, Cpu } from "lucide-react";
import { AIComparisonResponse } from "@/types/comparison";
import { Badge } from "@/components/ui/badge";

interface AIComparisonSummaryProps {
  data?: AIComparisonResponse | null;
  isLoading?: boolean;
  error?: string | null;
  className?: string;
}

export function AIComparisonSummary({
  data,
  isLoading,
  error,
  className,
}: AIComparisonSummaryProps) {
  if (isLoading) {
    return (
      <div className={`rounded-2xl border border-primary/20 bg-primary/5 p-5 shadow-sm animate-pulse ${className || ""}`}>
        <div className="flex items-center gap-2 mb-4">
          <div className="h-6 w-6 rounded-full bg-primary/30" />
          <div className="h-4 w-48 rounded bg-primary/20" />
        </div>
        <div className="space-y-2.5">
          <div className="h-3.5 w-full rounded bg-muted/60" />
          <div className="h-3.5 w-[90%] rounded bg-muted/60" />
          <div className="h-3.5 w-[75%] rounded bg-muted/60" />
        </div>
      </div>
    );
  }

  if (error || !data) {
    return null;
  }

  const { narrative, provider, model, latency_ms, fallback_used, usage, routing_reason } = data;

  return (
    <div className={`rounded-2xl border border-primary/20 bg-gradient-to-br from-primary/5 via-card to-background p-5 sm:p-6 shadow-sm ${className || ""}`}>
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-border/50 pb-4">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-primary/10 text-primary shadow-xs">
            <Sparkles className="h-4 w-4" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-foreground flex items-center gap-2">
              Comparative Analysis & Trade-off Synthesis
            </h3>
            <p className="text-xs text-muted-foreground">
              Grounded synthesis across price, spatial dimensions, and commuting
            </p>
          </div>
        </div>

        {/* Telemetry badges */}
        <div className="flex items-center gap-2 flex-wrap text-xs">
          {fallback_used ? (
            <Badge variant="outline" className="bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/30 gap-1 text-[11px]">
              <AlertTriangle className="h-3 w-3" />
              Deterministic Rule Summary
            </Badge>
          ) : (
            <Badge variant="secondary" className="gap-1 bg-background/80 border border-border shadow-2xs text-[11px] font-medium">
              <Bot className="h-3 w-3 text-primary" />
              {provider.toUpperCase()} ({model})
            </Badge>
          )}

          <div className="flex items-center gap-1 text-muted-foreground font-mono text-[11px] bg-muted/40 px-2 py-0.5 rounded-md border border-border/40">
            <Clock className="h-3 w-3" />
            <span>{latency_ms.toFixed(0)} ms</span>
          </div>

          {usage?.total_tokens ? (
            <div className="hidden sm:flex items-center gap-1 text-muted-foreground font-mono text-[11px] bg-muted/40 px-2 py-0.5 rounded-md border border-border/40">
              <Cpu className="h-3 w-3" />
              <span>{usage.total_tokens} tokens</span>
            </div>
          ) : null}
        </div>
      </div>

      {/* Narrative content */}
      <div className="mt-4 text-sm leading-relaxed text-foreground/90 whitespace-pre-line font-normal space-y-2">
        {narrative}
      </div>

      {/* Routing reason & safety footnote */}
      <div className="mt-4 pt-3 border-t border-border/40 flex items-center justify-between text-[11px] text-muted-foreground">
        <span className="flex items-center gap-1">
          <ShieldCheck className="h-3.5 w-3.5 text-emerald-500" />
          All metrics computed deterministically by PostgreSQL/PostGIS.
        </span>
        {routing_reason && (
          <span className="italic text-muted-foreground/80 hidden md:inline">
            Route: {routing_reason}
          </span>
        )}
      </div>
    </div>
  );
}
