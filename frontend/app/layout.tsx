import type { Metadata } from "next";
import { Header } from "@/components/layout/header";
import { Footer } from "@/components/layout/footer";
import { Providers } from "@/components/providers";
import { ComparisonBar } from "@/components/comparison/comparison-bar";
import "./globals.css";

export const metadata: Metadata = {
  title: "EstateMap AI — Location-First Real Estate Discovery",
  description:
    "Location-first real estate discovery powered by FastAPI, PostGIS, AI and mapcn.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full">
      <body className="flex min-h-full flex-col bg-background text-foreground antialiased selection:bg-primary/20 selection:text-primary">
        <Providers>
          <Header />
          <div className="flex flex-1 flex-col">{children}</div>
          <ComparisonBar />
          <Footer />
        </Providers>
      </body>
    </html>
  );
}

