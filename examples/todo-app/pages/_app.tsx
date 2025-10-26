import { ThemeProvider } from "@/components/theme-provider";
import "@/styles/globals.css";
import { api } from "@/utils/trpc/api";
import type { AppProps } from "next/app";
import { Toaster } from "sonner";

function App({ Component, pageProps }: AppProps) {
  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="dark"
      enableSystem
      disableTransitionOnChange
    >
      <Component {...pageProps} />
      <Toaster richColors />
    </ThemeProvider>
  );
}

export default api.withTRPC(App);
