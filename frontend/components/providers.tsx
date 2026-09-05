"use client";

import React, { useState } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { ComparisonProvider } from "@/context/comparison-context";
import { FavoritesProvider } from "@/context/favorites-context";

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000,
            refetchOnWindowFocus: false,
            retry: 1,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      <FavoritesProvider>
        <ComparisonProvider>{children}</ComparisonProvider>
      </FavoritesProvider>
    </QueryClientProvider>
  );
}
