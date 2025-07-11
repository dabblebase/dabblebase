import type { components } from "@/models/schema";
import { Card, CardContent } from "../ui/card";
import { Badge } from "../ui/badge";
import { useRouter } from "next/router";

type Assignment = components["schemas"]["GetAssignmentsResponse_Assignment"];

export default function AssignmentCard({
  courseId,
  isStaff,
  assignment,
}: {
  courseId: number;
  isStaff: boolean;
  assignment: Assignment;
}) {
  const router = useRouter();

  return (
    <Card
      key={assignment.id}
      onClick={() =>
        router.push(`/course/${courseId}/assignment/${assignment.id}`)
      }
      className="w-72 h-36 hover:bg-accent hover:cursor-pointer"
    >
      <CardContent className="flex flex-col gap-0.5">
        <h2 className="text-base font-bold">{assignment.name}</h2>
        <p className="text-sm text-muted-foreground">
          {assignment.is_group ? "Group assignment" : "Individual assignment"}
        </p>
        {isStaff && (
          <div className="mt-2">
            {assignment.state === "draft" && (
              <Badge variant="outline">Draft</Badge>
            )}
            {assignment.state === "published" && (
              <Badge variant="default">Published</Badge>
            )}
            {assignment.state === "unpublished" && (
              <Badge variant="secondary" className="bg-accent">
                Unpublished
              </Badge>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
