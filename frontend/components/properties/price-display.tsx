import React from "react";
import { formatPrice, formatPricePerSqFt } from "@/lib/formatters/currency";
import { cn } from "@/lib/utils";

interface PriceDisplayProps {
  price: number;
  areaSqFt?: number;
  size?: "sm" | "md" | "lg" | "xl";
  className?: string;
  showRate?: boolean;
}

export function PriceDisplay({
  price,
  areaSqFt,
  size = "md",
  className,
  showRate = false,
}: PriceDisplayProps) {
  const sizeClasses = {
    sm: "text-sm font-semibold",
    md: "text-lg font-bold",
    lg: "text-2xl font-bold tracking-tight",
    xl: "text-3xl font-extrabold tracking-tight",
  };

  return (
    <div className={cn("flex flex-col", className)}>
      <span className={cn(sizeClasses[size], "text-foreground")}>
        {formatPrice(price)}
      </span>
      {showRate && areaSqFt && areaSqFt > 0 && (
        <span className="text-xs text-muted-foreground font-normal">
          {formatPricePerSqFt(price, areaSqFt)}
        </span>
      )}
    </div>
  );
}
