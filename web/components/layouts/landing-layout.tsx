import { ReactNode } from "react";
import { LandingHeader } from "../headers/landing-header";

export default function LandingLayout({ children }: { children: ReactNode }) {
  return (
    <div className="[--header-height:calc(--spacing(16))]">
      <LandingHeader />
      <div>{children}</div>
    </div>
  );
}
