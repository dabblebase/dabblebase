import { Skeleton } from "../ui/skeleton";

export function DashboardLoading({ title }: { title: string }) {
  return (
    <>
      <h1 className="text-2xl font-semibold">{title}</h1>
      <div className="flex flex-row gap-4 flex-wrap">
        <Skeleton className="w-72 h-36 rounded-xl" />
        <Skeleton className="w-72 h-36 rounded-xl" />
        <Skeleton className="w-72 h-36 rounded-xl" />
      </div>
    </>
  );
}
