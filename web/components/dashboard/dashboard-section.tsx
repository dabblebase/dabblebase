import type { components } from "@/models/schema";
import { useState } from "react";
import { DashboardTermCoursesList } from "./dashboard-course-list";
import { Button } from "../ui/button";
import { ChevronDown, ChevronUp } from "lucide-react";

type Course = components["schemas"]["GetDashboardResponse_Course"];

export function DashboardSection({
  title,
  mostRecentTerm,
  otherTerms,
  courses,
}: {
  title: string;
  mostRecentTerm: string | null | undefined;
  otherTerms: string[] | null | undefined;
  courses: { [key: string]: Course[] };
}) {
  const [showMoreTerms, setShowMoreTerms] = useState(false);

  return (
    <>
      {mostRecentTerm && (
        <>
          <h1 className="text-2xl font-semibold">{title}</h1>
          <DashboardTermCoursesList
            term={mostRecentTerm}
            courses={courses[mostRecentTerm] ?? []}
          />
        </>
      )}
      {otherTerms && otherTerms.length > 0 && (
        <>
          <Button
            variant="ghost"
            className="w-min"
            onClick={() => setShowMoreTerms(!showMoreTerms)}
          >
            {showMoreTerms ? "Hide older courses" : "Show older courses"}
            {showMoreTerms ? (
              <ChevronUp className="pt-0.5 size-4" />
            ) : (
              <ChevronDown className="pt-0.5 size-4" />
            )}
          </Button>
          {showMoreTerms && (
            <>
              {otherTerms.map((term) => (
                <DashboardTermCoursesList
                  key={term}
                  term={term}
                  courses={courses[term] ?? []}
                />
              ))}
            </>
          )}
        </>
      )}
    </>
  );
}
