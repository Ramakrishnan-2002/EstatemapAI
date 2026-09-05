"use client";

import React from "react";
import { RankingContributionDelta } from "@/types/comparison";
import { Award, TrendingUp, TrendingDown, Minus } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface RankingDiffCardProps {
  delta: RankingContributionDelta;
  className?: string;
}

const FACTOR_NAMES: Record<string, string> = {
  price: "Price Fit",
  bedrooms: "Bedrooms Match",
  area: "Living Area",
  locality: "Locality Match",
  location: "POI Proximity",
  commute: "Commute Efficiency",
};

export function RankingDiffCard({ delta, className }: RankingDiffCardProps) {
  const factorEntries = Object.entries(delta.factor_deltas).sort(
    ([, a], [, b]) => Math.abs(b) - Math.abs(a)
  );

  return (
    <div className={`rounded-xl border border-border/70 bg-card/60 p-4 shadow-xs ${className || ""}`}>
      {/* Header */}
      <div className="flex items-center justify-between gap-2 border-b border-border/50 pb-3">
        <div className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <Award className="h-4 w-4" />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-foreground">
              {delta.winner_label} vs {delta.loser_label}
            </h4>
            <p className="text-xs text-muted-foreground">
              Net Score Advantage:{" "}
              <span className="font-semibold text-emerald-600 dark:text-emerald-400">
                +{delta.net_score_delta.toFixed(1)} pts
              </span>{" "}
              ({delta.winner_score.toFixed(1)}% vs {delta.loser_score.toFixed(1)}%)
            </p>
          </div>
        </div>
        <Badge variant="outline" className="bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/30 text-xs font-semibold">
          Higher Match: {delta.winner_label}
        </Badge>
      </div>

      {/* Summary statement */}
      <p className="mt-3 text-xs leading-relaxed text-foreground/90 font-medium bg-muted/30 p-2.5 rounded-lg border border-border/40">
        {delta.summary}
      </p>

      {/* Factor by factor breakdown table */}
      <div className="mt-3.5 space-y-2">
        <div className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">
          Factor Contribution Delta
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {factorEntries.map(([factorKey, diff]) => {
            const isPositive = diff > 0;
            const isNeutral = Math.abs(diff) < 0.01;
            const name = FACTOR_NAMES[factorKey] || factorKey;

            return (
              <div
                key={factorKey}
                className="flex items-center justify-between rounded-lg bg-background/80 border border-border/40 px-2.5 py-1.5 text-xs"
              >
                <span className="text-muted-foreground font-medium">{name}</span>
                <div className="flex items-center gap-1 font-mono font-semibold">
                  {isNeutral ? (
                    <span className="text-muted-foreground flex items-center gap-0.5">
                      <Minus className="h-3 w-3" /> 0.0
                    </span>
                  ) : isPositive ? (
                    <span className="text-emerald-600 dark:text-emerald-400 flex items-center gap-0.5">
                      <TrendingUp className="h-3.5 w-3.5" /> +{diff.toFixed(1)}
                    </span>
                  ) : (
                    <span className="text-rose-500 flex items-center gap-0.5">
                      <TrendingDown className="h-3.5 w-3.5" /> {diff.toFixed(1)}
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
