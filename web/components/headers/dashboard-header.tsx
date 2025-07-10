"use client";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbSeparator,
} from "../ui/breadcrumb";
import { GalleryVerticalEnd, SlashIcon } from "lucide-react";
import { ReactNode } from "react";
import UserHeaderSection from "./user-header-section";

export function DashboardHeader({ children }: { children: ReactNode }) {
  return (
    <header className="bg-background sticky top-0 z-50 flex w-full items-center border-b">
      <div className="flex h-(--header-height) w-full items-center gap-2 px-4">
        <Breadcrumb className="hidden sm:block">
          <BreadcrumbList>
            <BreadcrumbItem>
              <BreadcrumbLink href="/dashboard">
                <GalleryVerticalEnd className="size-4" />
              </BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator>
              <SlashIcon className="size-4 mx-1" />
            </BreadcrumbSeparator>
            {children}
          </BreadcrumbList>
        </Breadcrumb>
        <UserHeaderSection />
      </div>
    </header>
  );
}
