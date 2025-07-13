import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { useDeleteAssignmentTask } from "@/hooks/api/assignment/use-delete-assignment-task";
import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2Icon } from "lucide-react";
import { useRouter } from "next/router";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import z from "zod";

export default function DeleteAssignmentDialog({
  courseId,
  assignmentId,
  assignmentName,
  children,
}: {
  courseId: number;
  assignmentId: number;
  assignmentName: string;
  children: React.ReactNode;
}) {
  const router = useRouter();

  // Schema for the delete confirmation form
  const deleteAssignmentFormSchema = z.object({
    confirmation: z.string().refine((val) => val === assignmentName, {
      message: "The typed name does not match.",
    }),
  });
  type DeleteAssignmentFormSchemaType = z.infer<
    typeof deleteAssignmentFormSchema
  >;

  const deleteAssignmentForm = useForm<DeleteAssignmentFormSchemaType>({
    resolver: zodResolver(deleteAssignmentFormSchema),
    defaultValues: {
      confirmation: "",
    },
  });

  const [open, setOpen] = useState(false);

  const { launchDeleteAssignmentTask, isDeletingAssignment } =
    useDeleteAssignmentTask({
      onSuccess: () => {
        setOpen(false);
        toast.success("Assignment deleted.");
        // Redirect to the courses page to see the changes.
        router.push(`/course/${courseId}/assignments`);
      },
      onStartingTaskError: () => {
        toast.error(`Failed to start publishing assignment`, {
          description: "Please try again later.",
        });
      },
      onTaskError: () => {
        toast.error(`Failed to delete assignment`, {
          description: "Please try again later.",
        });
      },
    });

  const onDeleteButtonPressed = () => {
    launchDeleteAssignmentTask({
      params: {
        path: {
          assignment_id: assignmentId,
        },
      },
    });
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{children}</DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Delete Assignment?</DialogTitle>
          <DialogDescription className="my-3">
            Once the assignment is deleted, students will lose access, all
            project databases will be deleted, and no data will be recoverable.
            <br />
            <br />
            To delete the assignment, please confirm by typing the name of the
            assignment below.
          </DialogDescription>
        </DialogHeader>
        <Form {...deleteAssignmentForm}>
          <form
            className="grid gap-4"
            onSubmit={deleteAssignmentForm.handleSubmit(onDeleteButtonPressed)}
          >
            <FormField
              control={deleteAssignmentForm.control}
              name="confirmation"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="font-semibold">
                    Type &quot;{assignmentName}&quot; below:
                  </FormLabel>
                  <FormControl>
                    <Input
                      placeholder={`Repeat: ${assignmentName}`}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <DialogFooter>
              <DialogClose asChild>
                <Button variant="outline">Cancel</Button>
              </DialogClose>
              <Button
                type="submit"
                variant="destructive"
                disabled={
                  !deleteAssignmentForm.formState.isValid ||
                  isDeletingAssignment
                }
              >
                {isDeletingAssignment ? (
                  <>
                    <Loader2Icon className="animate-spin" />
                    Deleting...
                  </>
                ) : (
                  <>Delete</>
                )}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
