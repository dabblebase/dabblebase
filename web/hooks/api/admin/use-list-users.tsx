import { api } from "@/utils/api";

export function useListUsers() {
  const {
    data: usersData,
    isLoading: usersLoading,
    error: usersError,
  } = api.useQuery("get", "/api/admin/users");

  const noUsersFound = !!usersData && usersData.users.length === 0;

  return {
    usersData,
    usersLoading,
    usersError,
    noUsersFound,
  };
}
