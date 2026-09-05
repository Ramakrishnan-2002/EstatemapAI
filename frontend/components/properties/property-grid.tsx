import React from "react";
import { Property, RankedPropertyItem } from "@/types";
import { EmptyState } from "@/components/feedback/states";
import { PropertyCard } from "@/components/properties/property-card";
import { RankedPropertyCard } from "@/components/properties/ranked-property-card";
import { PropertyCardSkeleton } from "@/components/properties/property-card-skeleton";
import { cn } from "@/lib/utils";

interface PropertyGridProps {
  properties?: Property[];
  rankedItems?: RankedPropertyItem[];
  isLoading?: boolean;
  skeletonCount?: number;
  savedIds?: number[];
  selectedPropertyId?: string | number | null;
  hoveredPropertyId?: string | number | null;
  onSelectProperty?: (property: Property) => void;
  onHoverProperty?: (property: Property | null) => void;
  onToggleSave?: (propertyId: number, e: React.MouseEvent) => void;
  className?: string;
  columns?: 1 | 2 | 3 | 4;
}

export function PropertyGrid({
  properties = [],
  rankedItems,
  isLoading = false,
  skeletonCount = 6,
  savedIds = [],
  selectedPropertyId,
  hoveredPropertyId,
  onSelectProperty,
  onHoverProperty,
  onToggleSave,
  className,
  columns = 3,
}: PropertyGridProps) {
  const columnClasses = {
    1: "grid-cols-1",
    2: "grid-cols-1 sm:grid-cols-2",
    3: "grid-cols-1 sm:grid-cols-2 lg:grid-cols-3",
    4: "grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4",
  };

  if (isLoading) {
    return (
      <div className={cn("grid gap-5", columnClasses[columns], className)}>
        {Array.from({ length: skeletonCount }).map((_, idx) => (
          <PropertyCardSkeleton key={idx} />
        ))}
      </div>
    );
  }

  const isRanked = Boolean(rankedItems && rankedItems.length > 0);
  const totalItems = isRanked ? rankedItems!.length : properties.length;

  if (totalItems === 0) {
    return (
      <EmptyState
        title="No properties listed"
        description="No properties matching your criteria were found in this area."
      />
    );
  }

  if (isRanked && rankedItems) {
    return (
      <div className={cn("grid gap-5", columnClasses[columns], className)}>
        {rankedItems.map((item) => (
          <RankedPropertyCard
            key={item.property.id}
            item={item}
            isSaved={savedIds.includes(item.property.id)}
            isSelected={String(item.property.id) === String(selectedPropertyId)}
            isHovered={String(item.property.id) === String(hoveredPropertyId)}
            onSelect={onSelectProperty}
            onMouseEnter={onHoverProperty}
            onMouseLeave={() => onHoverProperty?.(null)}
            onToggleSave={onToggleSave}
          />
        ))}
      </div>
    );
  }

  return (
    <div className={cn("grid gap-5", columnClasses[columns], className)}>
      {properties.map((property) => (
        <PropertyCard
          key={property.id}
          property={property}
          isSaved={savedIds.includes(property.id)}
          isSelected={String(property.id) === String(selectedPropertyId)}
          isHovered={String(property.id) === String(hoveredPropertyId)}
          onSelect={onSelectProperty}
          onMouseEnter={onHoverProperty}
          onMouseLeave={() => onHoverProperty?.(null)}
          onToggleSave={onToggleSave}
        />
      ))}
    </div>
  );
}

