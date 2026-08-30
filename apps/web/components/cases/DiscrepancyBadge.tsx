import { getStatusBadgeClass } from "@/lib/formatters";

interface DiscrepancyBadgeProps {
  status?: string;
  count?: number;
  label?: string;
}

export function DiscrepancyBadge({ status, count, label }: DiscrepancyBadgeProps) {
  if (count !== undefined) {
    if (count === 0) {
      return (
        <span className="badge badge-reconciled" style={{ fontSize: "0.68rem" }}>
          ✓ Clean (0)
        </span>
      );
    }
    return (
      <span className="badge badge-discrepancy" style={{ fontSize: "0.68rem" }}>
        ⚠️ {count} {count === 1 ? "Discrepancy" : "Discrepancies"}
      </span>
    );
  }

  const currentStatus = status || "reconciled";
  const badgeClass = getStatusBadgeClass(currentStatus);
  const displayLabel = label || currentStatus.replace(/_/g, " ");

  return <span className={badgeClass}>{displayLabel}</span>;
}
