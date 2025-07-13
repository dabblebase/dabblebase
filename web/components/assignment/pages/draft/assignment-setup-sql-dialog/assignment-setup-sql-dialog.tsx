import { Button } from "@/components/ui/button";
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
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Textarea } from "@/components/ui/textarea";
import { RotateCcw, Undo2 } from "lucide-react";
import { useEffect, useState } from "react";
import SQLTestErrorCard from "./sql-test-error-card";
import SQLTestSuccessCard from "./sql-test-success-card";
import { toast } from "sonner";
import { useConfigurationSql } from "@/hooks/api/assignment/use-configuration-sql";

export default function AssignmentSetupSQLDialog({
  assignmentId,
  children,
}: {
  assignmentId: number;
  children: React.ReactNode;
}) {
  const {
    sqlData,
    testConfigurationSQL,
    saveConfigurationSQL,
    removeConfigurationSQL,
    resetConfigurationSQL,
    refetchOnSuccess,
  } = useConfigurationSql(assignmentId);

  const onTestButtonPressed = () => {
    testConfigurationSQL(
      {
        params: {
          path: {
            assignment_id: assignmentId,
          },
        },
        body: {
          sql: sqlText,
        },
      },
      {
        onSuccess: () => {
          refetchOnSuccess();
        },
      }
    );
  };

  const onSaveButtonPressed = () => {
    saveConfigurationSQL(
      { params: { path: { assignment_id: assignmentId } } },
      {
        onSuccess: () => {
          refetchOnSuccess();
          setOpen(false);
        },
        onError: () => {
          toast.error("Error saving SQL configuration", {
            description: "Please try again.",
          });
        },
      }
    );
  };

  const onRemoveButtonPressed = () => {
    removeConfigurationSQL(
      { params: { path: { assignment_id: assignmentId } } },
      {
        onSuccess: () => {
          refetchOnSuccess();
          setSqlText("");
        },
        onError: () => {
          toast.error("Error removing the SQL configuration", {
            description: "Please try again.",
          });
        },
      }
    );
  };

  const onResetButtonPressed = () => {
    resetConfigurationSQL(
      { params: { path: { assignment_id: assignmentId } } },
      {
        onSuccess: () => {
          refetchOnSuccess();
          setSqlText("");
        },
        onError: () => {
          toast.error("Error resetting the SQL configuration", {
            description: "Please try again.",
          });
        },
      }
    );
  };

  const [open, setOpen] = useState<boolean>(false);

  const [sqlText, setSqlText] = useState<string>("");

  useEffect(() => {
    if (!sqlData) return;
    if (!!sqlData.sql_draft) {
      setSqlText(sqlData.sql_draft);
    } else if (!!sqlData.sql) {
      setSqlText(sqlData.sql);
    }
  }, [sqlData]);

  return (
    <>
      {!!sqlData && (
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>{children}</DialogTrigger>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>Configure Startup SQL</DialogTitle>
              <DialogDescription>
                Set a SQL script to run on each student&apos;s project database
                when created. This is useful for pre-populating student
                databases with tables, data, and more.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 mt-2">
              <Label className="font-semibold">SQL script</Label>
              <Textarea
                className="h-48"
                placeholder={`ex)\nCREATE TABLE placeholder_table (\n\tid INT,\n\tname TEXT,\n\tcreated_at TIMESTAMP\n);`}
                value={sqlText}
                onChange={(e) => setSqlText(e.target.value)}
              />
              {sqlData.sql_draft_error && (
                <SQLTestErrorCard error={sqlData.sql_draft_error} />
              )}
              {((sqlData.sql && sqlData.sql === sqlText) ||
                (sqlData.sql_draft &&
                  !sqlData.sql_draft_error &&
                  sqlData.sql_draft === sqlText)) && (
                <SQLTestSuccessCard dbUrl={sqlData.db_url || ""} />
              )}
              <div className="flex flex-row w-full gap-2">
                {!!sqlData.sql &&
                  sqlData.sql !== null &&
                  !!sqlData.sql_draft &&
                  sqlText !== sqlData.sql &&
                  sqlText === sqlData.sql_draft && (
                    <Button variant="outline" onClick={onResetButtonPressed}>
                      <RotateCcw className="size-4" />
                      Reset
                    </Button>
                  )}

                {((sqlData.sql_draft && sqlText !== sqlData.sql_draft) ||
                  (!sqlData.sql_draft &&
                    sqlData.sql &&
                    sqlText !== sqlData.sql)) && (
                  <Button
                    variant="outline"
                    onClick={() => {
                      if (!!sqlData.sql_draft) {
                        setSqlText(sqlData.sql_draft!);
                      } else {
                        setSqlText(sqlData.sql!);
                      }
                    }}
                  >
                    <Undo2 className="size-4" />
                    Undo
                  </Button>
                )}
                {sqlText.length > 0 && (
                  <Button
                    className="ml-auto"
                    onClick={onTestButtonPressed}
                    disabled={
                      sqlText === sqlData.sql ||
                      sqlText == sqlData.sql_draft ||
                      sqlText.length === 0
                    }
                  >
                    Test
                  </Button>
                )}
              </div>
            </div>
            <Separator />
            <DialogFooter>
              <DialogClose asChild>
                <Button className="mr-auto" variant="outline">
                  Cancel
                </Button>
              </DialogClose>
              {sqlData.sql_draft &&
                sqlData.sql_draft.length > 0 &&
                sqlData.sql_draft === sqlText &&
                sqlData.sql_draft_success === true && (
                  <Button className="ml-auto" onClick={onSaveButtonPressed}>
                    Save
                  </Button>
                )}
              {!!sqlData.sql &&
                sqlData.sql.length > 0 &&
                sqlText.length === 0 && (
                  <Button className="ml-auto" onClick={onRemoveButtonPressed}>
                    Remove Startup SQL
                  </Button>
                )}
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}
    </>
  );
}
