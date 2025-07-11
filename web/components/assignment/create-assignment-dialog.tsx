import z from "zod";
import { Button } from "../ui/button";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog";
import { Input } from "../ui/input";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "../ui/form";
import { RadioGroup, RadioGroupItem } from "../ui/radio-group";
import { Card, CardContent } from "../ui/card";
import { Separator } from "../ui/separator";
import { api } from "@/utils/api";
import { Loader2Icon } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

const CreateAssignmentFormSchema = z.object({
  name: z.string().min(1, "Name is required"),
  type: z.enum(["individual", "group"], {
    required_error: "Assignment type is required",
  }),
});
type CreateAssignmentFormSchemaType = z.infer<
  typeof CreateAssignmentFormSchema
>;

export default function CreateAssignmentDialog({
  courseId,
  children,
}: {
  courseId: number;
  children: React.ReactNode;
}) {
  const createAssignmentForm = useForm<CreateAssignmentFormSchemaType>({
    resolver: zodResolver(CreateAssignmentFormSchema),
    defaultValues: {
      name: "",
      type: "individual",
    },
  });

  const { mutate: createAssignmentDraft } = api.useMutation(
    "post",
    "/api/assignment/draft"
  );

  const [formSubmitting, setFormSubmitting] = useState(false);

  const onSubmit = () => {
    setFormSubmitting(true);
    createAssignmentDraft(
      {
        body: {
          name: createAssignmentForm.getValues("name"),
          course_id: courseId,
          is_group: createAssignmentForm.getValues("type") === "group",
        },
      },
      {
        onSuccess: (data) => {
          // Do something with the returned assignment id
          console.log(data.assignment_id);
        },
        onError: () => {
          toast.error("Error creating new assignment", {
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
    <Dialog>
      <DialogTrigger asChild>{children}</DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>New Assignment</DialogTitle>
        </DialogHeader>
        <Form {...createAssignmentForm}>
          <form
            className="grid gap-4"
            onSubmit={createAssignmentForm.handleSubmit(onSubmit)}
          >
            <FormField
              control={createAssignmentForm.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="font-semibold">Name</FormLabel>
                  <FormControl>
                    <Input placeholder="ex) a04: Wordle" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={createAssignmentForm.control}
              name="type"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="font-semibold">
                    Assignment Type
                  </FormLabel>
                  <Card className="border-input">
                    <CardContent className="px-3">
                      <FormControl>
                        <RadioGroup
                          onValueChange={field.onChange}
                          defaultValue={field.value}
                          className="flex flex-col"
                        >
                          <FormItem className="flex items-center gap-3">
                            <FormControl>
                              <RadioGroupItem value="individual" />
                            </FormControl>
                            <FormLabel className="font-normal">
                              <div className="flex flex-col gap-1">
                                <p className="font-medium">
                                  Individual Assignment
                                </p>
                                <p className="text-accent-foreground/80">
                                  Projects will be created for every student in
                                  the class.
                                </p>
                              </div>
                            </FormLabel>
                          </FormItem>
                          <Separator className="my-2 bg-input" />
                          <FormItem className="flex items-center gap-3">
                            <FormControl>
                              <RadioGroupItem value="group" />
                            </FormControl>
                            <FormLabel className="font-normal">
                              <div className="flex flex-col gap-1">
                                <p className="font-medium">Group Assignment</p>
                                <p className="text-accent-foreground/80">
                                  Students share the same project database with
                                  their teammates.
                                </p>
                              </div>
                            </FormLabel>
                          </FormItem>
                        </RadioGroup>
                      </FormControl>
                    </CardContent>
                  </Card>
                  <FormDescription>
                    Once selected, an assignment&apos;s type cannot be changed.
                  </FormDescription>
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
                disabled={
                  !createAssignmentForm.formState.isValid || formSubmitting
                }
              >
                {formSubmitting ? (
                  <>
                    <Loader2Icon className="animate-spin" />
                    Creating...
                  </>
                ) : (
                  <>Continue</>
                )}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
