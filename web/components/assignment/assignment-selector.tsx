import { useState } from "react";
import { Popover, PopoverContent } from "../ui/popover";
import { PopoverTrigger } from "@radix-ui/react-popover";
import { Button } from "../ui/button";
import { CheckIcon, ChevronsUpDownIcon } from "lucide-react";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "../ui/command";
import { cn } from "@/utils/cn";
import { useDebounce } from "use-debounce";
import { Badge } from "../ui/badge";
import { useRouter } from "next/router";
import { useAssignmentDropdown } from "@/hooks/api/assignment/use-assignment-dropdown";

export default function AssignmentSelector({
  courseId,
  initialAssignmentId,
}: {
  courseId: number;
  initialAssignmentId?: number;
}) {
  const router = useRouter();

  const [open, setOpen] = useState(false);
  const [selectedAssignmentId, setAssignmentCourseId] = useState<
    string | undefined
  >(`${initialAssignmentId}`);
  const [search, setSearch] = useState("");
  const [debouncedSearch] = useDebounce(search, 300);

  const { dropdownData, selectedAssignment } = useAssignmentDropdown(
    courseId,
    debouncedSearch,
    initialAssignmentId,
    selectedAssignmentId
  );

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="ghost"
          role="combobox"
          aria-expanded={open}
          className="justify-between"
        >
          {!!dropdownData && !!selectedAssignment ? (
            <div className="flex flex-row items-center">
              {selectedAssignment.name}
              {dropdownData.is_staff &&
                selectedAssignment.state === "draft" && (
                  <Badge className="ml-2" variant="outline">
                    Draft
                  </Badge>
                )}
              {dropdownData.is_staff &&
                selectedAssignment.state === "published" && (
                  <Badge className="ml-2" variant="default">
                    Published
                  </Badge>
                )}
              {dropdownData.is_staff &&
                selectedAssignment.state === "unpublished" && (
                  <Badge className="ml-2 bg-accent" variant="secondary">
                    Unpublished
                  </Badge>
                )}
            </div>
          ) : (
            "Select assignment..."
          )}
          <ChevronsUpDownIcon className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[320px] p-0" align="start">
        <Command shouldFilter={false}>
          <CommandInput
            value={search}
            onValueChange={setSearch}
            placeholder="Search assignments..."
          />
          <CommandList>
            <CommandEmpty>No course found.</CommandEmpty>
            <CommandGroup>
              {!!dropdownData &&
                dropdownData.assignments.map((assignment) => (
                  <CommandItem
                    key={assignment.id}
                    value={`${assignment.id}`}
                    onSelect={(currentValue) => {
                      setAssignmentCourseId(currentValue);
                      setOpen(false);
                      router.push(
                        `/course/${courseId}/assignment/${currentValue}`
                      );
                    }}
                    className="flex items-center"
                  >
                    <CheckIcon
                      className={cn(
                        "mr-2 h-4 w-4",
                        selectedAssignmentId === `${assignment.id}`
                          ? "opacity-100"
                          : "opacity-0"
                      )}
                    />
                    {assignment.name}
                    {dropdownData.is_staff && assignment.state === "draft" && (
                      <Badge className="ml-auto" variant="outline">
                        Draft
                      </Badge>
                    )}
                    {dropdownData.is_staff &&
                      assignment.state === "published" && (
                        <Badge className="ml-auto" variant="default">
                          Published
                        </Badge>
                      )}
                    {dropdownData.is_staff &&
                      assignment.state === "unpublished" && (
                        <Badge
                          className="ml-auto bg-accent"
                          variant="secondary"
                        >
                          Unpublished
                        </Badge>
                      )}
                  </CommandItem>
                ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}
