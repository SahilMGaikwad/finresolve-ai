/**
 * FinResolve AI — Typed API Client
 * Interfaces with the FastAPI backend endpoints with token management and sanitized error handling.
 */

export interface CaseSummary {
  case_id: string;
  merchant_id: string;
  difficulty: string;
  discrepancies_count: number;
  status: string;
  payments_count: number;
  settlements_count: number;
}

export interface CaseDetail {
  case_id: string;
  merchant_id: string;
  difficulty: string;
  status: string;
  observed: {
    payments: any[];
    settlements: any[];
    fees: any[];
    refunds: any[];
    ledger_entries: any[];
    orders: any[];
    payouts: any[];
  };
  discrepancies: any[];
  evidence: any[];
  evidence_graph: {
    nodes: any[];
    edges: any[];
  };
  hypotheses: any[];
}

export interface InvestigationResult {
  investigation_id: string;
  case_id: string;
  status: string;
  summary: string;
  symptoms_identified: string[];
  root_cause_explanation: string;
  supporting_evidence_ids: string[];
  claims: {
    claim_id: string;
    claim_text: string;
    claimed_entity_id: string;
    claimed_field: string;
    claimed_value: any;
    evidence_ids: string[];
    verification_status: "VERIFIED" | "UNSUPPORTED" | "CONTRADICTED";
    verification_reason: string;
  }[];
  unsupported_claims_count: number;
  resolution_plan?: {
    plan_id: string;
    case_id: string;
    overall_strategy: string;
    steps: {
      step_number: number;
      action: {
        action_type: string;
        target_record_id: string;
        target_record_type: string;
        parameters: Record<string, any>;
        justification: string;
      };
      rationale: string;
      expected_intermediate_effect: string;
    }[];
    simulation_result?: {
      is_valid: boolean;
      cumulative_delta: {
        merchant_balance_delta_minor: number;
        fee_balance_delta_minor: number;
        tax_balance_delta_minor: number;
        customer_balance_delta_minor: number;
        net_system_delta_minor: number;
        is_balanced: boolean;
      };
      residual_discrepancies: string[];
      explanation: string;
    };
    policy_decision?: {
      decision: string;
      risk_level: string;
      approval_requirement: string;
      blocking_reasons: string[];
    };
  };
  human_review_package?: {
    case_id: string;
    discrepancies_summary: string[];
    verified_evidence_summary: string[];
    failed_simulations_summary: string[];
    key_ambiguities: string[];
    recommended_analyst_actions: string[];
    priority: string;
  };
  investigation_trace: {
    step_number: number;
    state: string;
    action_taken: string;
    tool_called?: string;
    tool_output_summary?: string;
    timestamp: string;
  }[];
}

export interface AuditEvent {
  event_id: string;
  timestamp: string;
  actor: string;
  actor_role: string;
  request_id: string;
  case_id?: string;
  operation: string;
  result: "SUCCESS" | "FAILURE" | "REJECTED" | "DISCREPANCY_DETECTED";
  reason?: string;
  prev_event_hash: string;
  event_hash: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://finresolve-ai.onrender.com";

class ApiClient {
  private token: string = "dev-token-analyst";

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const headers = {
      "Content-Type": "application/json",
      Authorization: `Bearer ${this.token}`,
      ...(options.headers || {}),
    };

    const res = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    if (!res.ok) {
      let errorDetail = `HTTP ${res.status}: ${res.statusText}`;
      try {
        const errorJson = await res.json();
        if (errorJson.detail) errorDetail = errorJson.detail;
      } catch {}
      throw new Error(errorDetail);
    }

    return res.json() as Promise<T>;
  }

  async listCases(limit = 100, offset = 0): Promise<{ total: number; cases: CaseSummary[] }> {
    return this.request<{ total: number; cases: CaseSummary[] }>(`/cases?limit=${limit}&offset=${offset}`);
  }

  async getCase(caseId: string): Promise<CaseDetail> {
    return this.request<CaseDetail>(`/cases/${caseId}`);
  }

  async seedBenchmark(numCases = 500): Promise<{ status: string; count: number }> {
    return this.request<{ status: string; count: number }>("/cases/seed-benchmark", {
      method: "POST",
      body: JSON.stringify({ num_cases: numCases, seed: 42, corruption_rate: 0.15 }),
    });
  }

  async investigateCase(caseId: string, records: any): Promise<InvestigationResult> {
    return this.request<InvestigationResult>(`/cases/${caseId}/investigate`, {
      method: "POST",
      body: JSON.stringify(records),
    });
  }

  async approveProposal(proposalId: string, comments = ""): Promise<any> {
    return this.request<any>(`/proposals/${proposalId}/approve`, {
      method: "POST",
      body: JSON.stringify({ comments }),
    });
  }

  async rejectProposal(proposalId: string, comments = ""): Promise<any> {
    return this.request<any>(`/proposals/${proposalId}/reject`, {
      method: "POST",
      body: JSON.stringify({ comments }),
    });
  }

  async getAuditEvents(caseId?: string): Promise<{ total_events: number; is_tamper_free: boolean; events: AuditEvent[] }> {
    const q = caseId ? `?case_id=${caseId}` : "";
    return this.request<{ total_events: number; is_tamper_free: boolean; events: AuditEvent[] }>(`/audit/events${q}`);
  }

  async getHealth(): Promise<{ status: string; version: string; environment: string; phase: string }> {
    return this.request<{ status: string; version: string; environment: string; phase: string }>("/health");
  }

  async getReady(): Promise<{ status: string; checks: Record<string, string> }> {
    return this.request<{ status: string; checks: Record<string, string> }>("/ready");
  }

  async getMetrics(): Promise<Record<string, any>> {
    return this.request<Record<string, any>>("/metrics");
  }
}

export const api = new ApiClient();
