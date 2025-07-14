import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { useJoinCourse } from "@/hooks/api/course/use-join-course";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/router";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import z from "zod";

// Schema for the join course form
const joinCourseFormSchema = z.object({
  inviteCode: z.string().length(6, "Invite code must be 6 characters long"),
});
type JoinCourseFormSchemaType = z.infer<typeof joinCourseFormSchema>;

export default function JoinCourseForm({
  onSubmit,
  children,
}: {
  onSubmit?: () => void;
  children?: React.ReactNode;
}) {
  const router = useRouter();

  const joinCourseForm = useForm<JoinCourseFormSchemaType>({
    resolver: zodResolver(joinCourseFormSchema),
    defaultValues: {
      inviteCode: "",
    },
  });

  const { joinCourse } = useJoinCourse();

  const onFormSubmit = () => {
    joinCourse(
      {
        params: {
          query: {
            invite_code: joinCourseForm.getValues("inviteCode"),
          },
        },
      },
      {
        onSuccess: (response) => {
          onSubmit?.();
          joinCourseForm.reset();
          toast.success(`Successfully joined ${response.course_code}!`);
          router.push("/course/" + response.course_id);
        },
        onError: () => {
          toast.error("Failed to join course.", {
            description: "Please check the invite code and try again.",
          });
        },
      }
    );
  };

  return (
    <Form {...joinCourseForm}>
      <form
        className="grid gap-4"
        onSubmit={joinCourseForm.handleSubmit(onFormSubmit)}
      >
        <FormField
          control={joinCourseForm.control}
          name="inviteCode"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="font-semibold">
                Enter 6-digit invite code:
              </FormLabel>
              <FormControl>
                <Input placeholder={`ex: ABC123`} {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        {children}
      </form>
    </Form>
  );
}
