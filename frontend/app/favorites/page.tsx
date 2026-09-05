"use client";

import React from "react";
import Link from "next/link";
import { ArrowLeft, Compass, Heart, Trash2 } from "lucide-react";
import { Property } from "@/types";
import { EmptyState, LoadingState } from "@/components/feedback/states";
import { PropertyGrid } from "@/components/properties/property-grid";
import { Button } from "@/components/ui/button";
import { useFavorites } from "@/context/favorites-context";

export default function FavoritesPage() {
  const { savedProperties, savedIds, isLoaded, removeSave, clearSaved } = useFavorites();

  if (!isLoaded) {
    return <LoadingState title="Loading saved properties..." />;
  }

  return (
    <div className="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <Link
              href="/search"
              className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
            >
              <ArrowLeft className="h-3.5 w-3.5" />
              <span>Back to Map</span>
            </Link>
          </div>
          <h1 className="mt-2 text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
            Saved Properties {savedProperties.length > 0 && `(${savedProperties.length})`}
          </h1>
          <p className="text-xs text-muted-foreground mt-1">
            Keep track of homes, villas, and apartments you are evaluating
          </p>
        </div>

        {savedProperties.length > 0 && (
          <Button
            variant="outline"
            size="sm"
            onClick={clearSaved}
            className="h-8 gap-1.5 text-xs text-muted-foreground hover:text-destructive"
          >
            <Trash2 className="h-3.5 w-3.5" />
            <span>Clear All</span>
          </Button>
        )}
      </div>

      {savedProperties.length === 0 ? (
        <EmptyState
          title="No saved properties yet"
          description="When browsing properties on the map or viewing a property detail page, click the heart icon to save it here for quick access."
          actionLabel="Explore Properties on Map"
          onAction={() => (window.location.href = "/search")}
        />
      ) : (
        <PropertyGrid
          properties={savedProperties}
          savedIds={savedIds}
          onToggleSave={(id) => removeSave(id)}
          columns={3}
        />
      )}
    </div>
  );
}

