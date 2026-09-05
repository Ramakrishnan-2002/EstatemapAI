"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { Property } from "@/types";

interface ComparisonContextType {
  selectedProperties: Property[];
  selectedIds: number[];
  toggleCompare: (property: Property) => boolean;
  isCompared: (propertyId: number) => boolean;
  removeCompare: (propertyId: number) => void;
  clearCompare: () => void;
  maxAllowed: number;
}

const ComparisonContext = createContext<ComparisonContextType | undefined>(undefined);

const STORAGE_KEY = "estatemap_compare_properties";
const MAX_COMPARE = 3;

export function ComparisonProvider({ children }: { children: React.ReactNode }) {
  const [selectedProperties, setSelectedProperties] = useState<Property[]>([]);

  // Load from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        if (Array.isArray(parsed)) {
          setSelectedProperties(parsed.slice(0, MAX_COMPARE));
        }
      }
    } catch {
      // Ignore localStorage read errors
    }
  }, []);

  // Sync to localStorage
  const saveToStorage = (props: Property[]) => {
    setSelectedProperties(props);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(props));
    } catch {
      // Ignore localStorage write errors
    }
  };

  const isCompared = (propertyId: number): boolean => {
    return selectedProperties.some((p) => p.id === propertyId);
  };

  const toggleCompare = (property: Property): boolean => {
    if (isCompared(property.id)) {
      saveToStorage(selectedProperties.filter((p) => p.id !== property.id));
      return false;
    } else {
      if (selectedProperties.length >= MAX_COMPARE) {
        return false;
      }
      saveToStorage([...selectedProperties, property]);
      return true;
    }
  };

  const removeCompare = (propertyId: number) => {
    saveToStorage(selectedProperties.filter((p) => p.id !== propertyId));
  };

  const clearCompare = () => {
    saveToStorage([]);
  };

  const selectedIds = selectedProperties.map((p) => p.id);

  return (
    <ComparisonContext.Provider
      value={{
        selectedProperties,
        selectedIds,
        toggleCompare,
        isCompared,
        removeCompare,
        clearCompare,
        maxAllowed: MAX_COMPARE,
      }}
    >
      {children}
    </ComparisonContext.Provider>
  );
}

export function useComparison() {
  const context = useContext(ComparisonContext);
  if (!context) {
    throw new Error("useComparison must be used within a ComparisonProvider");
  }
  return context;
}
