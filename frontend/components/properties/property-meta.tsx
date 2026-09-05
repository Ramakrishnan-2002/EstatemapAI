import React from "react";
import { formatArea, formatBathrooms, formatBedrooms } from "@/lib/formatters/property";
import { cn } from "@/lib/utils";

interface PropertyMetaProps {
  bedrooms?: number | null;
  bathrooms?: number | null;
  areaSqFt: number;
  className?: string;
  size?: "sm" | "md";
}

export function PropertyMeta({
  bedrooms,
  bathrooms,
  areaSqFt,
  className,
  size = "sm",
}: PropertyMetaProps) {
  const isSmall = size === "sm";

  return (
    <div
      className={cn(
        "flex flex-wrap items-center gap-2 text-muted-foreground",
        isSmall ? "text-xs" : "text-sm",
        className
      )}
    >
      <span className="font-medium text-foreground/90">
        {formatBedrooms(bedrooms)}
      </span>
      <span className="text-border">•</span>
      <span>{formatBathrooms(bathrooms)}</span>
      <span className="text-border">•</span>
      <span>{formatArea(areaSqFt)}</span>
    </div>
  );
}
