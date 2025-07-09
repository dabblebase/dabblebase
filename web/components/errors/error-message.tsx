import { CircleX } from "lucide-react";

export default function ErrorMessage({ resource }: { resource: string }) {
  return (
    <div className="flex flex-row gap-3 text-destructive">
      <CircleX />
      <div className="flex flex-col">
        <p className="font-semibold">Error loading {resource}.</p>
      </div>
    </div>
  );
}
