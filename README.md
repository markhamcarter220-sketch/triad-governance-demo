# Triad Governance Demo (MAG-1)

## What This Is

This repository is an **executable proof**, not a production system, framework, or library.

It demonstrates a governance model that separates three distinct functions:

1. **Sensing** — Gathering information and producing signals
2. **Authority** — Explicit permission to act, granted externally
3. **Execution** — Taking action only when authority is present and unambiguous

This separation creates a **legitimacy boundary**: systems can sense freely, but cannot execute without explicit authority. When multiple sensing agents disagree, the system freezes rather than guessing.

## What This Demo Proves

✓ **Separation of sensing, authority, and execution**
  Signals never grant authority. Authority must be explicit and external.

✓ **Authority conservation**
  Agents cannot self-authorize. Execution requires explicit permission.

✓ **Freeze-on-ambiguity semantics**
  Disagreement between agents → FREEZE (no guessing, no voting, no escalation).

✓ **Multi-Agent Strengthening (MAG-1)**
  Multiple agents can strengthen confidence when they agree, but a single disagreement freezes execution.

## What This Does NOT Claim

✗ This is not a complete governance system
✗ This is not production-ready code
✗ This is not a framework for building AI applications
✗ This does not solve alignment, safety, or control problems
✗ This does not address all governance concerns

This is a **minimal proof** that the triad model can be implemented and tested.

## How to Run the Demo

```bash
python triad_demo.py
```

The demo runs 5 test cases:
1. Single agent with authority → EXECUTE
2. Multiple agents agree with authority → EXECUTE
3. Agents disagree → FREEZE
4. Authority missing → FREEZE
5. Adversarial escalation attempt → FREEZE

## How to Run Tests

```bash
python -m pytest tests/test_triad_demo.py -v
```

Or run tests directly without pytest:
```bash
python tests/test_triad_demo.py
```

## References

This demo implements concepts from:
- **Governance Kernel** — The foundational model separating sensing, authority, and execution
- **MAG-1 (Multi-Agent Governance Strengthening)** — Using multiple agents to strengthen confidence while preserving freeze-on-ambiguity

## Structure

- `triad_demo.py` — Single-file executable demonstration
- `tests/test_triad_demo.py` — Test suite verifying invariants
- `README.md` — This file

## Key Invariants (Enforced by `authority_gate()`)

1. Signals never grant authority
2. Authority must be explicit
3. Disagreement → FREEZE (no voting, no majority rule)
4. Agents cannot self-authorize

## Why This Matters

Most AI systems conflate sensing with authority: if a model outputs a decision, that decision gets executed. This demo shows an alternative where:
- Multiple models can sense and evaluate
- Agreement strengthens confidence
- Disagreement triggers a freeze (preserving legitimacy)
- Execution requires explicit external authority

This is legitimacy preservation, not intelligence amplification.
