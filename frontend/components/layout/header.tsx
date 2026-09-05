"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Compass, Heart, LayoutDashboard, LogIn, LogOut, MapPin, Menu, User as UserIcon, X } from "lucide-react";
import { getMe, logout } from "@/lib/api/auth";
import { getStoredToken } from "@/lib/api/client";
import { User } from "@/types";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { useFavorites } from "@/context/favorites-context";

export function Header() {
  const pathname = usePathname();
  const [user, setUser] = useState<User | null>(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { savedProperties } = useFavorites();

  useEffect(() => {
    const token = getStoredToken();
    if (token) {
      getMe()
        .then((userData) => setUser(userData))
        .catch(() => {
          logout();
          setUser(null);
        });
    }
  }, [pathname]);

  const handleLogout = () => {
    logout();
    setUser(null);
    window.location.href = "/";
  };

  const navLinks = [
    { href: "/search", label: "Explore Map", icon: Compass },
    { href: "/favorites", label: "Saved", icon: Heart },
    { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  ];

  return (
    <header className="sticky top-0 z-40 w-full border-b border-border/80 bg-background/95 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Brand Logo */}
        <Link href="/" className="flex items-center gap-2.5 transition-opacity hover:opacity-90">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground shadow-sm">
            <MapPin className="h-4 w-4" />
          </div>
          <div className="flex flex-col">
            <span className="font-bold text-base tracking-tight text-foreground">
              EstateMap <span className="text-primary font-semibold text-xs">AI</span>
            </span>
          </div>
        </Link>

        {/* Desktop Navigation Links */}
        <nav className="hidden md:flex items-center gap-6">
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = pathname === link.href || (link.href !== "/" && pathname.startsWith(link.href));
            return (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  "flex items-center gap-1.5 text-sm font-medium transition-colors hover:text-primary",
                  isActive ? "text-primary font-semibold" : "text-muted-foreground"
                )}
              >
                <Icon className="h-4 w-4" />
                <span>{link.label}</span>
                {link.href === "/favorites" && savedProperties.length > 0 && (
                  <span className="flex h-4 min-w-4 items-center justify-center rounded-full bg-destructive px-1 text-[10px] font-bold text-destructive-foreground">
                    {savedProperties.length}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Desktop User Account Action */}
        <div className="hidden md:flex items-center gap-3">
          {user ? (
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 rounded-full border border-border bg-card px-3 py-1 text-xs font-medium text-foreground">
                <UserIcon className="h-3.5 w-3.5 text-primary" />
                <span className="max-w-[120px] truncate">{user.full_name || user.email}</span>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleLogout}
                className="h-8 gap-1 text-xs text-muted-foreground hover:text-destructive"
              >
                <LogOut className="h-3.5 w-3.5" />
                <span>Sign Out</span>
              </Button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link href="/login">
                <Button variant="ghost" size="sm" className="h-8 text-xs font-medium">
                  <LogIn className="mr-1 h-3.5 w-3.5" />
                  Sign In
                </Button>
              </Link>
              <Link href="/register">
                <Button size="sm" className="h-8 text-xs font-medium">
                  Register
                </Button>
              </Link>
            </div>
          )}
        </div>

        {/* Mobile Menu Toggle Button */}
        <button
          type="button"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="flex md:hidden h-9 w-9 items-center justify-center rounded-md border border-border text-foreground hover:bg-muted"
          aria-label="Toggle navigation menu"
        >
          {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {/* Mobile Navigation Drawer */}
      {mobileMenuOpen && (
        <div className="border-b border-border bg-card px-4 py-4 md:hidden animate-in slide-in-from-top-2">
          <nav className="flex flex-col gap-3">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={cn(
                    "flex items-center gap-2.5 rounded-md px-3 py-2 text-sm font-medium transition-colors hover:bg-accent",
                    isActive ? "bg-primary/10 text-primary font-semibold" : "text-foreground"
                  )}
                >
                  <Icon className="h-4 w-4" />
                  <span>{link.label}</span>
                  {link.href === "/favorites" && savedProperties.length > 0 && (
                    <span className="ml-auto flex h-4 min-w-4 items-center justify-center rounded-full bg-destructive px-1 text-[10px] font-bold text-destructive-foreground">
                      {savedProperties.length}
                    </span>
                  )}
                </Link>
              );
            })}

            <div className="my-2 border-t border-border" />

            {user ? (
              <div className="flex flex-col gap-2">
                <div className="px-3 text-xs text-muted-foreground">
                  Signed in as <span className="font-semibold text-foreground">{user.email}</span>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    handleLogout();
                    setMobileMenuOpen(false);
                  }}
                  className="justify-start text-xs text-destructive hover:bg-destructive/10"
                >
                  <LogOut className="mr-2 h-3.5 w-3.5" />
                  Sign Out
                </Button>
              </div>
            ) : (
              <div className="flex flex-col gap-2">
                <Link href="/login" onClick={() => setMobileMenuOpen(false)}>
                  <Button variant="outline" size="sm" className="w-full text-xs">
                    Sign In
                  </Button>
                </Link>
                <Link href="/register" onClick={() => setMobileMenuOpen(false)}>
                  <Button size="sm" className="w-full text-xs">
                    Create Account
                  </Button>
                </Link>
              </div>
            )}
          </nav>
        </div>
      )}
    </header>
  );
}
