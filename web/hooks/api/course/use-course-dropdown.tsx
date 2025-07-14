import { api } from "@/utils/api";

export function useCourseDropdown(
  debouncedSearch: string,
  initialCourseId?: number,
  selectedCourseId?: string
) {
  const { data: dropdownData } = api.useQuery(
    "get",
    "/api/course/dropdown",
    {
      params: {
        query: { search: debouncedSearch, selected_course_id: initialCourseId },
      },
    },
    { placeholderData: (prev) => prev }
  );

  const courses = Object.values(dropdownData?.courses || {}).flat();

  const selectedCourse =
    !!dropdownData &&
    !!dropdownData.selected_course &&
    initialCourseId === dropdownData?.selected_course.id
      ? dropdownData?.selected_course
      : courses.find((course) => `${course.id}` === selectedCourseId);

  return {
    dropdownData,
    selectedCourse,
  };
}
