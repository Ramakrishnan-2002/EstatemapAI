import React from "react";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

interface PropertyCardSkeletonProps {
  className?: string;
}

export function PropertyCardSkeleton({ className }: PropertyCardSkeletonProps) {
  return (
    <div
      className={cn(
        "flex flex-col overflow-hidden rounded-lg border border-border bg-card p-0 shadow-sm",
        className
      )}
    >
      <Skeleton className="aspect-[16/10] w-full rounded-none" />
      <div className="flex flex-col p-4 space-y-2.5">
        <Skeleton className="h-6 w-1/3" />
        <Skeleton className="h-4 w-4/5" />
        <Skeleton className="h-3.5 w-1/2" />
        <div className="pt-2 border-t border-border/60">
          <Skeleton className="h-3.5 w-3/4" />
        </div>
      </div>
    </div>
  );
}
