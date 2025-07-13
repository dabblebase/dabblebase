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
import { usePublishAssignmentTask } from "@/hooks/api/assignment/use-publish-assignment-task";
import { Loader2Icon } from "lucide-react";
import { useRouter } from "next/router";
import { useState } from "react";
import { toast } from "sonner";

export default function AssignmentPublishDialog({
  courseId,
  assignmentId,
  children,
}: {
  courseId: number;
  assignmentId: number;
  children?: React.ReactNode;
}) {
  const router = useRouter();

  const [open, setOpen] = useState(false);

  // const [isPublishing, setIsPublishing] = useState(false);
  // const [publishingTaskId, setPublishingTaskId] = useState<string | null>(null);

  // Mutation hook to initiate the publish request.
  const { launchPublishAssignmentTask, isPublishingAssignment } =
    usePublishAssignmentTask({
      onSuccess: () => {
        toast.success("Assignment published successfully!", {
          description: "Students will now have access to this assignment.",
        });
        // Redirect to the courses page to see the changes.
        router.push(`/course/${courseId}/assignments`);
      },
      onStartingTaskError: () => {
        toast.error(`Failed to start publishing assignment`, {
          description: "Please try again later.",
        });
      },
      onTaskError: () => {
        toast.error(`Failed to publish assignment`, {
          description: "Please try again later.",
        });
      },
    });

  const onPublishButtonPressed = () => {
    launchPublishAssignmentTask({
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
          <DialogTitle>Publish assignment?</DialogTitle>
          <DialogDescription className="my-3">
            Once the assignment is published, students will be able to see it
            and access their projects. You will not be able to change the
            project&apos;s configuration SQL.
          </DialogDescription>
          <DialogFooter>
            <DialogClose asChild>
              <Button variant="outline">Cancel</Button>
            </DialogClose>
            <Button
              type="submit"
              disabled={isPublishingAssignment}
              onClick={onPublishButtonPressed}
            >
              {isPublishingAssignment ? (
                <>
                  <Loader2Icon className="animate-spin" />
                  Publishing...
                </>
              ) : (
                <>Publish</>
              )}
            </Button>
          </DialogFooter>
        </DialogHeader>
      </DialogContent>
    </Dialog>
  );
}
