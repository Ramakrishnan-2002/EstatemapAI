"use client";

import React from "react";
import Link from "next/link";
import { X, ArrowRight, Scale, Trash2 } from "lucide-react";
import { useComparison } from "@/context/comparison-context";
import { formatPrice } from "@/lib/formatters/currency";
import { Button } from "@/components/ui/button";

export function ComparisonBar() {
  const { selectedProperties, removeCompare, clearCompare, maxAllowed } = useComparison();

  if (selectedProperties.length === 0) {
    return null;
  }

  const compareUrl = `/compare?ids=${selectedProperties.map((p) => p.id).join(",")}`;
  const canCompare = selectedProperties.length >= 2;

  return (
    <div className="fixed bottom-4 left-1/2 -translate-x-1/2 z-50 w-[95%] max-w-4xl animate-in fade-in slide-in-from-bottom-5 duration-300">
      <div className="bg-background/95 backdrop-blur-md border-2 border-primary/30 shadow-2xl rounded-2xl p-3 sm:p-4 flex flex-col sm:flex-row items-center justify-between gap-3">
        {/* Left: Indicator & Selection Thumbnails */}
        <div className="flex items-center gap-3 w-full sm:w-auto overflow-x-auto pb-1 sm:pb-0">
          <div className="flex items-center gap-1.5 shrink-0 px-2 py-1 bg-primary/10 rounded-lg text-primary font-semibold text-xs sm:text-sm">
            <Scale className="h-4 w-4" />
            <span>Compare</span>
            <span className="bg-primary text-primary-foreground rounded-full px-1.5 py-0.2 text-xs">
              {selectedProperties.length}/{maxAllowed}
            </span>
          </div>

          <div className="flex items-center gap-2">
            {selectedProperties.map((prop, idx) => {
              const label = String.fromCharCode(65 + idx); // A, B, C
              const imgUrl = prop.images && prop.images.length > 0 ? prop.images[0].image_url : null;
              return (
                <div
                  key={prop.id}
                  className="relative group flex items-center gap-2 bg-muted/60 border border-border rounded-xl px-2.5 py-1.5 text-xs shrink-0 max-w-[200px]"
                >
                  <span className="w-5 h-5 rounded-full bg-primary/20 text-primary font-bold flex items-center justify-center text-[10px]">
                    {label}
                  </span>
                  {imgUrl ? (
                    <img
                      src={imgUrl}
                      alt={prop.title}
                      className="w-7 h-7 rounded-md object-cover border border-border/50 shrink-0"
                    />
                  ) : null}
                  <div className="overflow-hidden">
                    <p className="font-medium truncate text-foreground text-[11px]">{prop.title}</p>
                    <p className="text-muted-foreground text-[10px] font-mono">{formatPrice(prop.price)}</p>
                  </div>
                  <button
                    onClick={() => removeCompare(prop.id)}
                    className="ml-1 text-muted-foreground hover:text-destructive p-0.5 rounded transition-colors"
                    aria-label={`Remove ${prop.title} from comparison`}
                  >
                    <X className="h-3.5 w-3.5" />
                  </button>
                </div>
              );
            })}

            {/* Empty slots placeholders */}
            {Array.from({ length: maxAllowed - selectedProperties.length }).map((_, i) => (
              <Link
                key={`empty-${i}`}
                href="/search"
                className="hidden md:flex items-center justify-center border border-dashed border-border/80 hover:border-primary/60 hover:text-primary rounded-xl px-3 py-2 text-[11px] text-muted-foreground/80 w-28 text-center transition-colors cursor-pointer"
                title="Browse listings to add more properties to comparison"
              >
                + Add property
              </Link>
            ))}
          </div>
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-2 w-full sm:w-auto justify-end shrink-0">
          <Button
            variant="ghost"
            size="sm"
            onClick={clearCompare}
            className="text-xs text-muted-foreground hover:text-destructive h-8 px-2"
          >
            <Trash2 className="h-3.5 w-3.5 mr-1" />
            Clear
          </Button>

          <Button
            asChild
            size="sm"
            disabled={!canCompare}
            className={canCompare ? "bg-primary text-primary-foreground font-semibold shadow-md h-8 px-3 text-xs" : "opacity-50 pointer-events-none h-8 px-3 text-xs"}
          >
            <Link href={canCompare ? compareUrl : "#"}>
              <span>{canCompare ? "Compare Now" : "Select 2 or 3"}</span>
              <ArrowRight className="ml-1.5 h-3.5 w-3.5" />
            </Link>
          </Button>
        </div>
      </div>
    </div>
  );
}
