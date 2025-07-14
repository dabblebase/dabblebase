import { ReactNode } from "react";
import { DashboardHeader } from "../headers/dashboard-header";
import { BreadcrumbItem, BreadcrumbPage } from "../ui/breadcrumb";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div className="[--header-height:calc(--spacing(16))]">
      <DashboardHeader>
        <BreadcrumbItem>
          <BreadcrumbPage>Courses</BreadcrumbPage>
        </BreadcrumbItem>
      </DashboardHeader>
      <div>{children}</div>
    </div>
  );
}
