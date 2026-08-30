# Deterministic Evidence Graph UI Specification

## 1. Overview
The **Evidence Graph Canvas** (`apps/web/components/graph/EvidenceGraphCanvas.tsx`) renders the multi-entity relationship graph constructed by `services/evidence/graph.py`.

## 2. Visual & Interaction Design
- **Supported Node Types**:
  - `Payment` (Emerald)
  - `Settlement` (Sky Blue)
  - `Fee` (Amber)
  - `Ledger Entry` (Indigo)
- **Supported Edge Types**:
  - `PAYS_FOR`, `SETTLES`, `CHARGES`, `POSTS_TO`, `REFERENCES`, `CONFLICTS_WITH`, `SUPPORTS`.
- **Discrepancy Indication**: Broken or conflicting relationships are rendered with crimson dashed lines and weighted strokes.
- **Node Selection Drawer**: Clicking any node opens the entity inspector showing entity IDs, type metadata, and degree connectivity.
- **Accessibility View**: A button toggles the view to an accessible HTML table (`AccessibleGraphList.tsx`) for screen readers and keyboard navigation.
