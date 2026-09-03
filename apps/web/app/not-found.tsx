import Link from "next/link";
import { Header } from "@/components/layout/Header";

export default function NotFound() {
  return (
    <div>
      <Header
        breadcrumbs={[{ label: "FINRESOLVE", href: "/" }, { label: "404 NOT FOUND" }]}
      />
      <div className="page-body" style={{ textAlign: "center", padding: "5rem 1.5rem" }}>
        <div style={{ fontSize: "10.5px", fontWeight: 800, color: "var(--color-brand)", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: "0.5rem" }}>
          RESOURCE ERROR 404
        </div>
        <h1 className="heading-editorial title-huge">
          PAGE NOT FOUND
        </h1>
        <p style={{ color: "var(--text-muted)", fontSize: "12.5px", maxWidth: "420px", margin: "0.75rem auto 1.5rem" }}>
          The requested financial reconciliation route or resource identifier does not exist in the active ledger.
        </p>
        <Link href="/" className="btn btn-primary">
          RETURN TO OVERVIEW →
        </Link>
      </div>
    </div>
  );
}
