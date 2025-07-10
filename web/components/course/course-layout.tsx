import { ReactNode } from "react";
import { DashboardHeader } from "../headers/dashboard-header";
import { BreadcrumbItem } from "../ui/breadcrumb";
import { SidebarInset, SidebarProvider } from "../ui/sidebar";
import CourseSidebar from "./course-sidebar";
import CourseSelector from "./course-selector";
import { useRouter } from "next/router";

export default function CourseLayout({ children }: { children: ReactNode }) {
  const router = useRouter();
  const { id } = router.query;

  return (
    <div className="[--header-height:calc(--spacing(16))]">
      <SidebarProvider className="flex flex-col">
        {/* Header */}
        <DashboardHeader>
          <BreadcrumbItem>
            <CourseSelector initialCourseId={id ? Number(id) : undefined} />
          </BreadcrumbItem>
        </DashboardHeader>
        {/* Inset */}
        <div className="flex flex-1">
          {/* Sidebar */}
          <CourseSidebar />
          {/* Content */}
          <SidebarInset>
            <div className="flex flex-1 flex-col">
              <div>{children}</div>
            </div>
          </SidebarInset>
        </div>
      </SidebarProvider>
    </div>
  );
}
