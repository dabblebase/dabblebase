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
import { useRepublishAssignment } from "@/hooks/api/assignment/use-republish-assignment";

export default function RepublishAssignmentDialog({
  assignmentId,
  children,
}: {
  assignmentId: number;
  children: React.ReactNode;
}) {
  const [open, setOpen] = useState(false);

  const { republishAssignment, refetchOnSuccess } = useRepublishAssignment();

  const onRepublishButtonPressed = () => {
    republishAssignment(
      {
        params: {
          path: {
            assignment_id: assignmentId,
          },
        },
      },
      {
        onSuccess: () => {
          toast.success("Assignment republished successfully.");
          // Invalideate the assignment data to refresh the state
          refetchOnSuccess();
          setOpen(false);
        },
        onError: () => {
          toast.error("Failed to republish the assignment.", {
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
          <DialogTitle>Republish Assignment?</DialogTitle>
          <DialogDescription className="my-3">
            Students will regain access to the assignment and their projects.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline">Cancel</Button>
          </DialogClose>
          <Button onClick={onRepublishButtonPressed}>Republish</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
