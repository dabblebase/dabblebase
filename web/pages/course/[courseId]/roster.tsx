import CourseLayout from "@/components/course/course-layout";
import { rosterColumnsGenerator } from "@/components/course/roster/roster-table/columns";
import { DataTable } from "@/components/ui/data-table";
import { useChangeMemberRole } from "@/hooks/api/course/use-change-member-role";
import { useCourseRole } from "@/hooks/api/course/use-course-role";
import { useCourseRoster } from "@/hooks/api/course/use-course-roster";
import { protectRoute } from "@/utils/auth";
import { GetServerSidePropsContext } from "next";
import { useRouter } from "next/router";
import type { components } from "@/models/schema";
import { toast } from "sonner";
import { useRemoveMember } from "@/hooks/api/course/use-remove-member";
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
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import CopyText from "@/components/ui/copy-text";

type Role = components["schemas"]["CourseMembershipRole"];

export default function CourseRosterPage() {
  const router = useRouter();
  const { courseId } = router.query;

  const { courseRoleData } = useCourseRole(courseId as unknown as number);
  const { rosterData } = useCourseRoster(courseId as unknown as number);

  const {
    changeMemberRole,
    refetchOnSuccess: refetchOnChangeMemberRoleSuccess,
  } = useChangeMemberRole();

  const onChangeRoleAction = (userId: number, role: Role) => {
    changeMemberRole(
      {
        params: {
          path: {
            course_id: courseId as unknown as number,
            user_id: userId,
          },
          query: {
            role: role,
          },
        },
      },
      {
        onSuccess: () => {
          refetchOnChangeMemberRoleSuccess();
          toast.success("Successfully changed member role.");
        },
        onError: () => {
          toast.error("Failed to change member role.", {
            description: "Please try again later.",
          });
        },
      }
    );
  };

  const { removeMember, refetchOnSuccess: refetchOnRemoveMemberSuccess } =
    useRemoveMember();

  const onRemoveMemberAction = (userId: number) => {
    removeMember(
      {
        params: {
          path: {
            course_id: courseId as unknown as number,
            user_id: userId,
          },
        },
      },
      {
        onSuccess: () => {
          refetchOnRemoveMemberSuccess();
          toast.success("Successfully removed member from course.");
        },
        onError: () => {
          toast.error("Failed to remove member from course.", {
            description: "Please try again later.",
          });
        },
      }
    );
  };
  return (
    <div className="flex flex-col mx-auto w-full max-w-[1200px] px-4 gap-8 my-8">
      <div className="flex flex-row w-full items-center justify-between">
        <h1 className="text-2xl font-semibold">Roster</h1>
        {!!rosterData && (
          <Dialog>
            <DialogTrigger asChild>
              <Button>
                <Plus />
                Invite Members
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
              <DialogHeader>
                <DialogTitle>Invite Members</DialogTitle>
                <DialogDescription className="my-3 text-accent-foreground/80">
                  Share this code with anyone you want to invite to your course.
                  They can use it to join your course.
                </DialogDescription>
                <CopyText
                  text={rosterData.invite_code}
                  buttonVariant="default"
                />
              </DialogHeader>
              <DialogFooter className="mt-3">
                <DialogClose asChild>
                  <Button variant="outline">Close</Button>
                </DialogClose>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        )}
      </div>

      {!!courseRoleData && !!courseRoleData.role && !!rosterData && (
        <DataTable
          columns={rosterColumnsGenerator(
            courseRoleData.role!,
            onChangeRoleAction,
            onRemoveMemberAction
          )}
          data={rosterData.members}
        />
      )}
    </div>
  );
}

export async function getServerSideProps(context: GetServerSidePropsContext) {
  return protectRoute(context, "/login");
}

CourseRosterPage.getLayout = function getLayout(page: React.ReactNode) {
  return <CourseLayout>{page}</CourseLayout>;
};
