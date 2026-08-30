import { getStatusBadgeClass } from "@/lib/formatters";

interface DiscrepancyBadgeProps {
  status: string;
  label?: string;
}

export function DiscrepancyBadge({ status, label }: DiscrepancyBadgeProps) {
  const badgeClass = getStatusBadgeClass(status);
  const displayLabel = label || status.replace(/_/g, " ");

  return <span className={badgeClass}>{displayLabel}</span>;
}
