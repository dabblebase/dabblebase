import { Button } from "@/components/ui/button";
import LandingLayout from "@/components/layouts/landing-layout";
import { useRouter } from "next/router";

export default function LandingPage() {
  const router = useRouter();

  return (
    <div className="space-y-24 px-6 py-16 md:px-12 lg:px-32">
      {/* Hero Section */}
      <section className="text-center space-y-6 max-w-3xl mx-auto my-8">
        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
          The Open Source Backend for the Clasroom
        </h1>
        <p className="text-muted-foreground text-lg">
          With Dabblebase, instructors can set up secure, isolated backends for
          students&apos; projects with built-in database, auth, storage, and
          realtime support.
        </p>
        <div className="flex justify-center gap-4">
          <Button onClick={() => router.push("/login")}>Get Started</Button>
          <Button variant="outline">Read the Docs</Button>
        </div>
      </section>
    </div>
  );
}

/** Assign the home page the landing page layout */
LandingPage.getLayout = function getLayout(page: React.ReactNode) {
  return <LandingLayout>{page}</LandingLayout>;
};
