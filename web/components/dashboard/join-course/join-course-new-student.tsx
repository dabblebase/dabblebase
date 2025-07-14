import { Button } from "@/components/ui/button";
import JoinCourseForm from "./join-course-form";
import { Plus } from "lucide-react";

export default function JoinCourseNewStudent() {
  return (
    <div className="flex flex-col pt-20 justify-center items-center">
      <h1 className="text-2xl font-bold mb-4">Welcome to Dabblebase!</h1>
      <p>
        Join your first course by entering an invite code from your instructor
        below.
      </p>
      <JoinCourseForm>
        <Button>
          <Plus />
          Join Course
        </Button>
      </JoinCourseForm>
    </div>
  );
}
