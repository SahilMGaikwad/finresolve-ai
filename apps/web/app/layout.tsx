import { Inter } from "next/font/google";
import "../styles/globals.css";
import { Navigation } from "../components/layout/Navigation";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-sans",
});

export const metadata = {
  title: "FinResolve AI — Financial Reconciliation Operations",
  description: "Enterprise Financial Operations & Counterfactual Resolution Workstation",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.variable}>
      <body className={inter.className}>
        <div className="app-container">
          <Navigation />
          <main className="main-content">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
