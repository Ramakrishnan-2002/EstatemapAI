import * as React from "react";
import { AlertCircle, FileQuestion, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";

interface LoadingStateProps {
  title?: string;
  description?: string;
}

export function LoadingState({
  title = "Loading properties...",
  description = "Fetching spatial location and listing details from the server.",
}: LoadingStateProps) {
  return (
    <div className="flex min-h-[300px] flex-col items-center justify-center p-8 text-center">
      <Loader2 className="h-8 w-8 animate-spin text-primary" />
      <h3 className="mt-4 text-base font-semibold text-foreground">{title}</h3>
      <p className="mt-1 text-sm text-muted-foreground">{description}</p>
    </div>
  );
}

interface EmptyStateProps {
  title?: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
}

export function EmptyState({
  title = "No properties found",
  description = "Try adjusting your search criteria, price range, or expanding the location area.",
  actionLabel,
  onAction,
}: EmptyStateProps) {
  return (
    <div className="flex min-h-[300px] flex-col items-center justify-center rounded-lg border border-dashed border-border p-8 text-center">
      <div className="rounded-full bg-muted p-3">
        <FileQuestion className="h-6 w-6 text-muted-foreground" />
      </div>
      <h3 className="mt-4 text-base font-semibold text-foreground">{title}</h3>
      <p className="mt-1 max-w-sm text-sm text-muted-foreground">{description}</p>
      {actionLabel && onAction && (
        <Button onClick={onAction} variant="outline" size="sm" className="mt-4">
          {actionLabel}
        </Button>
      )}
    </div>
  );
}

interface ErrorStateProps {
  title?: string;
  message?: string;
  code?: string;
  requestId?: string;
  onRetry?: () => void;
}

export function ErrorState({
  title = "Failed to load data",
  message = "An error occurred while communicating with the service. Please try again.",
  code,
  requestId,
  onRetry,
}: ErrorStateProps) {
  return (
    <div className="flex min-h-[300px] flex-col items-center justify-center rounded-lg border border-destructive/20 bg-destructive/5 p-8 text-center">
      <div className="rounded-full bg-destructive/10 p-3">
        <AlertCircle className="h-6 w-6 text-destructive" />
      </div>
      <h3 className="mt-4 text-base font-semibold text-foreground">{title}</h3>
      <p className="mt-1 max-w-md text-sm text-muted-foreground">{message}</p>
      {(code || requestId) && (
        <div className="mt-3 flex flex-wrap items-center justify-center gap-2 text-xs text-muted-foreground">
          {code && (
            <span className="rounded bg-muted px-2 py-0.5 font-mono">
              Code: {code}
            </span>
          )}
          {requestId && (
            <span className="rounded bg-muted px-2 py-0.5 font-mono">
              Req ID: {requestId.substring(0, 8)}
            </span>
          )}
        </div>
      )}
      {onRetry && (
        <Button onClick={onRetry} variant="outline" size="sm" className="mt-4">
          Try Again
        </Button>
      )}
    </div>
  );
}
