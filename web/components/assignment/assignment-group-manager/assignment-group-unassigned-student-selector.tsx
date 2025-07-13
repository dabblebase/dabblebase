import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { useState } from "react";
import type { components } from "@/models/schema";

type Group = components["schemas"]["GetGroupsResponse_Group"];

export default function AssignmentGroupUnassignedStudentSelector({
  groups,
  onSubmit,
  children,
}: {
  groups: Group[];
  onSubmit: (groupId: number, setOpen: (newValue: boolean) => void) => void;
  children?: React.ReactNode;
}) {
  const [open, setOpen] = useState(false);

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>{children}</PopoverTrigger>
      <PopoverContent className="w-[280px] p-0" align="start">
        <Command>
          <CommandInput placeholder="Search groups..." />
          <CommandList>
            <CommandEmpty>No groups found.</CommandEmpty>
            <CommandGroup>
              {groups.map((group) => (
                <CommandItem
                  key={group.group_id}
                  value={`${group.group_name}`}
                  onSelect={() => {
                    onSubmit(group.group_id, setOpen);
                  }}
                  className="flex items-center"
                >
                  <span className="ml-7">{group.group_name}</span>
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}
