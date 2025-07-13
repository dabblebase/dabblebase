import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogClose,
  DialogContent,
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
import { useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import z from "zod";

const CreateGroupFormSchema = z.object({
  group_name: z.string().min(1, "Group name is required"),
});
type CreateGroupFormSchemaType = z.infer<typeof CreateGroupFormSchema>;

export default function CreateAssignmentGroupDialog({
  assignmentId,
  children,
  refetch,
}: {
  assignmentId: number;
  children?: React.ReactNode;
  refetch: () => void;
}) {
  const createGroupForm = useForm<CreateGroupFormSchemaType>({
    resolver: zodResolver(CreateGroupFormSchema),
    defaultValues: {
      group_name: "",
    },
  });

  // Hooks related to creating a new group
  const { mutate: createGroup } = api.useMutation(
    "post",
    "/api/assignment/{assignment_id}/group"
  );

  const [open, setOpen] = useState(false);
  const [formSubmitting, setFormSubmitting] = useState(false);

  const onSubmit = () => {
    setFormSubmitting(true);
    createGroup(
      {
        params: {
          path: { assignment_id: assignmentId },
        },
        body: {
          group_name: createGroupForm.getValues("group_name"),
        },
      },
      {
        onSuccess: () => {
          // Refetch the group data to reflect the changes
          refetch();
          createGroupForm.reset();
          setOpen(false);
        },
        onError: () => {
          toast.error(`Failed to create group`, {
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
          <DialogTitle>Create new group</DialogTitle>
        </DialogHeader>
        <Form {...createGroupForm}>
          <form
            className="grid gap-4"
            onSubmit={createGroupForm.handleSubmit(onSubmit)}
          >
            <FormField
              control={createGroupForm.control}
              name="group_name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="font-semibold">Name</FormLabel>
                  <FormControl>
                    <Input placeholder="ex) Team A" {...field} />
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
                disabled={!createGroupForm.formState.isValid || formSubmitting}
              >
                {formSubmitting ? (
                  <>
                    <Loader2Icon className="animate-spin" />
                    Creating...
                  </>
                ) : (
                  <>Create</>
                )}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
