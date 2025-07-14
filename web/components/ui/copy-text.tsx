/** Custom component containing a readonly input and copy button */

import { toast } from "sonner";
import { Input } from "./input";
import { Button } from "./button";
import { Copy } from "lucide-react";
import { cn } from "@/utils/cn";

type ButtonVariant =
  | "outline"
  | "link"
  | "default"
  | "destructive"
  | "secondary"
  | "ghost"
  | null
  | undefined;

export default function CopyText({
  className,
  text,
  buttonVariant = "outline",
}: {
  text: string;
  className?: string;
  buttonVariant?: ButtonVariant;
}) {
  return (
    <div className={cn("flex flex-row gap-2 items-center", className)}>
      <Input id="link" defaultValue={text} readOnly className="h-9" />
      <Button
        variant={buttonVariant}
        type="submit"
        size="sm"
        className="px-3"
        onClick={() => {
          navigator.clipboard.writeText(text);
          toast.success("Database URL copied to clipboard");
        }}
      >
        <span className="sr-only">Copy</span>
        <Copy />
      </Button>
    </div>
  );
}
