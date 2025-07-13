import { Button } from "@/components/ui/button";
import CopyText from "@/components/ui/copy-text";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Ellipsis, Mail, Plug } from "lucide-react";

export default function ProjectsTableActionsRow({
  projectName,
  studentEmails,
  dbUrl,
}: {
  projectName: string;
  studentEmails: string;
  dbUrl: string;
}) {
  return (
    <div className="flex flex-row w-full px-3 gap-3">
      {/* Connect to database button */}
      <TooltipProvider delayDuration={0} skipDelayDuration={0}>
        <Popover>
          <Tooltip>
            <PopoverTrigger asChild>
              <TooltipTrigger asChild>
                <Button variant="outline" size="icon" className="ml-auto">
                  <Plug />
                </Button>
              </TooltipTrigger>
            </PopoverTrigger>
            <TooltipContent>
              <p>Connect to database</p>
            </TooltipContent>
          </Tooltip>
          <PopoverContent className="flex flex-col gap-2 w-80" align="end">
            <p className="text-sm font-bold">Connect to database</p>
            <p className="text-sm text-accent-foreground/80">
              Access {projectName}&apos;s database as the admin user using the
              database URL below:
            </p>
            <CopyText text={dbUrl} />
          </PopoverContent>
        </Popover>
      </TooltipProvider>
      {/* Dropdown menu */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="icon">
            <Ellipsis className="size-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem
            onClick={() => {
              window.location.href = `mailto:${studentEmails}`;
            }}
          >
            <Mail className="text-accent-foreground" />
            Contact
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}
