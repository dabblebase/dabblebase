import { api } from "@/utils/api";
import { Avatar, AvatarFallback, AvatarImage } from "../ui/avatar";
import { Button } from "../ui/button";
import Link from "next/link";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "../ui/dropdown-menu";
import { LogOut } from "lucide-react";
import { useLogOut } from "@/utils/auth";

/** Note: children passed in are placed to the left of the user avatar when logged-in. */
export default function UserHeaderSection({
  children,
}: {
  children?: React.ReactNode;
}) {
  const { data: profile, isLoading: profileLoading } = api.useQuery(
    "get",
    "/api/profile/summary"
  );

  const { logOut } = useLogOut();

  return (
    <div className="flex flex-row gap-3 w-full sm:ml-auto sm:w-auto">
      {!!profile && (
        <div className="flex flex-row gap-4 items-center">
          {children}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                className="h-8 w-8 rounded-full hover:cursor-pointer"
              >
                <Avatar className="size-9">
                  <AvatarImage src="" />
                  <AvatarFallback>{profile.initials}</AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-64" align="end">
              <DropdownMenuLabel>
                <div className="flex flex-col">
                  <p className="font-semibold text-foreground">
                    {profile.first_name} {profile.last_name}
                  </p>
                  <span className="text-sm">{profile.email}</span>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuGroup>
                <DropdownMenuItem onClick={logOut}>
                  <LogOut className="text-popover-foreground" />
                  Log out
                </DropdownMenuItem>
              </DropdownMenuGroup>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      )}
      {!profile && !profileLoading && (
        <>
          <Button asChild variant="outline">
            <Link href="/login">Sign in</Link>
          </Button>
          <Button asChild variant="default">
            <Link href="/login">Get started</Link>
          </Button>
        </>
      )}
    </div>
  );
}
