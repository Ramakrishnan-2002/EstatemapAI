'use client';

import React, { useState } from 'react';
import {
  Sparkles,
  Loader2,
  Send,
  X,
  AlertCircle,
  HelpCircle,
  CheckCircle2,
  Cpu,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  ConversationalSearchState,
  AskMapResponse,
} from '@/types/conversational_search';
import { askTheMap } from '@/lib/api/ask-map';
import { BoundingBoxSearchParams, ViewportSearchParams } from '@/types';

interface AskTheMapBarProps {
  currentState: ConversationalSearchState;
  mapViewport?: BoundingBoxSearchParams | ViewportSearchParams | null;
  onResponse: (response: AskMapResponse) => void;
  onCompare?: (ids: number[]) => void;
  className?: string;
}

const BENGALURU_SUGGESTIONS = [
  '2 BHK under 80L in Indiranagar',
  'Near EcoSpace within 20 min driving',
  'Add transit & hospital access',
  'Rank by commute',
  'Compare top 2',
  'Reset search',
];

const CHENNAI_SUGGESTIONS = [
  '3 BHK under 1.5 Cr in Adyar',
  'Near TIDEL Park within 20 min driving',
  'Near DLF Cybercity with gym',
  'Rank by commute',
  'Compare top 2',
  'Reset search',
];

