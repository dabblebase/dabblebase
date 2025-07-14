import { api } from "@/utils/api";
import { useTask, UseTaskOptions } from "../use-task";

export function usePublishAssignmentTask(options: UseTaskOptions) {
  const {
    launchTask: launchPublishAssignmentTask,
    isTaskRunning: isPublishingAssignment,
  } = useTask(
    api.useMutation("put", "/api/assignment/{assignment_id}/publish"),
    options
  );

  return { launchPublishAssignmentTask, isPublishingAssignment };
}
