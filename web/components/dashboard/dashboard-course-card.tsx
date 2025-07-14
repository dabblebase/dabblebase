import type { components } from "@/models/schema";
import { Card, CardContent } from "../ui/card";
import { useRouter } from "next/router";

type Course = components["schemas"]["GetDashboardResponse_Course"];

export default function DashboardCourseCard({ course }: { course: Course }) {
  const router = useRouter();

  return (
    <Card
      key={course.id}
      onClick={() => router.push(`/course/${course.id}/assignments`)}
      className="w-72 h-36 hover:bg-accent hover:cursor-pointer"
    >
      <CardContent className="flex flex-col gap-0.5">
        <h2 className="text-base font-bold">{course.code}</h2>
        <p className="text-sm font-medium">{course.name}</p>
        <p className="text-sm text-muted-foreground">
          {!!course.num_students && (
            <span>
              {course.num_students} student
              {course.num_students !== 1 ? "s" : ""} •{" "}
            </span>
          )}
          {course.num_assignments} assignment
          {course.num_assignments !== 1 ? "s" : ""}
        </p>
      </CardContent>
    </Card>
  );
}
