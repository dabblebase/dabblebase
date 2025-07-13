import ErrorMessage from "@/components/errors/error-message";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { api } from "@/utils/api";
import { useQueryClient } from "@tanstack/react-query";
import { CircleCheck, CircleSlash } from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import AssignmentSetupSQLDialog from "@/components/assignment/pages/draft/assignment-setup-sql-dialog/assignment-setup-sql-dialog";
import { Skeleton } from "@/components/ui/skeleton";
import AssignmentGroupManager from "./assignment-group-manager/assignment-group-manager";
import RenameComponent from "@/components/ui/rename";
import { Separator } from "@/components/ui/separator";
import AssignmentPublishDialog from "./assignment-publish-dialog";

export default function AssignmentDraftPage({
  courseId,
  assignmentId,
}: {
  courseId: number;
  assignmentId: number;
}) {
  const queryClient = useQueryClient();

  const {
    data: draftData,
    isLoading: draftDataLoading,
    isError: draftDataError,
    refetch: refetchDraftData,
  } = api.useQuery("get", "/api/assignment/{assignment_id}/draft", {
    params: {
      path: {
        assignment_id: assignmentId,
      },
    },
  });

  const { data: sqlData, isLoading: sqlDataLoading } = api.useQuery(
    "get",
    "/api/assignment/{assignment_id}/configuration-sql",
    {
      params: {
        path: {
          assignment_id: assignmentId,
        },
      },
    }
  );

  // Hooks and mutations for renaming the assignment
  const [renameText, setRenameText] = useState("");

  useEffect(() => {
    if (draftData) {
      setRenameText(draftData.name);
    }
  }, [draftData]);

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
          refetchDraftData();
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
      {draftDataLoading && <p>Loading...</p>}
      {draftDataError && <ErrorMessage resource="assignment" />}
      {!!draftData && (
        <>
          <h1 className="text-2xl font-semibold">
            New {draftData?.is_group ? "Group" : "Individual"} Assignment
          </h1>
          <div className="flex flex-col gap-2">
            <p className="text-lg font-bold">Assignment name</p>
            <RenameComponent
              initialValue={draftData.name}
              value={renameText}
              setValue={setRenameText}
              placeholder="ex) a04: Wordle"
              onRename={renameAssignmentHandler}
            />
          </div>
          <div className="flex flex-col gap-3">
            <p className="text-lg font-bold">Configuration</p>
            {sqlDataLoading && (
              <Skeleton className="w-full h-[150px] rounded-xl" />
            )}
            {!!sqlData && (
              <Card>
                <CardContent className="px-4">
                  <div className="flex flex-row gap-5 items-center">
                    {!!sqlData.sql ? (
                      <CircleCheck className="size-6 flex-shrink-0 text-accent-foreground/60" />
                    ) : (
                      <CircleSlash className="size-6 flex-shrink-0 text-accent-foreground/60" />
                    )}
                    <div className="flex flex-col flex-grow gap-1">
                      <p className="font-semibold">
                        Run SQL on database creation
                      </p>
                      <p className="text-accent-foreground/80">
                        Set a SQL script to run on each student&apos;s project
                        database when created. This is useful for pre-populating
                        student databases with tables, data, and more.
                      </p>
                    </div>
                    <AssignmentSetupSQLDialog assignmentId={assignmentId}>
                      <Button className="flex-shrink-0">
                        {!!sqlData.sql ? "Edit" : "Set up"}
                      </Button>
                    </AssignmentSetupSQLDialog>
                  </div>
                </CardContent>
              </Card>
            )}
            <em>
              Once the assignment is published, this configuration cannot be
              changed.
            </em>
          </div>
          {draftData.is_group && (
            <AssignmentGroupManager
              courseId={courseId}
              assignmentId={assignmentId}
            />
          )}
          <div className="flex flex-col gap-4">
            <Separator className="my-auto w-full bg-border/50" />
            <AssignmentPublishDialog
              courseId={courseId}
              assignmentId={assignmentId}
            >
              <Button className="ml-auto">Publish</Button>
            </AssignmentPublishDialog>
          </div>
        </>
      )}
    </div>
  );
}
