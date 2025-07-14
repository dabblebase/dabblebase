import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CircleX } from "lucide-react";

export default function SQLTestErrorCard({ error }: { error: string }) {
  return (
    <Card className="flex flex-col gap-2 p-3">
      <CardHeader className="px-2 flex flex-row gap-2 items-center text-destructive">
        <CircleX className="size-4" />
        <CardTitle className="text-sm">Error running SQL</CardTitle>
      </CardHeader>
      <CardContent className="px-2 mt-0">
        <p className="text-sm text-destructive/80">{error}</p>
      </CardContent>
    </Card>
  );
}
