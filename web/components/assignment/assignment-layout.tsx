import { ReactNode } from "react";
import { DashboardHeader } from "../headers/dashboard-header";
import { BreadcrumbItem, BreadcrumbSeparator } from "../ui/breadcrumb";
import { SidebarInset, SidebarProvider } from "../ui/sidebar";
import { useRouter } from "next/router";
import CourseSelector from "../course/course-selector";
import { SlashIcon } from "lucide-react";
import AssignmentSelector from "./assignment-selector";
import { useCourseRole } from "@/hooks/api/course/use-course-role";
import AssignmentSidebar from "./assignment-sidebar";

export default function AssignmentLayout({
  children,
}: {
  children: ReactNode;
}) {
  const router = useRouter();
  const { courseId, assignmentId } = router.query;

  const { courseRoleData } = useCourseRole(courseId as unknown as number);

  const header = (
    <DashboardHeader>
      <BreadcrumbItem>
        <CourseSelector
          initialCourseId={courseId ? Number(courseId) : undefined}
          disableSelect={true}
        />
      </BreadcrumbItem>
      <BreadcrumbSeparator>
        <SlashIcon className="size-4 mx-1" />
      </BreadcrumbSeparator>
      <AssignmentSelector
        courseId={Number(courseId)}
        initialAssignmentId={assignmentId ? Number(assignmentId) : undefined}
      />
    </DashboardHeader>
  );

  // If the user is a student for the course, show the assignment sidebar.
  if (!!courseRoleData && courseRoleData.role === "student") {
    return (
      <div className="[--header-height:calc(--spacing(16))]">
        <SidebarProvider className="flex flex-col">
          {/* Header */}
          {header}
          {/* Inset */}
          <div className="flex flex-1">
            {/* Sidebar */}
            <AssignmentSidebar />
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

  // Otherwise, show the regular layout with just the header.
  return (
    <div className="[--header-height:calc(--spacing(16))]">
      {/* Header */}
      {header}
      <div>{children}</div>
    </div>
  );
}
