import { LockKeyholeOpen } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Field, FieldGroup } from "@/components/ui/field";
import { dabblebase } from "@/utils/dabblebase/client";

export default function HomePage() {
  const authenticate = async () => {
    dabblebase.auth.signIn({
      provider: "unc",
      continueTo: "/authenticated",
    });
  };

  return (
    <div className="bg-background flex min-h-svh flex-col items-center justify-center gap-6 p-6 md:p-10">
      <div className="w-full max-w-sm">
        <div className="flex flex-col gap-6">
          <FieldGroup>
            <div className="flex flex-col items-center gap-2 text-center">
              <div className="flex flex-col items-center gap-2 font-medium">
                <div className="flex size-8 items-center justify-center rounded-md">
                  <LockKeyholeOpen className="size-6" />
                </div>
                <span className="sr-only">Auth Example</span>
              </div>
              <h1 className="text-xl font-bold">Dabblebase Auth Example</h1>
            </div>
            <Field>
              <Button onClick={authenticate}>Authenticate</Button>
            </Field>
          </FieldGroup>
        </div>
      </div>
    </div>
  );
}
