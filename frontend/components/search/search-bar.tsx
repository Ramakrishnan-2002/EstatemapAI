"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { MapPin, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

interface SearchBarProps {
  initialValue?: string;
  placeholder?: string;
  className?: string;
  onSearch?: (query: string) => void;
  size?: "default" | "lg";
}

export function SearchBar({
  initialValue = "",
  placeholder = "Search by city, locality or project (e.g. Bengaluru, Whitefield)...",
  className,
  onSearch,
  size = "default",
}: SearchBarProps) {
  const router = useRouter();
  const [query, setQuery] = useState(initialValue);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = query.trim();
    if (onSearch) {
      onSearch(trimmed);
    } else if (trimmed) {
      router.push(`/search?locality=${encodeURIComponent(trimmed)}`);
    } else {
      router.push("/search");
    }
  };

  const isLarge = size === "lg";

  return (
    <form
      onSubmit={handleSubmit}
      className={cn(
        "relative flex w-full items-center rounded-lg border border-border bg-card shadow-sm transition-all focus-within:border-primary focus-within:ring-2 focus-within:ring-ring/20",
        isLarge ? "p-1.5" : "p-1",
        className
      )}
    >
      <div className="flex items-center pl-3 text-muted-foreground">
        <MapPin className={cn(isLarge ? "h-5 w-5 text-primary" : "h-4 w-4")} />
      </div>
      <Input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder={placeholder}
        className={cn(
          "border-0 bg-transparent px-3 shadow-none focus-visible:ring-0 focus-visible:ring-offset-0",
          isLarge ? "h-11 text-base placeholder:text-muted-foreground/70" : "h-9 text-sm"
        )}
      />
      <Button
        type="submit"
        size={isLarge ? "lg" : "default"}
        className={cn(
          "shrink-0 gap-1.5 font-medium shadow-none",
          isLarge ? "h-11 px-6 text-sm" : "h-8 px-3 text-xs"
        )}
      >
        <Search className="h-4 w-4" />
        <span>Search</span>
      </Button>
    </form>
  );
}
