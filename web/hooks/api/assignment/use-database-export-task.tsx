import { api, fetchClient } from "@/utils/api";
import { useTask, UseTaskOptions } from "../use-task";
import { useCallback } from "react";
import { toast } from "sonner";

export function useDatabaseExportTask(
  assignmentId: number,
  options: UseTaskOptions
) {
  // Create handler to download the export result.
  const downloadExportedData = useCallback(async () => {
    const { data } = await fetchClient.GET(
      "/api/assignment/{assignment_id}/export-result",
      {
        params: {
          path: {
            assignment_id: assignmentId,
          },
        },
        parseAs: "blob", // Ensure we parse the response as a blob for file download
      }
    );
    if (!data) {
      toast.error("Failed to download export file.", {
        description: "Please try again later.",
      });
      return;
    }

    const url = window.URL.createObjectURL(data);
    const a = document.createElement("a");
    a.href = url;
    a.download = `assignment-export.zip`;
    document.body.appendChild(a);
    a.click();
    a.remove();
  }, [assignmentId]);

  const {
    launchTask: launchDatabaseExportTask,
    isTaskRunning: isExportingDatabase,
  } = useTask(
    api.useMutation("put", "/api/assignment/{assignment_id}/export"),
    {
      ...options,
      onSuccess: () => {
        // Download the exported database file
        options.onSuccess?.();
        downloadExportedData();
      },
    }
  );

  return { launchDatabaseExportTask, isExportingDatabase };
}
