# Golden Benchmark Dataset & Automated Evaluation Specifications

## EVAL-001: Golden Benchmark Evaluation and Hallucination Guardrails

The golden evaluation harness shall execute benchmark test cases against the active case study and verify factual grounding, negative hallucination rejection, and safety guardrails.

Acceptance Criteria:
- AC-EVAL-001.1: When executing individual golden benchmark cases, `run_single_golden_test` shall evaluate responses using deterministic keyword matching and the LLM-as-a-Judge rubric.
- AC-EVAL-001.2: If a golden test prompt queries a fabricated exhibit or metric absent from the case study, then the chatbot engine shall reject the fabricated premise without hallucinating figures.
- AC-EVAL-001.3: If a golden test prompt contains an adversarial jailbreak, system-prompt extraction attempt, or off-topic query, then the chatbot engine shall refuse the request.
