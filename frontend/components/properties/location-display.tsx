import React from "react";
import { MapPin } from "lucide-react";
import { cn } from "@/lib/utils";

interface LocationDisplayProps {
  locality: string;
  city: string;
  address?: string;
  showAddress?: boolean;
  className?: string;
}

export function LocationDisplay({
  locality,
  city,
  address,
  showAddress = false,
  className,
}: LocationDisplayProps) {
  return (
    <div className={cn("flex items-start gap-1.5 text-muted-foreground", className)}>
      <MapPin className="mt-0.5 h-3.5 w-3.5 shrink-0 text-primary/70" />
      <div className="flex flex-col">
        <span className="text-xs font-medium text-foreground/80">
          {locality}, {city}
        </span>
        {showAddress && address && (
          <span className="text-xs text-muted-foreground line-clamp-1">{address}</span>
        )}
      </div>
    </div>
  );
}
