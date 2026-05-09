import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "WebBuilder",
  description: "Next-generation production-grade web builder"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
