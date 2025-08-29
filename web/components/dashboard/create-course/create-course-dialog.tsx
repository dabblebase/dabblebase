import { Button } from "../../ui/button";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../../ui/dialog";
import { useState } from "react";
import CreateCourseForm from "./create-course-form";

export default function CreateCourseDialog({
  children,
}: {
  children: React.ReactNode;
}) {
  const [open, setOpen] = useState(false);

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{children}</DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Create Course</DialogTitle>
          <DialogDescription className="my-3 text-accent-foreground/80">
            Please enter in the details for the new course below.
          </DialogDescription>
        </DialogHeader>
        <CreateCourseForm
          onSubmit={() => {
            setOpen(false);
          }}
        >
          <DialogFooter className="mt-3">
            <DialogClose asChild>
              <Button variant="outline">Close</Button>
            </DialogClose>
            <Button type="submit" variant="default">
              Create Course
            </Button>
          </DialogFooter>
        </CreateCourseForm>
      </DialogContent>
    </Dialog>
  );
}
