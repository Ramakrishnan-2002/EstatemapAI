"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { Building2, Heart, Plus, Search, ShieldCheck, UserCheck } from "lucide-react";
import { getMe } from "@/lib/api/auth";
import { listProperties } from "@/lib/api/properties";
import { Property, User } from "@/types";
import { EmptyState, LoadingState } from "@/components/feedback/states";
import { PropertyGrid } from "@/components/properties/property-grid";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatDate } from "@/lib/formatters/date";

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null);
  const [userListings, setUserListings] = useState<Property[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isUnauthenticated, setIsUnauthenticated] = useState<boolean>(false);

  useEffect(() => {
    getMe()
      .then(async (userData) => {
        setUser(userData);
        const res = await listProperties({ page_size: 20 });
        if (userData && res.items) {
          setUserListings(res.items.filter((p) => p.owner_id === userData.id));
        } else {
          setUserListings([]);
        }
      })
      .catch(() => {
        setIsUnauthenticated(true);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, []);

  if (isLoading) {
    return <LoadingState title="Loading dashboard..." />;
  }

  if (isUnauthenticated || !user) {
    return (
      <div className="mx-auto max-w-md px-4 py-16 text-center">
        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-primary">
          <UserCheck className="h-6 w-6" />
        </div>
        <h1 className="text-xl font-bold text-foreground">Sign In to View Dashboard</h1>
        <p className="mt-2 text-xs text-muted-foreground">
          Please sign in with your EstateMap credentials to view your profile and managed listings.
        </p>
        <div className="mt-6 flex justify-center gap-3">
          <Link href="/login">
            <Button size="sm">Sign In</Button>
          </Link>
          <Link href="/register">
            <Button variant="outline" size="sm">
              Create Account
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8 space-y-8">
      {/* Profile Header */}
      <div className="flex flex-col justify-between gap-4 border-b border-border pb-6 sm:flex-row sm:items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
            Welcome back, {user.full_name || user.email}
          </h1>
          <p className="mt-1 text-xs text-muted-foreground">
            Account verified · Member since {formatDate(user.created_at)}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Link href="/search">
            <Button variant="outline" size="sm" className="h-8 gap-1.5 text-xs">
              <Search className="h-3.5 w-3.5" />
              <span>Explore Listings</span>
            </Button>
          </Link>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid gap-4 sm:grid-cols-3">
        <Card className="border-border bg-card shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-medium text-muted-foreground">
              My Active Listings
            </CardTitle>
            <Building2 className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">{userListings.length}</div>
            <p className="text-[11px] text-muted-foreground mt-0.5">
              Published on spatial discovery map
            </p>
          </CardContent>
        </Card>

        <Card className="border-border bg-card shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-medium text-muted-foreground">
              Saved Favorites
            </CardTitle>
            <Heart className="h-4 w-4 text-destructive" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">0</div>
            <p className="text-[11px] text-muted-foreground mt-0.5">
              Saved residential properties
            </p>
          </CardContent>
        </Card>

        <Card className="border-border bg-card shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-medium text-muted-foreground">
              Account Status
            </CardTitle>
            <ShieldCheck className="h-4 w-4 text-emerald-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">Verified</div>
            <p className="text-[11px] text-muted-foreground mt-0.5">
              {user.is_superuser ? "Platform Administrator" : "Verified User"}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* My Listings Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold tracking-tight text-foreground">
              My Property Listings
            </h2>
            <p className="text-xs text-muted-foreground">
              Manage your published properties and spatial coordinates
            </p>
          </div>
        </div>

        {userListings.length === 0 ? (
          <EmptyState
            title="No properties listed yet"
            description="You have not published any real estate listings yet."
          />
        ) : (
          <PropertyGrid properties={userListings} columns={3} />
        )}
      </div>
    </div>
  );
}

