/**
 * Helper hook that manages the lifecycle of a task request.
 *
 * Task requests are used to perform asynchronous operations in the background.
 * There is an API that kicks off the task which returns a task ID, then we
 * poll the status of the task until it is complete. Once the task is complete,
 * we can respond to the success or failure of the task.
 *
 * Usage:
 * ```ts
 * const { launchTask, isTaskRunning } = useTask(
 *   api.useMutation("post", "/api/task/launch"),
 *   {
 *    onSuccess: () => {...}
 *    onStartingTaskError: () => {...}
 *    onTaskError: () => {...}
 *   }
 * );
 * ```
 */

import { api } from "@/utils/api";
import { UseMutationResult } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import type { components } from "@/models/schema";

type TaskResponse = components["schemas"]["Task"];

export type UseTaskOptions = {
  onSuccess?: () => void;
  onStartingTaskError?: () => void;
  onTaskError?: () => void;
};

export function useTask<
  TData extends TaskResponse = TaskResponse,
  TError = unknown,
  TVariables = void,
  TContext = unknown
>(
  launchTaskMutator: UseMutationResult<TData, TError, TVariables, TContext>,
  options: UseTaskOptions
) {
  // Variable to store the state of the task.
  const [isTaskRunning, setIsTaskRunning] = useState(false);

  // Stores the task ID for the launched task if the task is running.
  const [taskId, setTaskId] = useState<string | null>(null);

  // Mutation hook which launches the task.
  const { mutate: launchTaskMutate } = launchTaskMutator;

  // Query hook for polling the status of the task.
  const { data: taskStatus } = api.useQuery(
    "get",
    "/api/task/{task_id}/status",
    {
      params: {
        path: {
          task_id: taskId!,
        },
      },
    },
    {
      enabled: !!taskId, // Only run this query if we have a task ID to poll.
      refetchInterval: 1000,
    }
  );

  // Respond to changes in the task status.
  useEffect(() => {
    if (taskStatus && taskStatus.status === "SUCCESS") {
      setIsTaskRunning(false);
      setTaskId(null);
      if (options.onSuccess) options.onSuccess();
    }
    if (
      taskStatus &&
      (taskStatus.status === "FAILURE" ||
        taskStatus.status === "REVOKED" ||
        taskStatus.status === "IGNORED")
    ) {
      setIsTaskRunning(false);
      setTaskId(null);
      if (options.onTaskError) options.onTaskError();
    }
  }, [taskStatus, options]);

  return {
    launchTask: (variables: TVariables) => {
      setIsTaskRunning(true);
      launchTaskMutate(variables, {
        onSuccess: (response) => {
          setTaskId(response.task_id); // Store the task ID for polling.
        },
        onError: () => {
          setIsTaskRunning(false);
          setTaskId(null);
          if (options.onStartingTaskError) options.onStartingTaskError();
        },
      });
    },
    isTaskRunning,
  };
}
