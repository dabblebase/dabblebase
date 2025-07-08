"use client";
import LogoHeaderSection from "./logo-header-section";

export function LoginHeader() {
  return (
    <header className="bg-background sticky top-0 z-50 flex w-full items-center">
      <div className="flex h-(--header-height) w-full items-center gap-2 px-4">
        <LogoHeaderSection />
      </div>
    </header>
  );
}
