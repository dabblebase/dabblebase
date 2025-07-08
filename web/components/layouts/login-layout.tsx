import { ReactNode } from "react";
import { LoginHeader } from "../headers/login-header";

export default function LoginLayout({ children }: { children: ReactNode }) {
  return (
    <div className="[--header-height:calc(--spacing(16))] relative">
      <LoginHeader />
      <div className="absolute top-0 w-full">{children}</div>
    </div>
  );
}
