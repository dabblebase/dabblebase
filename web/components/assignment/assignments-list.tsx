import type { components } from "@/models/schema";
import AssignmentCard from "./assignment-card";

type Assignment = components["schemas"]["GetAssignmentsResponse_Assignment"];

export function AssignmentsList({
  isStaff,
  assignments,
}: {
  isStaff: boolean;
  assignments: Assignment[];
}) {
  return (
    <div className="flex flex-row gap-4 flex-wrap">
      {assignments.map((assignment) => (
        <AssignmentCard
          key={assignment.id}
          assignment={assignment}
          isStaff={isStaff}
        />
      ))}
    </div>
  );
}
