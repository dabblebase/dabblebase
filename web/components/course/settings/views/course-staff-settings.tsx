import ErrorMessage from "@/components/errors/error-message";
import RenameComponent from "@/components/ui/rename";
import { useCourseStaffSettingsView } from "@/hooks/api/course/use-course-staff-settings-view";
import { useUpdateCourse } from "@/hooks/api/course/use-update-course";
import { useEffect, useState } from "react";
import { toast } from "sonner";

export default function CourseStaffSettings({
  courseId,
}: {
  courseId: number;
}) {
  const { settingsView, settingsViewError } =
    useCourseStaffSettingsView(courseId);

  const { updateCourse, refetchOnSuccess: refetchOnUpdateCourseSuccess } =
    useUpdateCourse();

  const [editCodeText, setEditCodeText] = useState("");
  const [editNameText, setEditNameText] = useState("");

  const editHandlerOptions = (setRenaming: (renaming: boolean) => void) => {
    return {
      onSuccess: () => {
        setRenaming(false);
        refetchOnUpdateCourseSuccess();
      },
      onError: () => {
        toast.error("Failed to update course code.", {
          description: "Please try again later.",
        });
      },
    };
  };
  const editCodeHandler = (setRenaming: (renaming: boolean) => void) => {
    if (!settingsView) return;
    updateCourse(
      {
        params: { path: { course_id: courseId } },
        body: { ...settingsView, code: editCodeText },
      },
      editHandlerOptions(setRenaming)
    );
  };

  const editNameHandler = (setRenaming: (renaming: boolean) => void) => {
    if (!settingsView) return;
    updateCourse(
      {
        params: { path: { course_id: courseId } },
        body: { ...settingsView, name: editNameText },
      },
      editHandlerOptions(setRenaming)
    );
  };

  useEffect(() => {
    if (settingsView) {
      setEditCodeText(settingsView.code);
      setEditNameText(settingsView.name);
    }
  }, [settingsView]);

  return (
    <div className="flex flex-col mx-auto w-full max-w-[800px] px-4 gap-8 my-8">
      <h1 className="text-2xl font-semibold">Course Settings</h1>
      {!!settingsViewError && <ErrorMessage resource="settings page" />}
      {!!settingsView && (
        <>
          <div className="flex flex-col gap-2">
            <p className="text-lg font-bold">Course code</p>
            <RenameComponent
              initialValue={settingsView.code}
              value={editCodeText}
              setValue={setEditCodeText}
              placeholder="ex) COMP426-001"
              onRename={editCodeHandler}
            />
          </div>
          <div className="flex flex-col gap-2">
            <p className="text-lg font-bold">Course name</p>
            <RenameComponent
              initialValue={settingsView.name}
              value={editNameText}
              setValue={setEditNameText}
              placeholder="ex) Modern Web Programming"
              onRename={editNameHandler}
            />
          </div>
        </>
      )}
    </div>
  );
}
