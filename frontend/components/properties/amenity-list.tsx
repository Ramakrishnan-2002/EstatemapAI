import React from "react";
import { Check } from "lucide-react";
import { Amenity } from "@/types";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface AmenityListProps {
  amenities: Amenity[];
  maxDisplay?: number;
  variant?: "badges" | "grid";
  className?: string;
}

export function AmenityList({
  amenities,
  maxDisplay,
  variant = "badges",
  className,
}: AmenityListProps) {
  if (!amenities || amenities.length === 0) {
    return null;
  }

  const items = maxDisplay ? amenities.slice(0, maxDisplay) : amenities;
  const remainingCount = maxDisplay ? amenities.length - maxDisplay : 0;

  if (variant === "grid") {
    return (
      <div className={cn("grid grid-cols-2 sm:grid-cols-3 gap-3", className)}>
        {items.map((amenity) => (
          <div
            key={amenity.id}
            className="flex items-center gap-2 rounded-md border border-border bg-card p-2.5 text-xs text-foreground/80"
          >
            <Check className="h-4 w-4 shrink-0 text-emerald-600 dark:text-emerald-400" />
            <span className="truncate font-medium">{amenity.name}</span>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className={cn("flex flex-wrap items-center gap-1.5", className)}>
      {items.map((amenity) => (
        <Badge key={amenity.id} variant="secondary" className="font-normal text-xs">
          {amenity.name}
        </Badge>
      ))}
      {remainingCount > 0 && (
        <Badge variant="outline" className="font-normal text-xs text-muted-foreground">
          +{remainingCount} more
        </Badge>
      )}
    </div>
  );
}