export function AskTheMapBar({
  currentState,
  mapViewport,
  onResponse,
  onCompare,
  className = '',
}: AskTheMapBarProps) {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastResponse, setLastResponse] = useState<AskMapResponse | null>(null);
  const [sessionId] = useState<string>(() => `sess_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`);

  const suggestions =
    currentState.city?.toLowerCase() === 'chennai'
      ? CHENNAI_SUGGESTIONS
      : BENGALURU_SUGGESTIONS;

  const handleSubmit = async (textToSubmit?: string) => {
    const message = (textToSubmit ?? query).trim();
    if (!message) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await askTheMap({
        message,
        session_id: sessionId,
        current_state: currentState,
        map_viewport: mapViewport,
      });

      setLastResponse(response);
      onResponse(response);

      // If response action is compare and target property IDs exist, notify compare handler
      if (response.action === 'compare' && response.state.selected_property_ids?.length > 0 && onCompare) {
        onCompare(response.state.selected_property_ids);
      }

      setQuery('');
    } catch (err: any) {
      setError(err?.message || 'Failed to process conversational search.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClarificationChoice = (suggestion: string) => {
    handleSubmit(suggestion);
  };

  return (
    <div
      className={`rounded-xl border border-primary/20 bg-gradient-to-r from-primary/5 via-card to-card p-4 shadow-sm transition-all ${className}`}
    >
      {/* Header & Meta telemetry */}
      <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <Sparkles className="h-4 w-4 animate-pulse" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-foreground">Ask the Map</h3>
            <p className="text-[11px] text-muted-foreground">
              Conversational search & multi-turn map refinement
            </p>
          </div>
        </div>

        {lastResponse && (
          <div className="flex items-center gap-2 text-[11px]">
            <Badge
              variant="outline"
              className="bg-background/80 text-muted-foreground font-mono text-[10px] gap-1"
            >
              <Cpu className="h-3 w-3" />
              {lastResponse.provider} ({lastResponse.model})
            </Badge>
            <span className="text-muted-foreground">
              {lastResponse.latency_ms}ms
            </span>
            {lastResponse.fallback_used && (
              <Badge variant="secondary" className="bg-amber-500/10 text-amber-600 text-[10px]">
                Fallback
              </Badge>
            )}
          </div>
        )}
      </div>

      {/* Input Form */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSubmit();
        }}
        className="flex gap-2"
      >
        <div className="relative flex-1">
          <Input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask anything... e.g., '2 BHK in Indiranagar under 80L', 'Filter to near hospitals', 'Compare top 2'"
            disabled={isLoading}
            className="h-10 bg-background pr-8 text-sm"
          />
          {query && (
            <button
              type="button"
              onClick={() => setQuery('')}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground cursor-pointer"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
        <Button
          type="submit"
          disabled={isLoading || !query.trim()}
          className="h-10 px-4 font-semibold"
        >
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Orchestrating...
            </>
          ) : (
            <>
              Send
              <Send className="ml-1.5 h-3.5 w-3.5" />
            </>
          )}
        </Button>
      </form>

      {/* Quick Suggestion Pills */}
      <div className="mt-2.5 flex flex-wrap items-center gap-1.5">
        <span className="text-[11px] font-medium text-muted-foreground">Try:</span>
        {suggestions.map((sugg) => (
          <button
            key={sugg}
            type="button"
            disabled={isLoading}
            onClick={() => {
              setQuery(sugg);
              handleSubmit(sugg);
            }}
            className="rounded-full border border-border/70 bg-background/80 px-2.5 py-0.5 text-[11px] text-muted-foreground transition hover:border-primary/40 hover:bg-primary/5 hover:text-foreground disabled:opacity-50 cursor-pointer"
          >
            {sugg}
          </button>
        ))}
      </div>

      {/* Clarification Alert */}
      {lastResponse?.needs_clarification && (
        <div className="mt-3 rounded-lg border border-amber-500/30 bg-amber-500/10 p-3 text-xs text-amber-900 dark:text-amber-200">
          <div className="flex items-start gap-2">
            <HelpCircle className="h-4 w-4 shrink-0 text-amber-600 dark:text-amber-400 mt-0.5" />
            <div className="space-y-2">
              <p className="font-medium">
                {lastResponse.clarification_prompt || 'Could you please clarify your request?'}
              </p>
              <div className="flex flex-wrap gap-1.5 pt-1">
                {currentState.city?.toLowerCase() === 'chennai' ? (
                  <>
                    <button
                      type="button"
                      onClick={() => handleClarificationChoice('TIDEL Park')}
                      className="rounded bg-amber-500/20 px-2 py-0.5 text-[11px] font-medium hover:bg-amber-500/30 transition cursor-pointer"
                    >
                      📍 TIDEL Park (OMR)
                    </button>
                    <button
                      type="button"
                      onClick={() => handleClarificationChoice('DLF Cybercity')}
                      className="rounded bg-amber-500/20 px-2 py-0.5 text-[11px] font-medium hover:bg-amber-500/30 transition cursor-pointer"
                    >
                      📍 DLF Cybercity (Porur)
                    </button>
                    <button
                      type="button"
                      onClick={() => handleClarificationChoice('Anna Nagar')}
                      className="rounded bg-amber-500/20 px-2 py-0.5 text-[11px] font-medium hover:bg-amber-500/30 transition cursor-pointer"
                    >
                      📍 Anna Nagar
                    </button>
                    <button
                      type="button"
                      onClick={() => handleClarificationChoice('Adyar')}
                      className="rounded bg-amber-500/20 px-2 py-0.5 text-[11px] font-medium hover:bg-amber-500/30 transition cursor-pointer"
                    >
                      📍 Adyar
                    </button>
                  </>
                ) : (
                  <>
                    <button
                      type="button"
                      onClick={() => handleClarificationChoice('EcoSpace Bellandur')}
                      className="rounded bg-amber-500/20 px-2 py-0.5 text-[11px] font-medium hover:bg-amber-500/30 transition cursor-pointer"
                    >
                      📍 EcoSpace (Bellandur)
                    </button>
                    <button
                      type="button"
                      onClick={() => handleClarificationChoice('Manyata Tech Park')}
                      className="rounded bg-amber-500/20 px-2 py-0.5 text-[11px] font-medium hover:bg-amber-500/30 transition cursor-pointer"
                    >
                      📍 Manyata Tech Park
                    </button>
                    <button
                      type="button"
                      onClick={() => handleClarificationChoice('Electronic City')}
                      className="rounded bg-amber-500/20 px-2 py-0.5 text-[11px] font-medium hover:bg-amber-500/30 transition cursor-pointer"
                    >
                      📍 Electronic City
                    </button>
                    <button
                      type="button"
                      onClick={() => handleClarificationChoice('Indiranagar 100ft Road')}
                      className="rounded bg-amber-500/20 px-2 py-0.5 text-[11px] font-medium hover:bg-amber-500/30 transition cursor-pointer"
                    >
                      📍 Indiranagar
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Error display */}
      {error && (
        <div className="mt-2.5 flex items-center gap-1.5 text-xs text-destructive">
          <AlertCircle className="h-3.5 w-3.5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Response Feedback & Patch Badges */}
      {lastResponse && !lastResponse.needs_clarification && (
        <div className="mt-3 space-y-2 rounded-lg border border-border/80 bg-background/80 p-3">
          {/* AI Message */}
          <div className="flex items-start gap-2">
            <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-500 mt-0.5" />
            <div className="space-y-1">
              <p className="text-xs font-medium text-foreground">
                {lastResponse.message}
              </p>
              {lastResponse.explanation_bullets && lastResponse.explanation_bullets.length > 0 && (
                <ul className="list-disc list-inside space-y-0.5 text-[11px] text-muted-foreground pl-1">
                  {lastResponse.explanation_bullets.map((b, idx) => (
                    <li key={idx}>{b}</li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          {/* Patch Field Badges */}
          <div className="flex flex-wrap items-center gap-1.5 pt-1 border-t border-border/50 text-[11px]">
            {lastResponse.feedback.added.map((item) => (
              <Badge
                key={`add-${item}`}
                variant="outline"
                className="border-emerald-500/40 bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 text-[10px] font-medium"
              >
                + Added: {item}
              </Badge>
            ))}
            {lastResponse.feedback.modified.map((item) => (
              <Badge
                key={`mod-${item}`}
                variant="outline"
                className="border-blue-500/40 bg-blue-500/10 text-blue-700 dark:text-blue-300 text-[10px] font-medium"
              >
                ✏️ Modified: {item}
              </Badge>
            ))}
            {lastResponse.feedback.removed.map((item) => (
              <Badge
                key={`rem-${item}`}
                variant="outline"
                className="border-amber-500/40 bg-amber-500/10 text-amber-700 dark:text-amber-300 text-[10px] font-medium"
              >
                ✕ Cleared: {item}
              </Badge>
            ))}
            {lastResponse.feedback.preserved.length > 0 && (
              <span className="text-[10px] text-muted-foreground ml-1">
                Preserved: {lastResponse.feedback.preserved.join(', ')}
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
