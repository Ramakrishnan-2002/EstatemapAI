'use client';

import React, { useState } from 'react';
import { Sparkles, Loader2, Check, ArrowRight, AlertCircle } from 'lucide-react';
import { aiApi } from '@/lib/api/ai';
import { PropertySearchIntent } from '@/types/ai';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';

interface NaturalLanguageSearchProps {
  onApplyIntent?: (intent: PropertySearchIntent) => void;
  className?: string;
}

export function NaturalLanguageSearch({
  onApplyIntent,
  className = '',
}: NaturalLanguageSearchProps) {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [parsedIntent, setParsedIntent] = useState<PropertySearchIntent | null>(null);
  const [latencyMs, setLatencyMs] = useState<number | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || query.length < 3) return;

    setIsLoading(true);
    setError(null);
    setParsedIntent(null);

    try {
      const res = await aiApi.parseSearch(query.trim());
      setParsedIntent(res.intent);
      setLatencyMs(res.latency_ms);
      if (onApplyIntent) {
        onApplyIntent(res.intent);
      }
    } catch (err: any) {
      setError(err?.message || 'Failed to parse natural language search intent.');
    } finally {
      setIsLoading(false);
    }
  };

  const formatPrice = (priceInr?: number | null) => {
    if (!priceInr) return null;
    if (priceInr >= 10_000_000) {
      return `₹${(priceInr / 10_000_000).toFixed(1)} Cr`;
    }
    if (priceInr >= 100_000) {
      return `₹${(priceInr / 100_000).toFixed(0)} Lakh`;
    }
    return `₹${priceInr.toLocaleString('en-IN')}`;
  };

  return (
    <div
      className={`rounded-xl border border-border/80 bg-gradient-to-r from-primary/5 via-card to-card p-4 shadow-sm transition-all ${className}`}
    >
      <div className="mb-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-primary animate-pulse" />
          <h3 className="text-sm font-semibold text-foreground">Ask EstateMap AI</h3>
          <span className="rounded-full bg-primary/10 px-2 py-0.5 text-[10px] font-medium text-primary">
            Natural Language
          </span>
        </div>
        {latencyMs !== null && (
          <span className="text-[11px] text-muted-foreground">
            Extracted in {latencyMs}ms
          </span>
        )}
      </div>

      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="relative flex-1">
          <Input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. 2 BHK under 70 lakh near Whitefield with hospital access"
            disabled={isLoading}
            className="h-10 bg-background pr-8 text-sm"
          />
        </div>
        <Button
          type="submit"
          disabled={isLoading || query.trim().length < 3}
          className="h-10 px-4 font-medium"
        >
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Parsing...
            </>
          ) : (
            <>
              Parse Intent
              <ArrowRight className="ml-1.5 h-4 w-4" />
            </>
          )}
        </Button>
      </form>

      {error && (
        <div className="mt-2.5 flex items-center gap-1.5 text-xs text-destructive">
          <AlertCircle className="h-3.5 w-3.5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {parsedIntent && (
        <div className="mt-3 rounded-lg border border-primary/20 bg-primary/5 p-3">
          <div className="mb-1.5 flex items-center justify-between">
            <span className="text-xs font-medium text-foreground">
              Understood criteria:
            </span>
            <span className="text-[11px] text-muted-foreground">
              Pydantic-validated
            </span>
          </div>

          <div className="flex flex-wrap gap-1.5">
            {parsedIntent.bedrooms && (
              <Badge variant="secondary" className="text-xs font-normal">
                🛏️ {parsedIntent.bedrooms} BHK
              </Badge>
            )}
            {parsedIntent.max_price && (
              <Badge variant="secondary" className="text-xs font-normal">
                💰 Max {formatPrice(parsedIntent.max_price)}
              </Badge>
            )}
            {parsedIntent.locality && (
              <Badge variant="secondary" className="text-xs font-normal">
                📍 {parsedIntent.locality}
              </Badge>
            )}
            {parsedIntent.city && (
              <Badge variant="secondary" className="text-xs font-normal">
                🏙️ {parsedIntent.city}
              </Badge>
            )}
            {parsedIntent.preferred_poi_categories?.map((cat) => (
              <Badge key={cat} variant="outline" className="text-xs font-normal">
                🎯 {cat.replace('_', ' ')}
              </Badge>
            ))}
            {parsedIntent.commute_destination && (
              <Badge variant="secondary" className="text-xs font-normal">
                🚗 Commute: {parsedIntent.commute_destination}
              </Badge>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
