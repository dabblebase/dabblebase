import { api } from "@/utils/api";
import { useTask, UseTaskOptions } from "../use-task";

export function useDeleteAssignmentTask(options: UseTaskOptions) {
  const {
    launchTask: launchDeleteAssignmentTask,
    isTaskRunning: isDeletingAssignment,
  } = useTask(
    api.useMutation("delete", "/api/assignment/{assignment_id}"),
    options
  );

  return { launchDeleteAssignmentTask, isDeletingAssignment };
}
