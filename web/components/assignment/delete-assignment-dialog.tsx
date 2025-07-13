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
import { api } from "@/utils/api";
import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2Icon } from "lucide-react";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";
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
  const [isDeleting, setIsDeleting] = useState(false);
  const [deletingTaskId, setDeletingTaskId] = useState<string | null>(null);

  // Mutation hook to initiate the publish request.
  // After the mutation succeeds, it will return a task ID that we can use to poll for
  //the status of the publishing task.
  const { mutate: deleteAssignment } = api.useMutation(
    "delete",
    "/api/assignment/{assignment_id}"
  );

  // Polling for the status of the deleting task.
  const { data: deletingStatus } = api.useQuery(
    "get",
    "/api/task/{task_id}/status",
    {
      params: {
        path: {
          task_id: deletingTaskId!,
        },
      },
    },
    {
      enabled: !!deletingTaskId, // Only run this query if we have a task ID to poll.
      refetchInterval: 1000,
    }
  );

  // Respond to changes in the publishing status
  useEffect(() => {
    if (deletingStatus && deletingStatus.status === "SUCCESS") {
      setIsDeleting(false);
      setDeletingTaskId(null);
      setOpen(false);
      toast.success("Assignment deleted.");
      // Redirect to the courses page to see the changes.
      router.push(`/course/${courseId}/assignments`);
    }
    if (
      deletingStatus &&
      (deletingStatus.status === "FAILURE" ||
        deletingStatus.status === "REVOKED" ||
        deletingStatus.status === "IGNORED")
    ) {
      setIsDeleting(false);
      setDeletingTaskId(null);
      toast.error(`Failed to delete assignment`, {
        description: "Please try again later.",
      });
    }
  }, [courseId, deletingStatus, router]);

  const onDeleteButtonPressed = () => {
    setIsDeleting(true);
    deleteAssignment(
      {
        params: {
          path: {
            assignment_id: assignmentId,
          },
        },
      },
      {
        onSuccess: (response) => {
          // Set the publishing ID, which kicks off the polling for the task to finish.
          setDeletingTaskId(response.task_id);
        },
        onError: () => {
          setIsDeleting(false);
          setDeletingTaskId(null);
          toast.error(`Failed to start publishing assignment`, {
            description: "Please try again later.",
          });
        },
      }
    );
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
                disabled={!deleteAssignmentForm.formState.isValid || isDeleting}
              >
                {isDeleting ? (
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
