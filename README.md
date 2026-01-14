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
- `FAILURE_MODES.md` — Documentation of specific failure patterns prevented by triad governance
- `WHY_THIS_EXISTS.md` — Explanation of why this demo exists and what it proves

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

## What This Demo Does NOT Show

This demo is intentionally limited in scope. It does not demonstrate:

✗ **AI intelligence or learning**
  The "agents" are fixed functions with no machine learning, neural networks, or adaptation. They exist only to show agreement and disagreement patterns.

✗ **Optimization or performance improvements**
  The demo has no performance tuning, caching, or efficiency optimizations. Adding governance is not claimed to improve throughput or latency.

✗ **Correctness guarantees**
  The demo does not prove that decisions are correct, only that authority boundaries are enforced. A system can have perfect governance and still make wrong decisions.

✗ **Better outcomes through autonomy**
  Freezing on ambiguity reduces autonomy by design. This is not presented as an improvement in all contexts—only in contexts where legitimacy preservation matters.

✗ **Operational completeness**
  There is no logging, monitoring, alerting, error recovery, or incident response. These are necessary for real systems but orthogonal to demonstrating the governance model.

✗ **Human oversight mechanisms**
  The demo shows structural separation of authority, but does not implement or demonstrate human review processes, audit trails, or accountability systems.

✗ **Scalability or deployment readiness**
  This code is proof-of-concept quality. It is not hardened, tested for edge cases beyond the core invariants, or designed for production use.

The purpose of this demo is to prove that triad governance can be implemented and that freeze-on-ambiguity is a coherent alternative to guess-and-execute. Everything else is deliberately omitted.

## Additional Documentation

- **[WHY_THIS_EXISTS.md](WHY_THIS_EXISTS.md)** — Explains the real-world problem this demo addresses and why the demo is intentionally minimal
- **[FAILURE_MODES.md](FAILURE_MODES.md)** — Documents specific failure patterns that occur when authority is not explicitly governed
