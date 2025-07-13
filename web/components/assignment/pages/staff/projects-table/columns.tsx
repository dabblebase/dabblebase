import type { components } from "@/models/schema";
import { ColumnDef } from "@tanstack/react-table";
import ProjectsTableActionsRow from "./actions-row";

type StudentProject =
  components["schemas"]["GetStudentProjectsResponse_Project"];

type GroupProject = components["schemas"]["GetGroupProjectsResponse_Project"];

export const individualProjectsColumns: ColumnDef<StudentProject>[] = [
  {
    accessorKey: "user_name",
    header: () => <span className="font-semibold">Name</span>,
    cell: ({ row }) => <span>{row.original.user_name}</span>,
  },
  {
    accessorKey: "actions",
    header: () => <></>,
    cell: ({ row }) => {
      const project = row.original;

      return (
        <ProjectsTableActionsRow
          projectName={project.user_name}
          studentEmails={project.user_email}
          dbUrl={project.db_url}
        />
      );
    },
  },
];

export const groupProjectsColumns: ColumnDef<GroupProject>[] = [
  {
    accessorKey: "group_name",
    header: () => <span className="font-semibold">Group Name</span>,
    cell: ({ row }) => <span>{row.original.group_name}</span>,
  },
  {
    accessorKey: "group_members",
    header: () => <span className="font-semibold">Group Members</span>,
    cell: ({ row }) => <span>{row.original.group_members.join(", ")}</span>,
  },
  {
    accessorKey: "actions",
    header: () => <></>,
    cell: ({ row }) => {
      const project = row.original;

      return (
        <ProjectsTableActionsRow
          projectName={project.group_name}
          studentEmails={project.group_member_emails.join(",")}
          dbUrl={project.db_url}
        />
      );
    },
  },
];
