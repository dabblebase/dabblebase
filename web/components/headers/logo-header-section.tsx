import Link from "next/link";

export default function LogoHeaderSection() {
  return (
    <Link href="/" className="flex items-center gap-2 font-bold">
      {/* <Logo className="size-6" /> */}
      <span>dabblebase</span>
    </Link>
  );
}
