import { ReactNode } from "react";
import { DashboardHeader } from "../headers/dashboard-header";
import { BreadcrumbItem, BreadcrumbSeparator } from "../ui/breadcrumb";
import { SidebarInset, SidebarProvider } from "../ui/sidebar";
import { useRouter } from "next/router";
import CourseSelector from "../course/course-selector";
import CourseSidebar from "../course/course-sidebar";
import { SlashIcon } from "lucide-react";
import AssignmentSelector from "./assignment-selector";

export default function AssignmentLayout({
  children,
}: {
  children: ReactNode;
}) {
  const router = useRouter();
  const { courseId, assignmentId } = router.query;

  return (
    <div className="[--header-height:calc(--spacing(16))]">
      <SidebarProvider className="flex flex-col">
        {/* Header */}
        <DashboardHeader>
          <BreadcrumbItem>
            <CourseSelector
              initialCourseId={courseId ? Number(courseId) : undefined}
            />
          </BreadcrumbItem>
          <BreadcrumbSeparator>
            <SlashIcon className="size-4 mx-1" />
          </BreadcrumbSeparator>
          <AssignmentSelector
            courseId={Number(courseId)}
            initialAssignmentId={
              assignmentId ? Number(assignmentId) : undefined
            }
          />
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
