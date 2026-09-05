"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  ComparisonResult,
  PropertyComparisonFact,
} from "@/types/comparison";
import {
  Building2,
  Check,
  TrendingDown,
  Maximize2,
  Navigation,
  Sparkles,
  MapPin,
  Hospital,
  GraduationCap,
  Bus,
  ChevronRight,
  Eye,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { formatPropertyType } from "@/lib/formatters/property";

interface ComparisonTableProps {
  comparison: ComparisonResult;
  className?: string;
}

export function ComparisonTable({ comparison, className }: ComparisonTableProps) {
  const { properties, best_by_dimension } = comparison;
  const [activeMobileIdx, setActiveMobileIdx] = useState<number>(0);

  const getWinnerBadge = (dimKey: string, label: string) => {
    if (best_by_dimension[dimKey] === label) {
      let text = "Best";
      if (dimKey === "price") text = "Lowest Price";
      if (dimKey === "space") text = "Largest Area";
      if (dimKey === "commute") text = "Fastest Route";
      if (dimKey === "ranking") text = "Top Match";

      return (
        <Badge
          variant="outline"
          className="bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/30 text-[10px] font-bold shrink-0 ml-1.5"
        >
          {text}
        </Badge>
      );
    }
    return null;
  };

  return (
    <div className={`space-y-6 ${className || ""}`}>
      {/* Mobile Selector Tab Bar (visible < md) */}
      <div className="flex md:hidden items-center gap-2 p-1.5 bg-muted/60 rounded-xl overflow-x-auto">
        {properties.map((prop, idx) => (
          <button
            key={prop.id}
            onClick={() => setActiveMobileIdx(idx)}
            className={`flex-1 min-w-[100px] py-2 px-3 rounded-lg text-xs font-semibold transition-all flex items-center justify-center gap-1.5 ${
              activeMobileIdx === idx
                ? "bg-background text-foreground shadow-xs border border-border"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            <span className="w-4 h-4 rounded-full bg-primary/15 text-primary text-[10px] flex items-center justify-center font-bold">
              {prop.label.replace("Property ", "")}
            </span>
            <span className="truncate">{prop.title}</span>
          </button>
        ))}
      </div>

      {/* Desktop Comparison Matrix (md and up) */}
      <div className="hidden md:block overflow-hidden rounded-2xl border border-border shadow-xs bg-card">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-border/80 bg-muted/30">
                <th className="p-4 text-xs font-semibold text-muted-foreground w-1/4">
                  Feature / Dimension
                </th>
                {properties.map((prop) => (
                  <th key={prop.id} className="p-4 w-1/3 min-w-[240px] align-top">
                    <div className="flex items-center justify-between gap-2 mb-2">
                      <div className="flex items-center gap-1.5">
                        <span className="w-6 h-6 rounded-full bg-primary text-primary-foreground text-xs font-bold flex items-center justify-center">
                          {prop.label.replace("Property ", "")}
                        </span>
                        <span className="font-bold text-sm text-foreground">{prop.label}</span>
                      </div>
                      <Badge variant="secondary" className="text-[10px]">
                        {formatPropertyType(prop.property_type)}
                      </Badge>
                    </div>

                    {/* Image */}
                    <div className="relative aspect-[16/9] rounded-xl overflow-hidden bg-muted mb-2.5 border border-border/50">
                      {prop.image_urls && prop.image_urls.length > 0 ? (
                        <img
                          src={prop.image_urls[0]}
                          alt={prop.title}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="flex h-full w-full items-center justify-center text-muted-foreground/60">
                          <Building2 className="h-8 w-8" />
                        </div>
                      )}
                    </div>

                    <Link
                      href={`/properties/${prop.id}`}
                      className="font-medium text-xs text-foreground hover:text-primary transition-colors line-clamp-2"
                      title={prop.title}
                    >
                      {prop.title}
                    </Link>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-border/60 text-xs">
              {/* Price Row */}
              <tr className="hover:bg-muted/10 transition-colors">
                <td className="p-4 font-semibold text-muted-foreground flex items-center gap-1.5">
                  <TrendingDown className="h-3.5 w-3.5 text-primary" />
                  Price (INR)
                </td>
                {properties.map((prop) => (
                  <td key={prop.id} className="p-4 font-semibold text-foreground text-sm">
                    <div className="flex items-center">
                      <span>{prop.price_formatted}</span>
                      {getWinnerBadge("price", prop.label)}
                    </div>
                  </td>
                ))}
              </tr>

              {/* Price per sq.ft. */}
              <tr className="hover:bg-muted/10 transition-colors">
                <td className="p-4 font-semibold text-muted-foreground">Price per sq.ft.</td>
                {properties.map((prop) => (
                  <td key={prop.id} className="p-4 font-mono text-foreground">
                    {prop.price_per_sqft ? `₹${prop.price_per_sqft.toLocaleString()}/sq.ft.` : "—"}
                  </td>
                ))}
              </tr>

              {/* Bedrooms & Bathrooms */}
              <tr className="hover:bg-muted/10 transition-colors">
                <td className="p-4 font-semibold text-muted-foreground">Bedrooms & Bathrooms</td>
                {properties.map((prop) => (
                  <td key={prop.id} className="p-4 text-foreground">
                    {prop.bedrooms ? `${prop.bedrooms} BHK` : "—"}
                    {prop.bathrooms ? ` • ${prop.bathrooms} Baths` : ""}
                  </td>
                ))}
              </tr>

              {/* Area */}
              <tr className="hover:bg-muted/10 transition-colors">
                <td className="p-4 font-semibold text-muted-foreground flex items-center gap-1.5">
                  <Maximize2 className="h-3.5 w-3.5 text-primary" />
                  Living Area
                </td>
                {properties.map((prop) => (
                  <td key={prop.id} className="p-4 text-foreground">
                    <div className="flex items-center">
                      <span>{prop.area_sqft ? `${prop.area_sqft.toLocaleString()} sq.ft.` : "—"}</span>
                      {getWinnerBadge("space", prop.label)}
                    </div>
                  </td>
                ))}
              </tr>

              {/* Locality & Address */}
              <tr className="hover:bg-muted/10 transition-colors">
                <td className="p-4 font-semibold text-muted-foreground flex items-center gap-1.5">
                  <MapPin className="h-3.5 w-3.5 text-primary" />
                  Locality & Address
                </td>
                {properties.map((prop) => (
                  <td key={prop.id} className="p-4 text-foreground">
                    <p className="font-medium">{prop.locality}, {prop.city}</p>
                    <p className="text-muted-foreground text-[11px] truncate mt-0.5">{prop.address}</p>
                  </td>
                ))}
              </tr>

              {/* Commute Time */}
              <tr className="hover:bg-muted/10 transition-colors bg-muted/20">
                <td className="p-4 font-semibold text-muted-foreground flex items-center gap-1.5">
                  <Navigation className="h-3.5 w-3.5 text-primary" />
                  Commute Route
                </td>
                {properties.map((prop) => (
                  <td key={prop.id} className="p-4 text-foreground">
                    {prop.commute_duration_mins != null ? (
                      <div>
                        <div className="flex items-center font-bold text-sm">
                          <span>{prop.commute_duration_mins.toFixed(0)} mins</span>
                          {getWinnerBadge("commute", prop.label)}
                        </div>
                        <p className="text-[11px] text-muted-foreground font-mono mt-0.5">
                          {prop.commute_distance_km?.toFixed(1)} km to {prop.commute_destination}
                        </p>
                      </div>
                    ) : (
                      <span className="text-muted-foreground italic">No destination specified</span>
                    )}
                  </td>
                ))}
              </tr>

              {/* Location Intelligence: Nearest Hospital */}
              <tr className="hover:bg-muted/10 transition-colors">
                <td className="p-4 font-semibold text-muted-foreground flex items-center gap-1.5">
                  <Hospital className="h-3.5 w-3.5 text-primary" />
                  Nearest Hospital
                </td>
                {properties.map((prop) => (
                  <td key={prop.id} className="p-4 text-foreground font-mono">
                    {prop.location_intelligence?.hospital != null
                      ? `${prop.location_intelligence.hospital.toFixed(2)} km`
                      : "—"}
                  </td>
                ))}
              </tr>

              {/* Nearest School */}
              <tr className="hover:bg-muted/10 transition-colors">
                <td className="p-4 font-semibold text-muted-foreground flex items-center gap-1.5">
                  <GraduationCap className="h-3.5 w-3.5 text-primary" />
                  Nearest School
                </td>
                {properties.map((prop) => (
                  <td key={prop.id} className="p-4 text-foreground font-mono">
                    {prop.location_intelligence?.school != null
                      ? `${prop.location_intelligence.school.toFixed(2)} km`
                      : "—"}
                  </td>
                ))}
              </tr>

              {/* Nearest Transit */}
              <tr className="hover:bg-muted/10 transition-colors">
                <td className="p-4 font-semibold text-muted-foreground flex items-center gap-1.5">
                  <Bus className="h-3.5 w-3.5 text-primary" />
                  Nearest Transit
                </td>
                {properties.map((prop) => (
                  <td key={prop.id} className="p-4 text-foreground font-mono">
                    {prop.location_intelligence?.transit != null
                      ? `${prop.location_intelligence.transit.toFixed(2)} km`
                      : "—"}
                  </td>
                ))}
              </tr>

              {/* Ranking Match Score */}
              <tr className="hover:bg-muted/10 transition-colors bg-primary/5">
                <td className="p-4 font-bold text-foreground flex items-center gap-1.5">
                  <Sparkles className="h-4 w-4 text-emerald-500" />
                  Ranking Match Score
                </td>
                {properties.map((prop) => (
                  <td key={prop.id} className="p-4 text-foreground">
                    <div className="flex items-center">
                      <span className="font-bold font-mono text-base text-emerald-600 dark:text-emerald-400">
                        {prop.ranking_score?.toFixed(1)}%
                      </span>
                      {getWinnerBadge("ranking", prop.label)}
                    </div>
                  </td>
                ))}
              </tr>

              {/* Actions */}
              <tr>
                <td className="p-4 font-semibold text-muted-foreground">Action</td>
                {properties.map((prop) => (
                  <td key={prop.id} className="p-4">
                    <Button asChild size="sm" variant="outline" className="w-full text-xs font-semibold">
                      <Link href={`/properties/${prop.id}`}>
                        <span>View Listing</span>
                        <ChevronRight className="ml-1 h-3.5 w-3.5" />
                      </Link>
                    </Button>
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Mobile Single-Card View (< md) */}
      <div className="block md:hidden">
        {(() => {
          const prop = properties[activeMobileIdx] || properties[0];
          if (!prop) return null;

          return (
            <div className="rounded-2xl border border-border shadow-xs bg-card p-4 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-primary text-primary-foreground text-xs font-bold flex items-center justify-center">
                    {prop.label.replace("Property ", "")}
                  </span>
                  <span className="font-bold text-base text-foreground">{prop.label}</span>
                </div>
                <Badge variant="secondary">{formatPropertyType(prop.property_type)}</Badge>
              </div>

              {/* Image */}
              <div className="relative aspect-[16/9] rounded-xl overflow-hidden bg-muted border border-border/50">
                {prop.image_urls && prop.image_urls.length > 0 ? (
                  <img
                    src={prop.image_urls[0]}
                    alt={prop.title}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="flex h-full w-full items-center justify-center text-muted-foreground/60">
                    <Building2 className="h-10 w-10" />
                  </div>
                )}
              </div>

              <div>
                <h4 className="font-semibold text-sm text-foreground">{prop.title}</h4>
                <p className="text-xs text-muted-foreground">{prop.address}, {prop.locality}, {prop.city}</p>
              </div>

              {/* Metrics Grid */}
              <div className="grid grid-cols-2 gap-2.5 pt-2 border-t border-border/60 text-xs">
                <div className="bg-muted/40 p-2.5 rounded-xl">
                  <span className="text-[10px] text-muted-foreground uppercase font-semibold">Price</span>
                  <div className="font-bold text-sm text-foreground mt-0.5">{prop.price_formatted}</div>
                  {getWinnerBadge("price", prop.label)}
                </div>

                <div className="bg-muted/40 p-2.5 rounded-xl">
                  <span className="text-[10px] text-muted-foreground uppercase font-semibold">Living Area</span>
                  <div className="font-bold text-sm text-foreground mt-0.5">
                    {prop.area_sqft ? `${prop.area_sqft.toLocaleString()} sq.ft.` : "—"}
                  </div>
                  {getWinnerBadge("space", prop.label)}
                </div>

                <div className="bg-muted/40 p-2.5 rounded-xl">
                  <span className="text-[10px] text-muted-foreground uppercase font-semibold">Layout</span>
                  <div className="font-semibold text-foreground mt-0.5">
                    {prop.bedrooms ? `${prop.bedrooms} BHK` : "—"} {prop.bathrooms ? `(${prop.bathrooms}B)` : ""}
                  </div>
                </div>

                <div className="bg-muted/40 p-2.5 rounded-xl">
                  <span className="text-[10px] text-muted-foreground uppercase font-semibold">Match Score</span>
                  <div className="font-bold font-mono text-sm text-emerald-600 dark:text-emerald-400 mt-0.5">
                    {prop.ranking_score?.toFixed(1)}%
                  </div>
                  {getWinnerBadge("ranking", prop.label)}
                </div>
              </div>

              {/* Commute summary */}
              {prop.commute_duration_mins != null && (
                <div className="bg-muted/30 p-3 rounded-xl text-xs space-y-1">
                  <span className="text-[10px] font-semibold text-muted-foreground uppercase">Commute Route</span>
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-foreground">{prop.commute_duration_mins.toFixed(0)} mins</span>
                    <span className="font-mono text-muted-foreground">{prop.commute_distance_km?.toFixed(1)} km</span>
                  </div>
                  <p className="text-[11px] text-muted-foreground truncate">To {prop.commute_destination}</p>
                </div>
              )}

              <Button asChild size="sm" className="w-full text-xs font-semibold">
                <Link href={`/properties/${prop.id}`}>
                  <span>View Full Listing</span>
                  <ChevronRight className="ml-1 h-3.5 w-3.5" />
                </Link>
              </Button>
            </div>
          );
        })()}
      </div>
    </div>
  );
}
