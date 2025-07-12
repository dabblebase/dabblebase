import { useState } from "react";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "../../../../ui/popover";
import {
  Command,
  CommandEmpty,
  CommandInput,
  CommandItem,
  CommandList,
} from "../../../../ui/command";
import { useDebounce } from "use-debounce";
import { api } from "@/utils/api";
import { CommandGroup } from "cmdk";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

export default function AssignmentGroupStudentSelector({
  courseId,
  assignmentId,
  groupId,
}: {
  courseId: number;
  assignmentId: number;
  groupId: number;
}) {
  const queryClient = useQueryClient();

  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [debouncedSearch] = useDebounce(search, 300);

  const { data: studentData } = api.useQuery(
    "get",
    "/api/course/{course_id}/students",
    {
      params: {
        path: { course_id: courseId },
        query: {
          search: debouncedSearch,
        },
      },
    },
    { placeholderData: (prev) => prev }
  );

  const { mutate: addStudentToGroup } = api.useMutation(
    "post",
    "/api/assignment/{assignment_id}/group/{group_id}/member"
  );

  const onSubmit = (studentId: number) => {
    addStudentToGroup(
      {
        params: {
          path: { assignment_id: assignmentId },
        },
        body: {
          group_id: groupId,
          user_id: studentId,
        },
      },
      {
        onSuccess: () => {
          // Refetch the group data to reflect the changes
          queryClient.refetchQueries({
            queryKey: ["get", "/api/assignment/{assignment_id}/groups"],
          });
          setOpen(false);
        },
        onError: () => {
          toast.error("Failed to add student to group", {
            description: "Please try again later.",
          });
        },
      }
    );
  };

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button variant="outline" size="sm">
          <Plus />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[280px] p-0" align="start">
        <Command shouldFilter={false}>
          <CommandInput
            value={search}
            onValueChange={setSearch}
            placeholder="Search students..."
          />
          <CommandList>
            <CommandEmpty>No students found.</CommandEmpty>
            <CommandGroup>
              {!!studentData &&
                studentData.students.map((student) => (
                  <CommandItem
                    key={student.user_id}
                    value={`${student.user_name}`}
                    onSelect={() => {
                      onSubmit(student.user_id);
                    }}
                    className="flex items-center"
                  >
                    <span className="ml-7">{student.user_name}</span>
                  </CommandItem>
                ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}
