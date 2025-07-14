import Link from "next/link";
import DabblebaseLogo from "../theme/logo";

export default function LogoHeaderSection() {
  return (
    <Link href="/" className="flex items-center gap-3 font-bold">
      <DabblebaseLogo />
      <span>dabblebase</span>
    </Link>
  );
}
