import ErrorMessage from "@/components/errors/error-message";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { DataTable } from "@/components/ui/data-table";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTrigger,
} from "@/components/ui/dialog";
import RenameComponent from "@/components/ui/rename";
import { Textarea } from "@/components/ui/textarea";
import { DialogTitle } from "@radix-ui/react-dialog";
import { useQueryClient } from "@tanstack/react-query";
import {
  CircleCheck,
  CircleSlash,
  Eye,
  EyeOff,
  FileDown,
  Loader2Icon,
  Pencil,
  Trash,
} from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import {
  groupProjectsColumns,
  individualProjectsColumns,
} from "./projects-table/columns";
import { Separator } from "@/components/ui/separator";
import DeleteAssignmentDialog from "../../delete-assignment-dialog";
import UnpublishAssignmentDialog from "../../unpublish-assignment-dialog";
import RepublishAssignmentDialog from "../../republish-assignment-dialog";
import AssignmentGroupManager from "../../assignment-group-manager/assignment-group-manager";
import { useAssignmentStaffView } from "@/hooks/api/assignment/use-assignment-staff-view";
import { useRenameAssignment } from "@/hooks/api/assignment/use-rename-assignment";
import { useDatabaseExportTask } from "@/hooks/api/assignment/use-database-export-task";

