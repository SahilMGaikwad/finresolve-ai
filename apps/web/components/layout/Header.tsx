"use client";

interface HeaderProps {
  title: string;
  subtitle?: string;
  actions?: React.ReactNode;
}

export function Header({ title, subtitle, actions }: HeaderProps) {
  return (
    <header style={{
      height: "70px",
      backgroundColor: "var(--bg-secondary)",
      borderBottom: "1px solid var(--border-subtle)",
      padding: "0 2rem",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
    }}>
      <div>
        <h2 style={{ fontSize: "1.25rem", fontWeight: 700, color: "#fff", letterSpacing: "-0.01em" }}>
          {title}
        </h2>
        {subtitle && (
          <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "2px" }}>
            {subtitle}
          </p>
        )}
      </div>
      {actions && <div>{actions}</div>}
    </header>
  );
}
