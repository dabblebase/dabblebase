/** Custom rename component. */

import { useFocusOnCondition } from "@/hooks/ui/use-focus-on-condition";
import { useState } from "react";
import { Input } from "./input";
import { Button } from "./button";
import { Check, Pencil, X } from "lucide-react";
import { cn } from "@/utils/cn";

type RenameComponentProps = {
  initialValue: string;
  value: string;
  setValue: (value: string) => void;
  placeholder?: string;
  onRename: (setRenaming: (renaming: boolean) => void) => void;
  inputWidth?: string;
  customNameClassName?: string;
  // Define any props that you need for the RenameComponent
};

export default function RenameComponent({
  initialValue,
  value,
  setValue,
  placeholder,
  onRename,
  inputWidth = "300px",
  customNameClassName = "",
}: RenameComponentProps) {
  const [renaming, setRenaming] = useState(false);
  const inputRef = useFocusOnCondition<HTMLInputElement>(renaming);

  return (
    <div className="flex flex-row items-center gap-4">
      {renaming ? (
        <>
          <Input
            ref={inputRef}
            className={`w-[${inputWidth}]`}
            type="text"
            placeholder={placeholder}
            value={value}
            onChange={(e) => setValue(e.target.value)}
          />
          <div className="flex flex-row gap-2">
            <Button
              variant="outline"
              size="icon"
              onClick={() => {
                setRenaming(false);
                setValue(initialValue);
              }}
            >
              <X />
            </Button>
            <Button
              variant="default"
              size="icon"
              onClick={() => onRename(setRenaming)}
              disabled={value.length === 0}
            >
              <Check />
            </Button>
          </div>
        </>
      ) : (
        <>
          <p className={cn("min-w-fit", customNameClassName)}>{initialValue}</p>
          <Button
            variant="outline"
            size="icon"
            onClick={() => setRenaming(true)}
          >
            <Pencil />
          </Button>
        </>
      )}
    </div>
  );
}
