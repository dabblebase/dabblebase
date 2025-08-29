import { Button } from "@/components/ui/button";
import JoinCourseForm from "./join-course-form";
import { Plus } from "lucide-react";
import CreateCourseForm from "../create-course/create-course-form";

export default function JoinCourseNewStudent({
  isInstructor,
}: {
  isInstructor: boolean;
}) {
  return (
    <div className="flex flex-col pt-20 justify-center items-center">
      <h1 className="text-2xl font-bold mb-4">Welcome to Dabblebase!</h1>
      {isInstructor && (
        <>
          <p>Create your first course below.</p>
          <CreateCourseForm>
            <Button>
              <Plus />
              Create Course
            </Button>
          </CreateCourseForm>
          <p>
            Or, join your first course by entering an invite code from your
            instructor below.
          </p>
        </>
      )}
      {!isInstructor && (
        <p>
          Join your first course by entering an invite code from your instructor
          below.
        </p>
      )}
      <JoinCourseForm>
        <Button variant={isInstructor ? "secondary" : "default"}>
          <Plus />
          Join Course
        </Button>
      </JoinCourseForm>
    </div>
  );
}
