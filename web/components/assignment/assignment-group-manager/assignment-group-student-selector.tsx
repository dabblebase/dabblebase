import { useState } from "react";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  Command,
  CommandEmpty,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import { useDebounce } from "use-debounce";
import { CommandGroup } from "cmdk";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { toast } from "sonner";
import { useAddGroupMember } from "@/hooks/api/assignment/groups/use-add-group-member";
import { useStudents } from "@/hooks/api/course/use-students";

export default function AssignmentGroupStudentSelector({
  courseId,
  assignmentId,
  groupId,
  refetch,
}: {
  courseId: number;
  assignmentId: number;
  groupId: number;
  refetch: () => void;
}) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [debouncedSearch] = useDebounce(search, 300);

  const { studentData } = useStudents(courseId, assignmentId, debouncedSearch);

  const { addGroupMember, refetchOnSuccess: refetchOnSuccessAddGroupMember } =
    useAddGroupMember();

  const onSubmit = (studentId: number) => {
    addGroupMember(
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
          refetch();
          refetchOnSuccessAddGroupMember();
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
