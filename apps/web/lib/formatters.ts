/**
 * FinResolve AI — Financial Formatting Utilities
 * Handles exact minor currency unit (paise) to INR conversions, ISO timestamps, and status classes.
 */

export function formatINR(minorUnits: number | null | undefined): string {
  if (minorUnits === null || minorUnits === undefined) {
    return "₹0.00";
  }
  const isNegative = minorUnits < 0;
  const absMinor = Math.abs(minorUnits);
  const rupees = Math.floor(absMinor / 100);
  const paise = absMinor % 100;
  const formattedPaise = paise.toString().padStart(2, "0");
  const formattedRupees = rupees.toLocaleString("en-IN");

  return `${isNegative ? "-" : ""}₹${formattedRupees}.${formattedPaise}`;
}

export function formatDateTime(isoString: string | null | undefined): string {
  if (!isoString) return "—";
  try {
    const d = new Date(isoString);
    return d.toLocaleString("en-IN", {
      year: "numeric",
      month: "short",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
    });
  } catch {
    return isoString;
  }
}

export function getStatusBadgeClass(status: string | null | undefined): string {
  const s = (status || "").toLowerCase();
  if (s === "reconciled" || s === "completed" || s === "auto_resolvable" || s === "approved" || s === "processed") {
    return "badge badge-reconciled";
  }
  if (s === "discrepancy" || s === "blocked" || s === "rejected" || s === "failed") {
    return "badge badge-discrepancy";
  }
  if (s === "human_review_required" || s === "human_review" || s === "pending") {
    return "badge badge-review";
  }
  return "badge badge-info";
}
