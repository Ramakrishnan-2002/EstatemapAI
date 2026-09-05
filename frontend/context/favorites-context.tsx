"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { Property } from "@/types";

interface FavoritesContextType {
  savedProperties: Property[];
  savedIds: number[];
  isLoaded: boolean;
  toggleSave: (property: Property) => boolean;
  isSaved: (propertyId: number | string) => boolean;
  removeSave: (propertyId: number | string) => void;
  clearSaved: () => void;
}

const FavoritesContext = createContext<FavoritesContextType | undefined>(undefined);

const STORAGE_KEY = "estatemap_saved_properties";
const EVENT_NAME = "estatemap-favorites-changed";

export function FavoritesProvider({ children }: { children: React.ReactNode }) {
  const [savedProperties, setSavedProperties] = useState<Property[]>([]);
  const [isLoaded, setIsLoaded] = useState<boolean>(false);

  const loadFromStorage = useCallback(() => {
    if (typeof window === "undefined") return;
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        if (Array.isArray(parsed)) {
          setSavedProperties(parsed);
        } else {
          setSavedProperties([]);
        }
      } else {
        setSavedProperties([]);
      }
    } catch {
      setSavedProperties([]);
    } finally {
      setIsLoaded(true);
    }
  }, []);

  // Load from localStorage on mount and listen to storage events
  useEffect(() => {
    loadFromStorage();

    const handleStorageChange = () => {
      loadFromStorage();
    };

    window.addEventListener("storage", handleStorageChange);
    window.addEventListener(EVENT_NAME, handleStorageChange);

    return () => {
      window.removeEventListener("storage", handleStorageChange);
      window.removeEventListener(EVENT_NAME, handleStorageChange);
    };
  }, [loadFromStorage]);

  // Sync to localStorage and notify all listeners
  const saveToStorage = (props: Property[]) => {
    setSavedProperties(props);
    if (typeof window !== "undefined") {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(props));
        window.dispatchEvent(new Event(EVENT_NAME));
      } catch {
        // Ignore localStorage write errors
      }
    }
  };

  const isSaved = (propertyId: number | string): boolean => {
    const id = Number(propertyId);
    return savedProperties.some((p) => Number(p.id) === id);
  };

  const toggleSave = (property: Property): boolean => {
    if (!property || property.id == null) return false;
    const propId = Number(property.id);
    const exists = savedProperties.some((p) => Number(p.id) === propId);

    if (exists) {
      const updated = savedProperties.filter((p) => Number(p.id) !== propId);
      saveToStorage(updated);
      return false;
    } else {
      const updated = [property, ...savedProperties.filter((p) => Number(p.id) !== propId)];
      saveToStorage(updated);
      return true;
    }
  };

  const removeSave = (propertyId: number | string) => {
    const propId = Number(propertyId);
    const updated = savedProperties.filter((p) => Number(p.id) !== propId);
    saveToStorage(updated);
  };

  const clearSaved = () => {
    saveToStorage([]);
  };

  const savedIds = savedProperties.map((p) => Number(p.id));

  return (
    <FavoritesContext.Provider
      value={{
        savedProperties,
        savedIds,
        isLoaded,
        toggleSave,
        isSaved,
        removeSave,
        clearSaved,
      }}
    >
      {children}
    </FavoritesContext.Provider>
  );
}

export function useFavorites() {
  const context = useContext(FavoritesContext);
  if (!context) {
    throw new Error("useFavorites must be used within a FavoritesProvider");
  }
  return context;
}
