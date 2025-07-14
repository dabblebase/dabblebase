"use client";
import { Button } from "@/components/ui/button";
import LogoHeaderSection from "./logo-header-section";
import Link from "next/link";
import UserHeaderSection from "./user-header-section";

export function LandingHeader() {
  return (
    <header className="bg-background sticky top-0 z-50 flex w-full items-center border-b">
      <div className="flex h-(--header-height) w-full items-center gap-2 px-4">
        <LogoHeaderSection />
        {/* <Separator orientation="vertical" className="mr-2 h-4" />
        <Breadcrumb className="hidden sm:block">
          <BreadcrumbList>
            <BreadcrumbItem>
              <BreadcrumbLink href="#">
                Building Your Application
              </BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbItem>
              <BreadcrumbPage>Data Fetching</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb> */}
        <UserHeaderSection>
          <Button asChild variant="default">
            <Link href="/dashboard">Dashboard</Link>
          </Button>
        </UserHeaderSection>
      </div>
    </header>
  );
}
