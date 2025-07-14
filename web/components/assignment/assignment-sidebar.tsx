import { Archive, Database, MousePointer, UserLock } from "lucide-react";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "../ui/sidebar";
import { useRouter } from "next/router";
import { cn } from "@/utils/cn";

export default function AssignmentSidebar() {
  return (
    <Sidebar
      className="top-(--header-height) h-[calc(100svh-var(--header-height))]! w-[calc(var(--sidebar-width-icon)+1px)]! border-r"
      collapsible="none"
    >
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              <AssignmentSidebarItem
                icon={Database}
                tooltip="Database"
                selectedPath="database"
              />
              <AssignmentSidebarItem
                icon={UserLock}
                tooltip="Authentication"
                selectedPath="auth"
              />
              <AssignmentSidebarItem
                icon={Archive}
                tooltip="Storage"
                selectedPath="storage"
              />
              <AssignmentSidebarItem
                icon={MousePointer}
                tooltip="Realtime"
                selectedPath="realtime"
              />
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
}
export function AssignmentSidebarItem({
  icon: Icon,
  tooltip,
  selectedPath,
}: {
  icon: React.ComponentType<{ className?: string }>;
  tooltip: string;
  selectedPath: string;
}) {
  const router = useRouter();
  // Determine the selected item by the current URL path's final path segment after `/course/{some number}/assignment/{some number}`
  const currentPath = router.asPath.split("/").pop();
  const isSelected = currentPath === selectedPath;

  const { courseId, assignmentId } = router.query as {
    courseId: string;
    assignmentId: string;
  };

  const onClick = () => {
    if (selectedPath !== currentPath) {
      router.push(
        `/course/${courseId}/assignment/${assignmentId}/${selectedPath}`
      );
    }
  };
  return (
    <SidebarMenuItem>
      <SidebarMenuButton
        size="lg"
        tooltip={{ children: tooltip, hidden: false }}
        className={cn("flex flex-col items-center justify-center", {
          "bg-primary text-primary-foreground": isSelected,
          "hover:bg-sidebar-accent hover:text-sidebar-accent-foreground":
            !isSelected,
          "hover:bg-primary hover:text-primary-foreground": isSelected,
          "active:bg-primary active:text-primary-foreground": isSelected,
        })}
        onClick={onClick}
      >
        <Icon className="size-5!" />
      </SidebarMenuButton>
    </SidebarMenuItem>
  );
}
