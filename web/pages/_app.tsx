import "@/styles/globals.css";
import type { AppProps } from "next/app";
import { ThemeProvider } from "@/components/theme/theme-provider";
import { NextPage } from "next";
import { ReactElement, ReactNode } from "react";
import { Open_Sans, IBM_Plex_Mono, Source_Serif_4 } from "next/font/google";

/** Import fonts used by the theme */
const openSans = Open_Sans({
  variable: "--font-open-sans",
  subsets: ["latin"],
});

const ibmPlexMono = IBM_Plex_Mono({
  variable: "--font-ibm-plex-mono",
  subsets: ["latin"],
  weight: ["100", "200", "300", "400", "500", "600", "700"],
});

const sourceSerif4 = Source_Serif_4({
  variable: "--font-source-serif-4",
  subsets: ["latin"],
});

// This type extends NextPage to include a getLayout function that can be used to wrap the page in a specific layout
// component - required for TypeScript type checking
export type NextPageWithLayout<P = unknown, IP = P> = NextPage<P, IP> & {
  getLayout?: (page: ReactElement) => ReactNode;
};

// Type for AppProps that includes the layout functionality
type AppPropsWithLayout = AppProps & {
  Component: NextPageWithLayout;
};

export default function App({ Component, pageProps }: AppPropsWithLayout) {
  // Function to retrieve the component's assigned layout, if any
  const getLayout = Component.getLayout ?? ((page) => page);

  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
    >
      <main
        className={`${openSans.variable} ${ibmPlexMono.variable} ${sourceSerif4.variable}`}
      >
        {getLayout(<Component {...pageProps} />)}
      </main>
    </ThemeProvider>
  );
}
