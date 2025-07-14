import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog";
import { useState } from "react";
import { Button } from "../ui/button";
import { toast } from "sonner";
import { useUnpublishAssignment } from "@/hooks/api/assignment/use-unpublish-assignment";

export default function UnpublishAssignmentDialog({
  assignmentId,
  children,
}: {
  assignmentId: number;
  children: React.ReactNode;
}) {
  const [open, setOpen] = useState(false);

  const { unpublishAssignment, refetchOnSuccess } = useUnpublishAssignment();

  const onUnpublishButtonPressed = () => {
    unpublishAssignment(
      {
        params: {
          path: {
            assignment_id: assignmentId,
          },
        },
      },
      {
        onSuccess: () => {
          toast.success("Assignment unpublished successfully.");
          // Invalideate the assignment data to refresh the state
          refetchOnSuccess();
          setOpen(false);
        },
        onError: () => {
          toast.error("Failed to unpublish the assignment.", {
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
          <DialogTitle>Unpublish Assignment?</DialogTitle>
          <DialogDescription className="my-3">
            Students will regain access to the assignment and their projects.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline">Cancel</Button>
          </DialogClose>
          <Button onClick={onUnpublishButtonPressed}>Unpublish</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
