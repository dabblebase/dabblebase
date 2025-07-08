import LoginLayout from "@/components/layouts/login-layout";
import { Button } from "@/components/ui/button";
import { GalleryVerticalEnd, GraduationCap } from "lucide-react";

export default function LoginPage() {
  return (
    <div className="bg-background flex min-h-svh flex-col items-center justify-center gap-6 p-6 md:p-10">
      <div className="w-full max-w-sm">
        <div className="flex flex-col gap-6">
          <form>
            <div className="flex flex-col gap-6">
              <div className="flex flex-col items-center gap-2">
                <a
                  href="#"
                  className="flex flex-col items-center gap-2 font-medium"
                >
                  <div className="flex size-8 items-center justify-center rounded-md">
                    <GalleryVerticalEnd className="size-6" />
                  </div>
                  <span className="sr-only">Acme Inc.</span>
                </a>
                <h1 className="text-xl font-bold">Welcome to Dabblebase!</h1>
                <div className="text-center text-sm">
                  Sign in or sign up below:
                </div>
              </div>
              <div className="flex flex-col gap-6">
                <Button type="submit" className="w-full">
                  <GraduationCap className="size-5 mr-2" />
                  Continue with UNC SSO
                </Button>
              </div>
            </div>
          </form>
          <div className="text-muted-foreground *:[a]:hover:text-primary text-center text-xs text-balance *:[a]:underline *:[a]:underline-offset-4">
            By clicking continue, you agree to our{" "}
            <a href="#">Terms of Service</a> and <a href="#">Privacy Policy</a>.
          </div>
        </div>
      </div>
    </div>
  );
}

/** Assign the home page the login page layout */
LoginPage.getLayout = function getLayout(page: React.ReactNode) {
  return <LoginLayout>{page}</LoginLayout>;
};
