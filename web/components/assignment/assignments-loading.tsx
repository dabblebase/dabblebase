import { Skeleton } from "../ui/skeleton";

export function AssignmentsLoading() {
  return (
    <>
      <div className="flex flex-row gap-4 flex-wrap">
        <Skeleton className="w-72 h-36 rounded-xl" />
        <Skeleton className="w-72 h-36 rounded-xl" />
        <Skeleton className="w-72 h-36 rounded-xl" />
      </div>
    </>
  );
}
