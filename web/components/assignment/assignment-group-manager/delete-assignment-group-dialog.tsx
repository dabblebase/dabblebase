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
import { useState } from "react";
import { toast } from "sonner";

export default function DeleteAssignmentGroupDialog({
  assignmentId,
  groupId,
  children,
  refetch,
}: {
  assignmentId: number;
  groupId: number;
  children?: React.ReactNode;
  refetch: () => void;
}) {
  const [open, setOpen] = useState(false);
  const [formSubmitting, setFormSubmitting] = useState(false);

  const { mutate: deleteGroup } = api.useMutation(
    "delete",
    "/api/assignment/{assignment_id}/group/{group_id}"
  );

  const onSubmit = () => {
    setFormSubmitting(true);
    deleteGroup(
      {
        params: {
          path: {
            assignment_id: assignmentId,
            group_id: groupId,
          },
        },
      },
      {
        onSuccess: () => {
          // Refetch the group data to reflect the changes
          refetch();
          setOpen(false);
        },
        onError: () => {
          toast.error("Failed to delete group", {
            description: "Please try again later.",
          });
        },
        onSettled: () => {
          setFormSubmitting(false);
        },
      }
    );
  };
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{children}</DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Delete Group</DialogTitle>
          <DialogDescription>
            Are you sure you want to delete this group? All users in this group
            will be unassigned from it.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline">Cancel</Button>
          </DialogClose>
          <Button
            variant="destructive"
            onClick={onSubmit}
            disabled={formSubmitting}
          >
            {formSubmitting ? (
              <>
                <Loader2Icon className="animate-spin" />
                Deleting...
              </>
            ) : (
              <>Delete</>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