export default function AssignmentStaffPage({
  courseId,
  assignmentId,
}: {
  courseId: number;
  assignmentId: number;
}) {
  const queryClient = useQueryClient();

  const {
    staffViewData,
    staffViewLoading,
    staffViewError,
    refetchStaffViewData,
    individualProjectData,
    individualProjectError,
    groupProjectData,
    groupProjectError,
  } = useAssignmentStaffView(assignmentId);

  // Hooks and mutations for renaming the assignment
  const [renameText, setRenameText] = useState("");

  useEffect(() => {
    if (staffViewData) {
      setRenameText(staffViewData.name);
    }
  }, [staffViewData]);

  const {
    renameAssignment,
    refetchOnSuccess: refetchOnRenameAssignmentSuccess,
  } = useRenameAssignment();

  const renameAssignmentHandler = (
    setRenaming: (renaming: boolean) => void
  ) => {
    renameAssignment(
      {
        params: {
          query: {
            name: renameText,
          },
          path: {
            assignment_id: assignmentId,
          },
        },
      },
      {
        onSuccess: () => {
          setRenaming(false);
          refetchOnRenameAssignmentSuccess();
          // TODO: Remove dependency on refetch queries
          refetchStaffViewData();
          // Refetch the dropdown data so that the new name is reflected in the header
          queryClient.refetchQueries({
            queryKey: ["get", "/api/assignment/dropdown"],
          });
        },
        onError: () => {
          toast.error("Error renaming assignment", {
            description: "Please make sure that the name is not empty.",
          });
        },
      }
    );
  };

  // Hooks and mutations for exporting student data
  const { launchDatabaseExportTask, isExportingDatabase } =
    useDatabaseExportTask(assignmentId, {
      onStartingTaskError: () => {
        toast.error("Failed to start exporting assignment", {
          description: "Please try again later.",
        });
      },
      onTaskError: () => {
        toast.error("Failed to export assignment data", {
          description: "Please try again later.",
        });
      },
    });

  const onExportButtonPressed = () => {
    launchDatabaseExportTask({
      params: {
        path: {
          assignment_id: assignmentId,
        },
      },
    });
  };

  return (
    <div className="flex flex-col mx-auto w-full max-w-[800px] px-4 gap-8 my-8">
      {staffViewLoading && <p>Loading...</p>}
      {staffViewError && <ErrorMessage resource="assignment" />}
      {!!staffViewData && (
        <>
          <div className="flex flex-row items-center justify-between">
            <RenameComponent
              initialValue={staffViewData.name}
              value={renameText}
              setValue={setRenameText}
              placeholder="ex) a04: Wordle"
              onRename={renameAssignmentHandler}
              customNameClassName="text-2xl font-semibold"
            />
            {staffViewData.state === "published" && (
              <Badge variant="default">Published</Badge>
            )}
            {staffViewData.state === "unpublished" && (
              <Badge className="bg-accent" variant="secondary">
                Unpublished
              </Badge>
            )}
          </div>
          <div className="flex flex-col gap-3">
            <p className="text-lg font-bold">Configuration</p>
            <Card>
              <CardContent className="px-4">
                <div className="flex flex-row gap-5 items-center">
                  {!!staffViewData.configuration_sql ? (
                    <CircleCheck className="size-6 flex-shrink-0 text-accent-foreground/60" />
                  ) : (
                    <CircleSlash className="size-6 flex-shrink-0 text-accent-foreground/60" />
                  )}
                  <div className="flex flex-col flex-grow gap-1">
                    <p className="font-semibold">
                      Run SQL on database creation
                    </p>
                    {!!staffViewData.configuration_sql ? (
                      <p className="text-accent-foreground/80">
                        SQL script provided.
                      </p>
                    ) : (
                      <p className="text-accent-foreground/80">
                        Not configured for this assignment.
                      </p>
                    )}
                  </div>
                  {!!staffViewData.configuration_sql && (
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button variant="outline" className="flex-shrink-0">
                          View
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle>
                            Run SQL on database creation
                          </DialogTitle>
                          <DialogDescription>
                            The following SQL script has been run when setting
                            up all student projects:
                          </DialogDescription>
                        </DialogHeader>
                        <Textarea
                          className="w-full h-[200px]"
                          value={staffViewData.configuration_sql}
                          readOnly
                        />
                        <DialogFooter>
                          <DialogClose asChild>
                            <Button variant="outline">Close</Button>
                          </DialogClose>
                        </DialogFooter>
                      </DialogContent>
                    </Dialog>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
          <div className="flex flex-col gap-3">
            <div className="flex flex-row w-full items-center justify-between">
              <p className="text-lg font-bold">
                {staffViewData.is_group ? "Group" : "Student"} projects
              </p>
              {staffViewData.is_group && (
                <Dialog>
                  <DialogTrigger asChild>
                    <Button variant="outline">
                      <Pencil /> Edit groups
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="sm:max-w-[800px]">
                    <DialogTitle className="hidden">
                      Manage groups for this assignment
                    </DialogTitle>
                    <AssignmentGroupManager
                      courseId={courseId}
                      assignmentId={assignmentId}
                      refetch={() => {
                        queryClient.refetchQueries({
                          queryKey: [
                            "get",
                            "/api/assignment/{assignment_id}/group-projects",
                          ],
                        });
                        queryClient.refetchQueries({
                          queryKey: [
                            "get",
                            "/api/assignment/{assignment_id}/groups",
                          ],
                        });
                      }}
                    />
                  </DialogContent>
                </Dialog>
              )}
            </div>

            {!!individualProjectData && (
              <DataTable
                columns={individualProjectsColumns}
                data={individualProjectData.projects}
              />
            )}
            {!!individualProjectError && (
              <ErrorMessage resource="student projects" />
            )}
            {!!groupProjectData && (
              <DataTable
                columns={groupProjectsColumns}
                data={groupProjectData.projects}
              />
            )}
            {!!groupProjectError && <ErrorMessage resource="group projects" />}
            <Card className="mt-3">
              <CardContent className="px-4">
                <div className="flex flex-row gap-5 items-center">
                  <FileDown className="size-6 flex-shrink-0 text-accent-foreground/60" />
                  <div className="flex flex-col flex-grow gap-1">
                    <p className="font-semibold">Export project databases</p>
                    <p className="text-accent-foreground/80">
                      Downloads a zip file containing SQL scripts to recreate
                      all student databases, including all tables and data.
                      Great for offline grading or as input to a configured
                      autograder.
                    </p>
                  </div>
                  <Button
                    type="submit"
                    disabled={isExportingDatabase}
                    onClick={onExportButtonPressed}
                    className="flex-shrink-0"
                  >
                    {isExportingDatabase ? (
                      <>
                        <Loader2Icon className="animate-spin" />
                        Exporting...
                      </>
                    ) : (
                      <>Export</>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
          <div className="flex flex-col gap-3">
            <p className="text-lg font-bold">Danger zone</p>
            <Card>
              <CardContent className="px-4">
                {staffViewData.state === "published" && (
                  <div className="flex flex-row gap-5 items-center">
                    <EyeOff className="size-6 flex-shrink-0 text-accent-foreground/60" />
                    <div className="flex flex-col flex-grow gap-1">
                      <p className="font-semibold">Unpublish assignment</p>
                      <p className="text-accent-foreground/80">
                        The assignment will no longer be visible to students and
                        students will lose access to their projects. Staff can
                        still access the assignment and projects. Great for
                        grading after the assignment deadline has passed.{" "}
                        <em>
                          Student access can be restored by re-publishing the
                          assignment.
                        </em>
                      </p>
                    </div>
                    <UnpublishAssignmentDialog assignmentId={assignmentId}>
                      <Button variant="outline" className="flex-shrink-0">
                        Unpublish
                      </Button>
                    </UnpublishAssignmentDialog>
                  </div>
                )}
                {staffViewData.state === "unpublished" && (
                  <div className="flex flex-row gap-5 items-center">
                    <Eye className="size-6 flex-shrink-0 text-accent-foreground/60" />
                    <div className="flex flex-col flex-grow gap-1">
                      <p className="font-semibold">Republish assignment</p>
                      <p className="text-accent-foreground/80">
                        The assignment will no longer be visible to students and
                        students will lose access to their projects. Staff can
                        still access the assignment and projects. Great for
                        grading after the assignment deadline has passed.{" "}
                        <em>
                          Student access can be restored by re-publishing the
                          assignment.
                        </em>
                      </p>
                    </div>
                    <RepublishAssignmentDialog assignmentId={assignmentId}>
                      <Button variant="outline" className="flex-shrink-0">
                        Republish
                      </Button>
                    </RepublishAssignmentDialog>
                  </div>
                )}
                <Separator className="my-6" />
                <div className="flex flex-row gap-5 items-center">
                  <Trash className="size-6 flex-shrink-0 text-destructive" />
                  <div className="flex flex-col flex-grow gap-1">
                    <p className="font-semibold">Delete assignment</p>
                    <p className="text-accent-foreground/80">
                      All student projects will be deleted and data will not be
                      recoverable.
                    </p>
                  </div>
                  <DeleteAssignmentDialog
                    courseId={courseId}
                    assignmentId={assignmentId}
                    assignmentName={staffViewData.name}
                  >
                    <Button variant="destructive" className="flex-shrink-0">
                      Delete
                    </Button>
                  </DeleteAssignmentDialog>
                </div>
              </CardContent>
            </Card>
          </div>
        </>
      )}
    </div>
  );
}
