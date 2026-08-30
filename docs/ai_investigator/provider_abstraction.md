# FinResolve AI — LLM Provider Abstraction

## 1. Provider Protocol

```python
class LLMProvider(ABC):
    @abstractmethod
    def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: type[T],
    ) -> T:
        pass
```

---

## 2. Supported Implementations

1. **`MockDeterministicLLMProvider`**:
   - Default prototype provider.
   - Synthesizes findings directly from Phase 3 Evidence Graph and diagnostic hypotheses.
   - Runs 100% offline with zero network or credential dependencies.
2. **Pluggable Adapters**:
   - Designed to support `OpenAILLMProvider`, `AnthropicLLMProvider`, and `GeminiLLMProvider` for production environments.

---

## 3. Fallback Mechanism

If the active LLM provider raises an exception, times out, or returns invalid JSON:
1. An error is logged in the audit trace.
2. The [`DeterministicInvestigatorFallback`](file:///Users/sahilgaikwad/finresolve-ai/services/investigator/fallback.py) immediately synthesizes rule-based findings.
3. The case safely transitions to `HUMAN_REVIEW_REQUIRED`.
