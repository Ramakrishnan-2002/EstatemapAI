"use client";

import React from "react";
import Link from "next/link";
import { ArrowRight, Bed, Bath, Maximize2, MapPin } from "lucide-react";
import { Property } from "@/types";
import { formatPrice } from "@/lib/formatters/currency";
import { formatArea, formatBedrooms, formatBathrooms, formatPropertyType } from "@/lib/formatters/property";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface PropertyPopupProps {
  property: Property;
  onClose?: () => void;
}

export function PropertyPopup({ property, onClose }: PropertyPopupProps) {
  const primaryImage =
    property.images && property.images.length > 0
      ? property.images[0].image_url
      : null;

  return (
    <div
      className="w-64 overflow-hidden rounded-lg border border-border bg-card shadow-xl transition-all"
      role="dialog"
      aria-label={`Property details for ${property.title}`}
    >
      {/* Thumbnail */}
      <div className="relative h-32 w-full bg-muted">
        {primaryImage ? (
          <img
            src={primaryImage}
            alt={property.title}
            className="h-full w-full object-cover"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center text-muted-foreground">
            <span className="text-xs">No image available</span>
          </div>
        )}
        <div className="absolute top-2 left-2">
          <Badge variant="secondary" className="bg-background/90 backdrop-blur-xs text-[10px] font-semibold">
            {formatPropertyType(property.property_type)}
          </Badge>
        </div>
      </div>

      {/* Content */}
      <div className="p-3">
        <div className="flex items-baseline justify-between">
          <div className="text-base font-bold text-foreground">
            {formatPrice(property.price)}
          </div>
        </div>

        <h4 className="mt-1 truncate text-xs font-semibold text-foreground" title={property.title}>
          {property.title}
        </h4>

        <div className="mt-1 flex items-center gap-1 text-[11px] text-muted-foreground">
          <MapPin className="h-3 w-3 shrink-0 text-emerald-600" />
          <span className="truncate">{property.locality}, {property.city}</span>
        </div>

        {/* Specs Row */}
        <div className="mt-2 flex items-center gap-2 border-t border-border/60 pt-2 text-[11px] text-muted-foreground">
          {property.bedrooms && (
            <div className="flex items-center gap-0.5">
              <Bed className="h-3 w-3" />
              <span>{formatBedrooms(property.bedrooms)}</span>
            </div>
          )}
          {property.bathrooms && (
            <div className="flex items-center gap-0.5">
              <Bath className="h-3 w-3" />
              <span>{formatBathrooms(property.bathrooms)}</span>
            </div>
          )}
          {property.area_sqft && (
            <div className="flex items-center gap-0.5 ml-auto">
              <Maximize2 className="h-3 w-3" />
              <span>{formatArea(property.area_sqft)}</span>
            </div>
          )}
        </div>

        {/* Action Link */}
        <div className="mt-3">
          <Link href={`/properties/${property.id}`} className="w-full">
            <Button size="sm" className="w-full h-7 text-xs gap-1">
              <span>View Property</span>
              <ArrowRight className="h-3 w-3" />
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
