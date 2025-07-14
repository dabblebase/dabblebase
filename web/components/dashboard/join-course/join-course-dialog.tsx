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
import JoinCourseForm from "./join-course-form";

export default function JoinCourseDialog({
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
          <DialogTitle>Join Course</DialogTitle>
          <DialogDescription className="my-3 text-accent-foreground/80">
            To join a course, you need to enter the 6-digit invite code provided
            by your instructor.
          </DialogDescription>
        </DialogHeader>
        <JoinCourseForm
          onSubmit={() => {
            setOpen(false);
          }}
        >
          <DialogFooter className="mt-3">
            <DialogClose asChild>
              <Button variant="outline">Close</Button>
            </DialogClose>
            <Button type="submit" variant="default">
              Join Course
            </Button>
          </DialogFooter>
        </JoinCourseForm>
      </DialogContent>
    </Dialog>
  );
}
