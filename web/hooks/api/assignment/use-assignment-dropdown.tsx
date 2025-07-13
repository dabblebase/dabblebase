import { api } from "@/utils/api";

export function useAssignmentDropdown(
  courseId: number,
  debouncedSearch: string,
  initialAssignmentId?: number,
  selectedAssignmentId?: string
) {
  const { data: dropdownData } = api.useQuery(
    "get",
    "/api/assignment/dropdown",
    {
      params: {
        query: {
          search: debouncedSearch,
          course_id: courseId,
          selected_assignment_id: initialAssignmentId,
        },
      },
    },
    { placeholderData: (prev) => prev }
  );

  const assignments = Object.values(dropdownData?.assignments || {}).flat();

  const selectedAssignment =
    !!dropdownData &&
    !!dropdownData.selected_assignment &&
    initialAssignmentId === dropdownData?.selected_assignment.id
      ? dropdownData?.selected_assignment
      : assignments.find(
          (assignment) => `${assignment.id}` === selectedAssignmentId
        );

  return {
    dropdownData,
    selectedAssignment,
  };
}
