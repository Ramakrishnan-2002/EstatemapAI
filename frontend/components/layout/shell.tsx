import React from "react";
import { cn } from "@/lib/utils";

interface ShellProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  container?: boolean;
}

export function Shell({
  children,
  className,
  container = true,
  ...props
}: ShellProps) {
  return (
    <div
      className={cn(
        "flex flex-1 flex-col py-6",
        container && "mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}
