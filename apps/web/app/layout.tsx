import "../styles/globals.css";
import { Navigation } from "../components/layout/Navigation";

export const metadata = {
  title: "FinResolve AI — Analyst Command Center",
  description: "Counterfactual Financial Reconciliation & Resolution Engine",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
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
