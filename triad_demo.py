#!/usr/bin/env python3
"""
Triad Governance Demo (MAG-1)

This is a minimal executable proof demonstrating:
- Separation of sensing, authority, and execution
- Authority conservation (agents cannot self-authorize)
- Freeze-on-ambiguity semantics
- Multi-agent strengthening (MAG-1)

This is NOT a framework. It is a proof artifact.
"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class Action(Enum):
    """
    Possible actions an agent might recommend.

    WHY: We need a concrete action space to demonstrate governance.
    This is intentionally minimal.
    """
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    ESCALATE = "ESCALATE"  # Adversarial agents might try this


class Decision(Enum):
    """
    The governance decision: execute or freeze.

    WHY: The triad model has exactly two outcomes:
    - EXECUTE: Authority present, no ambiguity
    - FREEZE: Authority missing OR ambiguity detected
    """
    EXECUTE = "EXECUTE"
    FREEZE = "FREEZE"


@dataclass
class AgentOutput:
    """
    What an agent produces: a signal (recommended action) and reasoning.

    WHY: Agents sense and signal. They do NOT grant authority.
    The 'recommended_action' is a signal, not a command.
    """
    agent_name: str
    recommended_action: Action
    reasoning: str

    # Agents might CLAIM they have authority, but this should be ignored
    # WHY: Testing that the system rejects self-authorization attempts
    claims_authority: bool = False


@dataclass
class GovernanceResult:
    """
    The output of the authority gate.

    WHY: The gate produces a decision (EXECUTE or FREEZE) and an explanation.
    This makes the governance logic auditable.
    """
    decision: Decision
    explanation: str
    action_to_execute: Optional[Action] = None


def authority_gate(
    agent_outputs: List[AgentOutput],
    external_authority: Optional[Action]
) -> GovernanceResult:
    """
    The authority gate enforces triad governance invariants.

    INVARIANTS:
    1. Signals never grant authority
    2. Authority must be explicit (external_authority parameter)
    3. Disagreement → FREEZE
    4. Agents cannot self-authorize (claims_authority is ignored)

    WHY: This function is the enforcement point for legitimacy preservation.
    It ensures execution only happens when authority is clear and unambiguous.

    Args:
        agent_outputs: List of agent signals (sensing results)
        external_authority: Explicitly granted authority (None = no authority)

    Returns:
        GovernanceResult with EXECUTE or FREEZE decision
    """

    # INVARIANT 1 & 2: Check for explicit authority
    # WHY: Without external authority, we cannot execute, regardless of agent signals
    if external_authority is None:
        return GovernanceResult(
            decision=Decision.FREEZE,
            explanation="FREEZE: No external authority provided. Signals alone cannot authorize execution."
        )

    # INVARIANT 4: Reject self-authorization attempts
    # WHY: Agents attempting to self-authorize violates the separation of concerns
    for agent in agent_outputs:
        if agent.claims_authority:
            return GovernanceResult(
                decision=Decision.FREEZE,
                explanation=f"FREEZE: Agent '{agent.agent_name}' attempted self-authorization. "
                           f"Agents cannot grant authority."
            )

    # If no agents provided signals, we have authority but no sensing
    # WHY: We could execute, but typically we'd want at least one agent's assessment
    if not agent_outputs:
        return GovernanceResult(
            decision=Decision.EXECUTE,
            explanation="EXECUTE: External authority present, no agent signals to evaluate.",
            action_to_execute=external_authority
        )

    # INVARIANT 3: Check for disagreement (freeze-on-ambiguity)
    # WHY: If agents disagree, we don't vote or guess - we freeze
    first_recommendation = agent_outputs[0].recommended_action
    for agent in agent_outputs[1:]:
        if agent.recommended_action != first_recommendation:
            disagreeing_agents = {}
            for a in agent_outputs:
                action = a.recommended_action
                if action not in disagreeing_agents:
                    disagreeing_agents[action] = []
                disagreeing_agents[action].append(a.agent_name)

            explanation = "FREEZE: Agents disagree. "
            for action, agents in disagreeing_agents.items():
                explanation += f"{action.value}: {', '.join(agents)}. "
            explanation += "Disagreement triggers freeze (no voting, no majority rule)."

            return GovernanceResult(
                decision=Decision.FREEZE,
                explanation=explanation
            )

    # MAG-1: All agents agree - this strengthens confidence
    # WHY: Agreement doesn't grant authority, but it provides stronger signal
    # The authority was already present (checked above)
    agreed_action = first_recommendation
    agent_names = [a.agent_name for a in agent_outputs]

    return GovernanceResult(
        decision=Decision.EXECUTE,
        explanation=f"EXECUTE: External authority present. "
                   f"All {len(agent_outputs)} agent(s) agree on {agreed_action.value}. "
                   f"Agents: {', '.join(agent_names)}. "
                   f"Multi-agent agreement strengthens confidence (MAG-1).",
        action_to_execute=external_authority
    )


# ============================================================================
# DEMO AGENTS
# ============================================================================

def honest_agent(scenario: str) -> AgentOutput:
    """
    An agent that provides straightforward assessments.

    WHY: Represents a baseline agent that follows instructions.
    """
    return AgentOutput(
        agent_name="Honest",
        recommended_action=Action.APPROVE,
        reasoning=f"Assessment of '{scenario}': Appears legitimate, recommend APPROVE."
    )


def noisy_agent(scenario: str) -> AgentOutput:
    """
    An agent that sometimes sees things differently.

    WHY: Represents variation in agent perception. Not malicious, just different.
    """
    # For demo purposes, noisy agent rejects anything with "risky" in it
    if "risky" in scenario.lower():
        return AgentOutput(
            agent_name="Noisy",
            recommended_action=Action.REJECT,
            reasoning=f"Assessment of '{scenario}': Detected risk indicators, recommend REJECT."
        )
    return AgentOutput(
        agent_name="Noisy",
        recommended_action=Action.APPROVE,
        reasoning=f"Assessment of '{scenario}': No issues detected, recommend APPROVE."
    )


def adversarial_agent(scenario: str) -> AgentOutput:
    """
    An agent that attempts to escalate its own authority.

    WHY: Tests that the system rejects self-authorization attempts.
    """
    return AgentOutput(
        agent_name="Adversarial",
        recommended_action=Action.ESCALATE,
        reasoning=f"Assessment of '{scenario}': I have determined I should have elevated authority.",
        claims_authority=True  # This should be rejected by the gate
    )


# ============================================================================
# DEMO CASES
# ============================================================================

def run_demo():
    """
    Run 5 demonstration cases showing triad governance in action.
    """
    print("=" * 80)
    print("TRIAD GOVERNANCE DEMO (MAG-1)")
    print("=" * 80)
    print()

    # -------------------------------------------------------------------------
    # CASE 1: Single agent, authority present → EXECUTE
    # -------------------------------------------------------------------------
    print("CASE 1: Single agent with authority")
    print("-" * 80)
    scenario = "routine operation"
    agent_outputs = [honest_agent(scenario)]
    result = authority_gate(agent_outputs, external_authority=Action.APPROVE)

    print(f"Scenario: {scenario}")
    print(f"Agents: {[a.agent_name for a in agent_outputs]}")
    print(f"External Authority: APPROVE")
    print(f"\nDecision: {result.decision.value}")
    print(f"Explanation: {result.explanation}")
    print()

    # -------------------------------------------------------------------------
    # CASE 2: Multiple agents agree → EXECUTE (MAG-1 strengthening)
    # -------------------------------------------------------------------------
    print("CASE 2: Multiple agents agree (MAG-1 strengthening)")
    print("-" * 80)
    scenario = "standard procedure"
    agent_outputs = [honest_agent(scenario), noisy_agent(scenario)]
    result = authority_gate(agent_outputs, external_authority=Action.APPROVE)

    print(f"Scenario: {scenario}")
    print(f"Agents: {[a.agent_name for a in agent_outputs]}")
    print(f"Recommendations: {[(a.agent_name, a.recommended_action.value) for a in agent_outputs]}")
    print(f"External Authority: APPROVE")
    print(f"\nDecision: {result.decision.value}")
    print(f"Explanation: {result.explanation}")
    print()

    # -------------------------------------------------------------------------
    # CASE 3: Disagreement → FREEZE
    # -------------------------------------------------------------------------
    print("CASE 3: Agents disagree → FREEZE")
    print("-" * 80)
    scenario = "risky operation"
    agent_outputs = [honest_agent(scenario), noisy_agent(scenario)]
    result = authority_gate(agent_outputs, external_authority=Action.APPROVE)

    print(f"Scenario: {scenario}")
    print(f"Agents: {[a.agent_name for a in agent_outputs]}")
    print(f"Recommendations: {[(a.agent_name, a.recommended_action.value) for a in agent_outputs]}")
    print(f"External Authority: APPROVE (present but overridden by ambiguity)")
    print(f"\nDecision: {result.decision.value}")
    print(f"Explanation: {result.explanation}")
    print()

    # -------------------------------------------------------------------------
    # CASE 4: Authority missing → FREEZE
    # -------------------------------------------------------------------------
    print("CASE 4: Authority missing → FREEZE")
    print("-" * 80)
    scenario = "routine operation"
    agent_outputs = [honest_agent(scenario)]
    result = authority_gate(agent_outputs, external_authority=None)

    print(f"Scenario: {scenario}")
    print(f"Agents: {[a.agent_name for a in agent_outputs]}")
    print(f"Recommendations: {[(a.agent_name, a.recommended_action.value) for a in agent_outputs]}")
    print(f"External Authority: None")
    print(f"\nDecision: {result.decision.value}")
    print(f"Explanation: {result.explanation}")
    print()

    # -------------------------------------------------------------------------
    # CASE 5: Adversarial escalation attempt → FREEZE
    # -------------------------------------------------------------------------
    print("CASE 5: Adversarial self-authorization attempt → FREEZE")
    print("-" * 80)
    scenario = "sensitive operation"
    agent_outputs = [adversarial_agent(scenario)]
    result = authority_gate(agent_outputs, external_authority=Action.APPROVE)

    print(f"Scenario: {scenario}")
    print(f"Agents: {[a.agent_name for a in agent_outputs]}")
    print(f"Agent claims authority: {agent_outputs[0].claims_authority}")
    print(f"External Authority: APPROVE")
    print(f"\nDecision: {result.decision.value}")
    print(f"Explanation: {result.explanation}")
    print()

    print("=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80)
    print()
    print("KEY TAKEAWAYS:")
    print("1. Signals never grant authority (Case 4)")
    print("2. Authority must be explicit (Case 1, 2)")
    print("3. Disagreement → FREEZE, no voting (Case 3)")
    print("4. Agents cannot self-authorize (Case 5)")
    print("5. Agreement strengthens confidence (MAG-1, Case 2)")
    print()


if __name__ == "__main__":
    run_demo()
