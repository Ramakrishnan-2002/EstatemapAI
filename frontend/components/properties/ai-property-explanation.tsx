'use client';

import React, { useCallback, useEffect, useState } from 'react';
import { Sparkles, Loader2, RefreshCw, ShieldCheck, AlertCircle } from 'lucide-react';
import { aiApi } from '@/lib/api/ai';
import { AIExplanationResponse } from '@/types/ai';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface AIPropertyExplanationProps {
  propertyId: number;
  destinationLat?: number | null;
  destinationLng?: number | null;
  destinationName?: string | null;
  className?: string;
}

export function AIPropertyExplanation({
  propertyId,
  destinationLat,
  destinationLng,
  destinationName,
  className = '',
}: AIPropertyExplanationProps) {
  const [data, setData] = useState<AIExplanationResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchExplanation = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const res = await aiApi.explainProperty(propertyId, {
        destination_lat: destinationLat,
        destination_lng: destinationLng,
        destination_name: destinationName,
      });
      setData(res);
    } catch (err: any) {
      setError(err?.message || 'AI summary currently unavailable.');
    } finally {
      setIsLoading(false);
    }
  }, [propertyId, destinationLat, destinationLng, destinationName]);

  useEffect(() => {
    if (propertyId) {
      fetchExplanation();
    }
  }, [propertyId, fetchExplanation]);

  return (
    <div
      className={`rounded-xl border border-border/80 bg-gradient-to-br from-card via-card to-primary/5 p-5 shadow-sm ${className}`}
    >
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2 border-b border-border/60 pb-3">
        <div className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <Sparkles className="h-4 w-4" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-foreground">
              Why This Property Fits
            </h3>
            <p className="text-[11px] text-muted-foreground">
              Factual synthesis of price, location intelligence & commute
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Badge
            variant="outline"
            className="flex items-center gap-1 bg-background/80 text-[10px] font-normal text-muted-foreground"
          >
            <ShieldCheck className="h-3 w-3 text-emerald-500" />
            Verified Facts
          </Badge>
          <Button
            variant="ghost"
            size="icon"
            onClick={fetchExplanation}
            disabled={isLoading}
            className="h-7 w-7 text-muted-foreground hover:text-foreground"
            title="Refresh explanation"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? 'animate-spin' : ''}`} />
          </Button>
        </div>
      </div>

      {isLoading ? (
        <div className="space-y-2.5 py-3">
          <div className="h-3.5 w-full animate-pulse rounded bg-muted" />
          <div className="h-3.5 w-5/6 animate-pulse rounded bg-muted" />
          <div className="h-3.5 w-2/3 animate-pulse rounded bg-muted" />
        </div>
      ) : error ? (
        <div className="flex items-center justify-between py-2 text-xs text-muted-foreground">
          <div className="flex items-center gap-1.5 text-amber-500">
            <AlertCircle className="h-4 w-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={fetchExplanation}
            className="h-7 text-xs"
          >
            Retry
          </Button>
        </div>
      ) : data ? (
        <div>
          <p className="text-sm leading-relaxed text-foreground/90">
            {data.explanation}
          </p>

          <div className="mt-3 flex items-center justify-between text-[11px] text-muted-foreground">
            <span>
              {data.fallback_used ? (
                'Deterministic Rule-Based Summary'
              ) : (
                `Generated via ${data.provider} (${data.model})`
              )}
            </span>
            {data.latency_ms > 0 && <span>{data.latency_ms}ms</span>}
          </div>
        </div>
      ) : null}
    </div>
  );
}
