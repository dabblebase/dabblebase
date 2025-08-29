import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useCreateCourse } from "@/hooks/api/course/use-create-course";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/router";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import z from "zod";

// Schema for the join course form
const createCourseFormSchema = z.object({
  code: z.string(),
  name: z.string(),
  description: z.string(),
  term_type: z.enum(["Fall", "Spring", "Summer", "Winter"]),
  term_year: z.number().gte(1000).lte(9999),
});
type CreateCourseFormSchemaType = z.infer<typeof createCourseFormSchema>;

export default function CreateCourseForm({
  onSubmit,
  children,
}: {
  onSubmit?: () => void;
  children?: React.ReactNode;
}) {
  const router = useRouter();

  const createCourseForm = useForm<CreateCourseFormSchemaType>({
    resolver: zodResolver(createCourseFormSchema),
    defaultValues: {
      code: "",
      name: "",
      description: "",
      term_type: "Fall",
      term_year: 2025,
    },
  });

  const { createCourse } = useCreateCourse();

  const onFormSubmit = () => {
    createCourse(
      {
        body: {
          code: createCourseForm.getValues("code"),
          name: createCourseForm.getValues("name"),
          description: createCourseForm.getValues("description"),
          term_type: createCourseForm.getValues("term_type"),
          term_year: createCourseForm.getValues("term_year"),
        },
      },
      {
        onSuccess: (response) => {
          onSubmit?.();
          createCourseForm.reset();
          toast.success(`Successfully created ${response.code}!`);
          router.push("/course/" + response.id);
        },
        onError: () => {
          toast.error("Failed to create course.", {
            description: "Please try again.",
          });
        },
      }
    );
  };

  return (
    <Form {...createCourseForm}>
      <form
        className="grid gap-4"
        onSubmit={createCourseForm.handleSubmit(onFormSubmit)}
      >
        <FormField
          control={createCourseForm.control}
          name="code"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="font-semibold">
                Enter the course code:
              </FormLabel>
              <FormControl>
                <Input placeholder={`ex: COMP426`} {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={createCourseForm.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="font-semibold">
                Enter the course&apos;s name:
              </FormLabel>
              <FormControl>
                <Input placeholder={`ex: Modern Web Programming`} {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={createCourseForm.control}
          name="description"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="font-semibold">
                Enter the course description:
              </FormLabel>
              <FormControl>
                <Input placeholder={`ex: Sample description`} {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={createCourseForm.control}
          name="term_type"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="font-semibold">
                Select the term this course is offered in:
              </FormLabel>
              <FormControl>
                <Select
                  onValueChange={field.onChange}
                  defaultValue={field.value}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a term" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Fall">Fall</SelectItem>
                    <SelectItem value="Spring">Spring</SelectItem>
                    <SelectItem value="Summer">Summer</SelectItem>
                    <SelectItem value="Winter">Winter</SelectItem>
                  </SelectContent>
                </Select>
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={createCourseForm.control}
          name="term_year"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="font-semibold">
                Enter the year this course is offered:
              </FormLabel>
              <FormControl>
                <Input
                  type="number"
                  placeholder="ex: 2025"
                  {...field}
                  onChange={(e) => field.onChange(Number(e.target.value))}
                />
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
