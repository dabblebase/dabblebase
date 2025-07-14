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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { components } from "@/models/schema";
import { ColumnDef } from "@tanstack/react-table";
import { Trash } from "lucide-react";

type Member = components["schemas"]["GetRosterResponse_Member"];
type Role = components["schemas"]["CourseMembershipRole"];

export const rosterColumnsGenerator = (
  role: Role,
  onRoleChange: (userId: number, role: Role) => void,
  onRemoveMember: (userId: number) => void
): ColumnDef<Member>[] => {
  return [
    {
      accessorKey: "user_name",
      header: () => <span className="font-semibold">Name</span>,
      cell: ({ row }) => <span>{row.original.user_name}</span>,
    },
    {
      accessorKey: "user_email",
      header: () => <span className="font-semibold">Email</span>,
      cell: ({ row }) => <span>{row.original.user_email}</span>,
    },
    {
      accessorKey: "role",
      header: () => <span className="font-semibold">Role</span>,
      cell: ({ row }) => (
        <Select
          value={row.original.role}
          onValueChange={(value) => {
            onRoleChange(row.original.user_id, value as Role);
          }}
        >
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Select a role." />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="owner" hidden>
              Owner
            </SelectItem>
            {role === "owner" && (
              <>
                <SelectItem value="admin">Admin</SelectItem>
                <SelectItem value="staff">Staff</SelectItem>
                <SelectItem value="student">Student</SelectItem>
              </>
            )}
            {role === "admin" && (
              <>
                <SelectItem value="admin">Admin</SelectItem>
                <SelectItem value="staff">Staff</SelectItem>
              </>
            )}
            {role === "staff" && (
              <>
                <SelectItem value="staff">Staff</SelectItem>
                <SelectItem value="student">Student</SelectItem>
              </>
            )}
          </SelectContent>
        </Select>
      ),
    },
    {
      accessorKey: "actions",
      header: () => <></>,
      cell: ({ row }) => {
        return (
          <div className="ml-auto">
            <Dialog>
              <DialogTrigger asChild>
                <Button variant="outline" size="icon" className="ml-auto">
                  <Trash className="text-destructive" />
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Remove member?</DialogTitle>
                  <DialogDescription className="my-3 text-muted-foreground/80">
                    Are you sure you want to remove {row.original.user_name}?
                    Once removed, they will be unable to access this class or
                    any of their assignments. Projects they created while in the
                    class will remain for grading and archival purposes.
                  </DialogDescription>
                </DialogHeader>
                <DialogFooter>
                  <DialogClose asChild>
                    <Button variant="outline">Cancel</Button>
                  </DialogClose>
                  <Button
                    type="submit"
                    variant="destructive"
                    onClick={() => {
                      onRemoveMember(row.original.user_id);
                    }}
                  >
                    Delete
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        );
      },
    },
  ];
};
