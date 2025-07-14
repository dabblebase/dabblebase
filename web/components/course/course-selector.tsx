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
import { useCourseDropdown } from "@/hooks/api/course/use-course-dropdown";

export default function CourseSelector({
  initialCourseId,
  disableSelect = false,
}: {
  initialCourseId?: number;
  disableSelect?: boolean;
}) {
  const router = useRouter();

  const [open, setOpen] = useState(false);
  const [selectedCourseId, setSelectedCourseId] = useState<string | undefined>(
    `${initialCourseId}`
  );
  const [search, setSearch] = useState("");
  const [debouncedSearch] = useDebounce(search, 300);

  const { dropdownData, selectedCourse } = useCourseDropdown(
    debouncedSearch,
    initialCourseId,
    selectedCourseId
  );

  if (disableSelect) {
    return (
      <>
        {!!selectedCourse && (
          <Button
            variant="ghost"
            className="justify-between"
            onClick={() =>
              router.push(`/course/${selectedCourse.id}/assignments`)
            }
          >
            <div className="flex flex-row items-center">
              {selectedCourse.code}
              {selectedCourse.is_staff && <Badge className="ml-2">Staff</Badge>}
            </div>
          </Button>
        )}
      </>
    );
  }

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="ghost"
          role="combobox"
          aria-expanded={open}
          className="justify-between"
        >
          {!!selectedCourse ? (
            <div className="flex flex-row items-center">
              {selectedCourse.code}
              {selectedCourse.is_staff && <Badge className="ml-2">Staff</Badge>}
            </div>
          ) : (
            "Select course..."
          )}
          <ChevronsUpDownIcon className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[260px] p-0" align="start">
        <Command shouldFilter={false}>
          <CommandInput
            value={search}
            onValueChange={setSearch}
            placeholder="Search courses..."
          />
          <CommandList>
            <CommandEmpty>No course found.</CommandEmpty>
            {!!dropdownData &&
              dropdownData.terms.map((term) => (
                <CommandGroup key={term} heading={term}>
                  {dropdownData.courses[term].map((course) => (
                    <CommandItem
                      key={course.id}
                      value={`${course.id}`}
                      onSelect={(currentValue) => {
                        setSelectedCourseId(currentValue);
                        setOpen(false);
                        router.push(`/course/${currentValue}/assignments`);
                      }}
                      className="flex items-center"
                    >
                      <CheckIcon
                        className={cn(
                          "mr-2 h-4 w-4",
                          selectedCourseId === `${course.id}`
                            ? "opacity-100"
                            : "opacity-0"
                        )}
                      />
                      {course.code}
                      {course.is_staff && (
                        <Badge className="ml-auto">Staff</Badge>
                      )}
                    </CommandItem>
                  ))}
                </CommandGroup>
              ))}
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}
