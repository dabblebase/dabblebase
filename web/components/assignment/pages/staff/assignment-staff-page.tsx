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
import { api } from "@/utils/api";
import { DialogTitle } from "@radix-ui/react-dialog";
import { useQueryClient } from "@tanstack/react-query";
import { CircleCheck, CircleSlash } from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import {
  groupProjectsColumns,
  individualProjectsColumns,
} from "./projects-table/columns";
import { DataTablePagination } from "@/components/ui/data-table-pagination";

export default function AssignmentStaffPage({
  assignmentId,
}: {
  assignmentId: number;
}) {
  const queryClient = useQueryClient();

  const {
    data: staffViewData,
    isLoading: staffViewLoading,
    isError: staffViewError,
    refetch: refetchStaffViewData,
  } = api.useQuery("get", "/api/assignment/{assignment_id}/staff-view", {
    params: {
      path: {
        assignment_id: assignmentId,
      },
    },
  });

  const {
    data: individualProjectData,
    isLoading: individualProjectLoading,
    isError: individualProjectError,
  } = api.useQuery(
    "get",
    "/api/assignment/{assignment_id}/student-projects",
    {
      params: {
        path: {
          assignment_id: assignmentId,
        },
      },
    },
    {
      enabled: !!staffViewData && staffViewData.is_group === false,
    }
  );

  const {
    data: groupProjectData,
    isLoading: groupProjectLoading,
    isError: groupProjectError,
  } = api.useQuery(
    "get",
    "/api/assignment/{assignment_id}/group-projects",
    {
      params: {
        path: {
          assignment_id: assignmentId,
        },
      },
    },
    {
      enabled: !!staffViewData && staffViewData.is_group === true,
    }
  );

  // Hooks and mutations for renaming the assignment
  const [renameText, setRenameText] = useState("");

  useEffect(() => {
    if (staffViewData) {
      setRenameText(staffViewData.name);
    }
  }, [staffViewData]);

  const { mutate: renameAssignment } = api.useMutation(
    "put",
    "/api/assignment/{assignment_id}/rename"
  );

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
            <p className="text-lg font-bold">
              {staffViewData.is_group ? "Group" : "Student"} projects
            </p>
            {!!individualProjectData && (
              <DataTable
                columns={individualProjectsColumns}
                data={individualProjectData.projects}
              />
            )}
            {!!groupProjectData && (
              <DataTable
                columns={groupProjectsColumns}
                data={groupProjectData.projects}
              />
            )}
          </div>
        </>
      )}
    </div>
  );
}
