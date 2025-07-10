import type { components } from "@/models/schema";
import DashboardCourseCard from "./dashboard-course-card";

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
          <DashboardCourseCard key={course.id} course={course} />
        ))}
      </div>
    </div>
  );
}
