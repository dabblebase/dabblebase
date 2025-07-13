/** Custom component containing a readonly input and copy button */

import { toast } from "sonner";
import { Input } from "./input";
import { Button } from "./button";
import { Copy } from "lucide-react";

export default function CopyText({ text }: { text: string }) {
  return (
    <div className="flex flex-row gap-2 items-center">
      <Input id="link" defaultValue={text} readOnly className="h-9" />
      <Button
        variant="outline"
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
