import type { components } from "@/models/schema";
import { Card, CardContent } from "../ui/card";

type Course = components["schemas"]["GetDashboardResponse_Course"];

export function DashboardTermCoursesList({
  term,
  courses,
}: {
  term: string;
  courses: Course[];
}) {
  return (
    <div className="flex flex-col gap-4">
      <p className="text-lg font-bold">{term}</p>
      <div className="flex flex-row gap-4 flex-wrap">
        {courses.map((course) => (
          <Card
            key={course.id}
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
        ))}
      </div>
    </div>
  );
}
