import { api } from "@/utils/api";
import { useQueryClient } from "@tanstack/react-query";

export function useConfigurationSql(assignmentId: number) {
  const queryClient = useQueryClient();

  const { data: sqlData, isLoading: sqlDataLoading } = api.useQuery(
    "get",
    "/api/assignment/{assignment_id}/configuration-sql",
    {
      params: {
        path: {
          assignment_id: assignmentId,
        },
      },
    }
  );

  const { mutate: testConfigurationSQL } = api.useMutation(
    "put",
    "/api/assignment/{assignment_id}/configuration-sql/test"
  );

  const { mutate: saveConfigurationSQL } = api.useMutation(
    "put",
    "/api/assignment/{assignment_id}/configuration-sql/save"
  );

  const { mutate: removeConfigurationSQL } = api.useMutation(
    "put",
    "/api/assignment/{assignment_id}/configuration-sql/remove"
  );

  const { mutate: resetConfigurationSQL } = api.useMutation(
    "put",
    "/api/assignment/{assignment_id}/configuration-sql/reset"
  );

  const refetchOnSuccess = () => {
    queryClient.refetchQueries({
      queryKey: ["get", "/api/assignment/{assignment_id}/configuration-sql"],
    });
  };

  return {
    sqlData,
    sqlDataLoading,
    testConfigurationSQL,
    saveConfigurationSQL,
    removeConfigurationSQL,
    resetConfigurationSQL,
    refetchOnSuccess,
  };
}
