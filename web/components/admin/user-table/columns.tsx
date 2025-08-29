import { Badge } from "@/components/ui/badge";
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
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import type { components } from "@/models/schema";
import { ColumnDef } from "@tanstack/react-table";
import { MoreHorizontal } from "lucide-react";

type User = components["schemas"]["ListUsersResponse_User"];

export const adminUserListColumsGenerator = (
  onAddInstructor: (userId: number) => void,
  onRemoveInstructor: (userId: number) => void
): ColumnDef<User>[] => {
  return [
    {
      accessorKey: "user_name",
      header: () => <span className="font-semibold">Name</span>,
      cell: ({ row }) => (
        <div className="flex flex-row gap-2 items-center">
          <span>{row.original.name}</span>
          {row.original.is_instructor && <Badge>Instructor</Badge>}
        </div>
      ),
    },
    {
      accessorKey: "user_email",
      header: () => <span className="font-semibold">Email</span>,
      cell: ({ row }) => <span>{row.original.email}</span>,
    },
    {
      accessorKey: "actions",
      header: () => <></>,
      cell: ({ row }) => {
        return (
          <div className="flex flex-row items-end px-2">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="h-8 w-8 ml-auto">
                  <MoreHorizontal />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                {!row.original.is_instructor && (
                  <Dialog>
                    <DialogTrigger asChild>
                      <DropdownMenuItem onSelect={(e) => e.preventDefault()}>
                        Add instructor role
                      </DropdownMenuItem>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>
                          Make {row.original.name} an instructor?
                        </DialogTitle>
                        <DialogDescription className="my-3 text-muted-foreground/80">
                          Instructors can create courses on Dabblebase and can
                          provision databases for class assignments.
                        </DialogDescription>
                      </DialogHeader>
                      <DialogFooter>
                        <DialogClose asChild>
                          <Button variant="outline">Cancel</Button>
                        </DialogClose>
                        <Button
                          type="submit"
                          variant="default"
                          onClick={() => {
                            onAddInstructor(row.original.id);
                          }}
                        >
                          Confirm
                        </Button>
                      </DialogFooter>
                    </DialogContent>
                  </Dialog>
                )}
                {row.original.is_instructor && (
                  <Dialog>
                    <DialogTrigger asChild>
                      <DropdownMenuItem onSelect={(e) => e.preventDefault()}>
                        Remove instructor role
                      </DropdownMenuItem>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>
                          Remove instructor permissions?
                        </DialogTitle>
                        <DialogDescription className="my-3 text-muted-foreground/80">
                          Once removed, {row.original.name} will no longer be
                          able to create new courses.
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
                            onRemoveInstructor(row.original.id);
                          }}
                        >
                          Delete
                        </Button>
                      </DialogFooter>
                    </DialogContent>
                  </Dialog>
                )}
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        );
      },
    },
  ];
};
