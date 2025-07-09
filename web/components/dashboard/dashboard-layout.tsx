import { ReactNode } from "react";
import { DashboardHeader } from "../headers/dashboard-header";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div className="[--header-height:calc(--spacing(16))]">
      <DashboardHeader>
        <></>
      </DashboardHeader>
      <div>{children}</div>
    </div>
  );
}
