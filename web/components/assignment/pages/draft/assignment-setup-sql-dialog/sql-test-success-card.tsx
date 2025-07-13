import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import CopyText from "@/components/ui/copy-text";
import { CircleCheck } from "lucide-react";

export default function SQLTestSuccessCard({ dbUrl }: { dbUrl: string }) {
  return (
    <Card className="flex flex-col gap-2 p-3">
      <CardHeader className="px-2 flex flex-row gap-2 items-center">
        <CircleCheck className="size-4" />
        <CardTitle className="text-sm">Success running SQL</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-2 px-2 mt-0">
        <p className="text-sm text-muted-foreground/80">
          Connect to the database to verify what students will see when they
          first connect to their database.
        </p>
        <p className="text-sm font-medium">Test database URL</p>
        <CopyText text={dbUrl} />
      </CardContent>
    </Card>
  );
}
