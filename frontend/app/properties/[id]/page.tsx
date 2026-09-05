"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  Bath,
  BedDouble,
  Building2,
  Calendar,
  CalendarCheck,
  CheckCircle2,
  Heart,
  Maximize2,
  Phone,
  Scale,
  Share2,
  ShieldCheck,
  UserCheck,
  Video,
  X,
} from "lucide-react";
import { getPropertyById } from "@/lib/api/properties";
import { CommuteResponse, Property } from "@/types";
import { ErrorState, LoadingState } from "@/components/feedback/states";
import { MapContainer } from "@/components/map/map-container";
import { AmenityList } from "@/components/properties/amenity-list";
import { LocationDisplay } from "@/components/properties/location-display";
import { LocationIntelligence } from "@/components/properties/location-intelligence";
import { AIPropertyExplanation } from "@/components/properties/ai-property-explanation";
import { CommutePanel } from "@/components/commute/commute-panel";
import { PriceDisplay } from "@/components/properties/price-display";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { useComparison } from "@/context/comparison-context";
import { useFavorites } from "@/context/favorites-context";
import { formatDate } from "@/lib/formatters/date";
import { formatArea, formatBathrooms, formatBedrooms, formatPropertyType } from "@/lib/formatters/property";

export default function PropertyDetailPage({
  params,
}: {
  params: { id: string };
}) {
  const propertyId = parseInt(params.id, 10);
  const [property, setProperty] = useState<Property | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [activeCommuteRoute, setActiveCommuteRoute] = useState<CommuteResponse | null>(null);

  // Comparison and Favorites contexts
  const { toggleCompare, isCompared } = useComparison();
  const { toggleSave, isSaved } = useFavorites();

  // Contact Modal State
  const [showContactModal, setShowContactModal] = useState<boolean>(false);
  const [contactForm, setContactForm] = useState({
    name: "",
    phone: "",
    email: "",
    message: "Hi, I am interested in this property. Please share additional details or arrange a callback.",
  });
  const [contactSubmitted, setContactSubmitted] = useState<boolean>(false);

  // Schedule Modal State
  const [showScheduleModal, setShowScheduleModal] = useState<boolean>(false);
  const [scheduleForm, setScheduleForm] = useState({
    date: new Date(Date.now() + 86400000).toISOString().split("T")[0],
    timeSlot: "10:00 AM - 12:00 PM",
    mode: "in_person" as "in_person" | "video",
    name: "",
    phone: "",
    notes: "",
  });
  const [scheduleSubmitted, setScheduleSubmitted] = useState<boolean>(false);

  useEffect(() => {
    if (isNaN(propertyId)) {
      setErrorMessage("Invalid property ID provided.");
      setIsLoading(false);
      return;
    }

    getPropertyById(propertyId)
      .then((data) => {
        setProperty(data);
      })
      .catch((err) => {
        setErrorMessage(err instanceof Error ? err.message : "Failed to load property listing.");
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [propertyId]);

  if (isLoading) {
    return <LoadingState title="Loading verified property details..." />;
  }

  if (errorMessage || !property) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-12">
        <ErrorState
          title="Property Listing Unavailable"
          message={errorMessage || "The requested property listing could not be found."}
          onRetry={() => window.location.reload()}
        />
      </div>
    );
  }

  const primaryImage =
    property.images && property.images.length > 0 ? property.images[0].image_url : null;
  const inComparison = isCompared(property.id);

  const handleToggleCompare = () => {
    toggleCompare(property);
  };

  const handleSendContact = (e: React.FormEvent) => {
    e.preventDefault();
    setContactSubmitted(true);
    setTimeout(() => {
      setShowContactModal(false);
      setContactSubmitted(false);
    }, 3000);
  };

  const handleBookSchedule = (e: React.FormEvent) => {
    e.preventDefault();
    setScheduleSubmitted(true);
    setTimeout(() => {
      setShowScheduleModal(false);
      setScheduleSubmitted(false);
    }, 3000);
  };

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Top Navigation & Actions Bar */}
      <div className="mb-6 flex items-center justify-between">
        <Link
          href="/search"
          className="inline-flex items-center gap-1.5 text-xs font-medium text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back to Search</span>
        </Link>
        <div className="flex items-center gap-2">
          {/* Comparison Toggle Button */}
          <Button
            variant={inComparison ? "default" : "outline"}
            size="sm"
            onClick={handleToggleCompare}
            className={`h-8 gap-1.5 text-xs ${
              inComparison
                ? "bg-primary text-primary-foreground font-semibold"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            <Scale className="h-3.5 w-3.5" />
            <span>{inComparison ? "In Comparison" : "Add to Compare"}</span>
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={() => toggleSave(property)}
            className="h-8 gap-1.5 text-xs"
          >
            <Heart className={`h-3.5 w-3.5 ${isSaved(property.id) ? "fill-destructive text-destructive" : ""}`} />
            <span>{isSaved(property.id) ? "Saved" : "Save"}</span>
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              if (navigator.share) {
                navigator.share({ title: property.title, url: window.location.href });
              } else {
                navigator.clipboard.writeText(window.location.href);
              }
            }}
            className="h-8 gap-1.5 text-xs"
          >
            <Share2 className="h-3.5 w-3.5" />
            <span>Share</span>
          </Button>
        </div>
      </div>

      <div className="grid gap-8 lg:grid-cols-3">
        <div className="space-y-8 lg:col-span-2">
          <div className="relative aspect-[16/10] w-full overflow-hidden rounded-xl border border-border bg-muted shadow-sm">
            {primaryImage ? (
              <img src={primaryImage} alt={property.title} className="h-full w-full object-cover" />
            ) : (
              <div className="flex h-full w-full flex-col items-center justify-center bg-muted/60 text-muted-foreground">
                <Building2 className="h-16 w-16 stroke-[1] text-muted-foreground/50" />
                <span className="mt-2 text-sm font-medium">EstateMap Verified Listing</span>
              </div>
            )}
            <div className="absolute left-4 top-4 flex items-center gap-2">
              <Badge variant="secondary" className="bg-background/90 text-xs font-semibold backdrop-blur-md">
                {formatPropertyType(property.property_type)}
              </Badge>
              <Badge variant="success" className="text-xs font-semibold backdrop-blur-md">
                VERIFIED
              </Badge>
            </div>
          </div>

          <div>
            <h1 className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
              {property.title}
            </h1>
            <LocationDisplay locality={property.locality} city={property.city} address={property.address} showAddress className="mt-2 text-sm" />
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 rounded-lg border border-border bg-card p-4 shadow-sm">
            <div className="flex flex-col">
              <span className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider">Bedrooms</span>
              <div className="mt-1 flex items-center gap-1.5 text-sm font-bold text-foreground">
                <BedDouble className="h-4 w-4 text-primary" />
                <span>{formatBedrooms(property.bedrooms)}</span>
              </div>
            </div>
            <div className="flex flex-col">
              <span className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider">Bathrooms</span>
              <div className="mt-1 flex items-center gap-1.5 text-sm font-bold text-foreground">
                <Bath className="h-4 w-4 text-primary" />
                <span>{formatBathrooms(property.bathrooms)}</span>
              </div>
            </div>
            <div className="flex flex-col">
              <span className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider">Carpet Area</span>
              <div className="mt-1 flex items-center gap-1.5 text-sm font-bold text-foreground">
                <Maximize2 className="h-4 w-4 text-primary" />
                <span>{formatArea(property.area_sqft)}</span>
              </div>
            </div>
            <div className="flex flex-col">
              <span className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider">Listed On</span>
              <div className="mt-1 flex items-center gap-1.5 text-sm font-bold text-foreground">
                <Calendar className="h-4 w-4 text-primary" />
                <span>{formatDate(property.created_at)}</span>
              </div>
            </div>
          </div>

          <AIPropertyExplanation
            propertyId={property.id}
            destinationLat={activeCommuteRoute?.destination.latitude}
            destinationLng={activeCommuteRoute?.destination.longitude}
            destinationName={activeCommuteRoute?.destination.name}
          />

          <div className="space-y-3">
            <h2 className="text-lg font-bold tracking-tight text-foreground">About this property</h2>
            <div className="rounded-lg border border-border bg-card p-5 text-sm text-foreground/85 leading-relaxed">
              {property.description || "No description provided for this listing."}
            </div>
          </div>

          {property.amenities && property.amenities.length > 0 && (
            <div className="space-y-3">
              <h2 className="text-lg font-bold tracking-tight text-foreground">Amenities & Facilities</h2>
              <AmenityList amenities={property.amenities} variant="grid" />
            </div>
          )}

          <div className="space-y-3">
            <h2 className="text-lg font-bold tracking-tight text-foreground">Location & Spatial Context</h2>
            <div className="h-72 w-full">
              <MapContainer
                properties={[property]}
                selectedPropertyId={String(property.id)}
                route={
                  activeCommuteRoute && activeCommuteRoute.geometry.coordinates.length >= 2
                    ? {
                        coordinates: activeCommuteRoute.geometry.coordinates,
                        color: "#3b82f6",
                        name: activeCommuteRoute.destination.name,
                      }
                    : null
                }
                latitude={property.latitude}
                longitude={property.longitude}
                zoom={14}
                interactive={true}
              />
            </div>
          </div>

          <CommutePanel
            propertyId={property.id}
            propertyCity={property.city}
            latitude={property.latitude}
            longitude={property.longitude}
            onRouteCalculated={setActiveCommuteRoute}
          />
          <LocationIntelligence propertyId={property.id} />
        </div>

        <div className="space-y-6">
          <Card className="sticky top-20 border-border bg-card shadow-sm">
            <CardHeader className="pb-3">
              <span className="text-xs font-medium text-muted-foreground">Listing Price</span>
              <PriceDisplay price={property.price} areaSqFt={property.area_sqft} size="xl" showRate />
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="rounded-md bg-muted/40 p-3 text-xs text-muted-foreground">
                <div className="flex items-center gap-1.5 font-medium text-foreground">
                  <ShieldCheck className="h-4 w-4 text-emerald-600" />
                  <span>Verified Geographic Coordinates</span>
                </div>
                <div className="mt-1 font-mono text-[11px]">
                  Lat: {property.latitude.toFixed(5)}, Lng: {property.longitude.toFixed(5)}
                </div>
              </div>

              <div className="flex flex-col gap-2 pt-2">
                <Button onClick={() => setShowContactModal(true)} className="w-full font-semibold flex items-center justify-center gap-2 cursor-pointer">
                  <Phone className="h-4 w-4" />
                  <span>Contact Property Owner</span>
                </Button>
                <Button variant="outline" onClick={() => setShowScheduleModal(true)} className="w-full text-xs flex items-center justify-center gap-2 cursor-pointer">
                  <CalendarCheck className="h-4 w-4 text-primary" />
                  <span>Schedule Site Visit</span>
                </Button>
                <Button
                  variant={inComparison ? "secondary" : "outline"}
                  onClick={handleToggleCompare}
                  className="w-full text-xs flex items-center justify-center gap-2 cursor-pointer border-dashed"
                >
                  <Scale className="h-4 w-4 text-primary" />
                  <span>{inComparison ? "Remove from Comparison" : "Add to Comparison"}</span>
                </Button>
              </div>

              <div className="border-t border-border pt-4 text-center text-xs text-muted-foreground">
                <UserCheck className="mx-auto h-4 w-4 text-muted-foreground/60 mb-1" />
                Owner ID: #{property.owner_id} · Direct Listing
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Contact Owner Modal */}
      {showContactModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4 animate-in fade-in duration-200">
          <div className="relative w-full max-w-md rounded-2xl border border-border bg-card p-6 shadow-2xl">
            <button onClick={() => setShowContactModal(false)} className="absolute right-4 top-4 rounded-md p-1 text-muted-foreground hover:text-foreground">
              <X className="h-5 w-5" />
            </button>
            {contactSubmitted ? (
              <div className="flex flex-col items-center justify-center py-6 text-center space-y-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-emerald-500/20 text-emerald-500">
                  <CheckCircle2 className="h-7 w-7" />
                </div>
                <h3 className="text-lg font-bold text-foreground">Inquiry Sent Successfully!</h3>
              </div>
            ) : (
              <div>
                <h3 className="text-base font-bold text-foreground pb-4 border-b border-border">Contact Property Owner</h3>
                <form onSubmit={handleSendContact} className="space-y-3 mt-4">
                  <input type="text" placeholder="Your Name" required value={contactForm.name} onChange={(e) => setContactForm({ ...contactForm, name: e.target.value })} className="w-full rounded-md border border-input bg-background px-3 py-2 text-xs" />
                  <input type="tel" placeholder="Your Mobile Number" required value={contactForm.phone} onChange={(e) => setContactForm({ ...contactForm, phone: e.target.value })} className="w-full rounded-md border border-input bg-background px-3 py-2 text-xs" />
                  <textarea rows={3} value={contactForm.message} onChange={(e) => setContactForm({ ...contactForm, message: e.target.value })} className="w-full rounded-md border border-input bg-background px-3 py-2 text-xs resize-none" />
                  <Button type="submit" className="w-full font-semibold">Send Inquiry</Button>
                </form>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Schedule Site Visit Modal */}
      {showScheduleModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4 animate-in fade-in duration-200">
          <div className="relative w-full max-w-md rounded-2xl border border-border bg-card p-6 shadow-2xl">
            <button onClick={() => setShowScheduleModal(false)} className="absolute right-4 top-4 rounded-md p-1 text-muted-foreground hover:text-foreground">
              <X className="h-5 w-5" />
            </button>
            {scheduleSubmitted ? (
              <div className="flex flex-col items-center justify-center py-6 text-center space-y-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/20 text-primary">
                  <CalendarCheck className="h-7 w-7" />
                </div>
                <h3 className="text-lg font-bold text-foreground">Site Visit Requested!</h3>
              </div>
            ) : (
              <div>
                <h3 className="text-base font-bold text-foreground pb-4 border-b border-border">Schedule a Property Visit</h3>
                <form onSubmit={handleBookSchedule} className="space-y-3 mt-4">
                  <div className="grid grid-cols-2 gap-2">
                    <button type="button" onClick={() => setScheduleForm({ ...scheduleForm, mode: "in_person" })} className={`p-2 border rounded-lg text-xs ${scheduleForm.mode === "in_person" ? "border-primary bg-primary/10" : ""}`}>In-Person</button>
                    <button type="button" onClick={() => setScheduleForm({ ...scheduleForm, mode: "video" })} className={`p-2 border rounded-lg text-xs ${scheduleForm.mode === "video" ? "border-primary bg-primary/10" : ""}`}>Video Tour</button>
                  </div>
                  <input type="date" required value={scheduleForm.date} onChange={(e) => setScheduleForm({ ...scheduleForm, date: e.target.value })} className="w-full rounded-md border border-input bg-background px-3 py-2 text-xs" />
                  <input type="text" placeholder="Your Name" required value={scheduleForm.name} onChange={(e) => setScheduleForm({ ...scheduleForm, name: e.target.value })} className="w-full rounded-md border border-input bg-background px-3 py-2 text-xs" />
                  <Button type="submit" className="w-full font-semibold">Confirm Booking</Button>
                </form>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
