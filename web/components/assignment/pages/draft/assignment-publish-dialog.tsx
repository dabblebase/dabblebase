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
import { api } from "@/utils/api";
import { Loader2Icon } from "lucide-react";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";
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

  const [isPublishing, setIsPublishing] = useState(false);
  const [publishingTaskId, setPublishingTaskId] = useState<string | null>(null);

  // Mutation hook to initiate the publish request.
  // After the mutation succeeds, it will return a task ID that we can use to poll for
  //the status of the publishing task.
  const { mutate: publishAssignment } = api.useMutation(
    "put",
    "/api/assignment/{assignment_id}/publish"
  );

  // Polling for the status of the publishing task.
  const { data: publishingStatus } = api.useQuery(
    "get",
    "/api/task/{task_id}/status",
    {
      params: {
        path: {
          task_id: publishingTaskId!,
        },
      },
    },
    {
      enabled: !!publishingTaskId, // Only run this query if we have a task ID to poll.
      refetchInterval: 1000,
    }
  );

  // Respond to changes in the publishing status
  useEffect(() => {
    if (publishingStatus && publishingStatus.status === "SUCCESS") {
      setIsPublishing(false);
      setPublishingTaskId(null);
      setOpen(false);
      toast.success("Assignment published successfully!", {
        description: "Students will now have access to this assignment.",
      });
      // Refetch the queries that might be affected by the publishing action.
      // Redirect to the courses page to see the changes.
      router.push(`/course/${courseId}/assignments`);
    }
    if (
      publishingStatus &&
      (publishingStatus.status === "FAILURE" ||
        publishingStatus.status === "REVOKED" ||
        publishingStatus.status === "IGNORED")
    ) {
      setIsPublishing(false);
      setPublishingTaskId(null);
      toast.error(`Failed to publish assignment`, {
        description: "Please try again later.",
      });
    }
  }, [courseId, publishingStatus, router]);

  const onPublishButtonPressed = () => {
    setIsPublishing(true);
    publishAssignment(
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
          setPublishingTaskId(response.task_id);
        },
        onError: () => {
          setIsPublishing(false);
          setPublishingTaskId(null);
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
              disabled={isPublishing}
              onClick={onPublishButtonPressed}
            >
              {isPublishing ? (
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
