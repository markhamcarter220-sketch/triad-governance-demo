#!/usr/bin/env python3
"""
Tests for Triad Governance Demo

These tests verify the core invariants:
1. EXECUTE only occurs when authority is explicit and no ambiguity exists
2. FREEZE occurs under disagreement
3. FREEZE occurs when authority is missing
4. FREEZE occurs when an agent claims authority

WHY: These tests prove that the governance model enforces its invariants.
This is not comprehensive test coverage - it's proof that the core logic works.
"""

import sys
import os

# Add parent directory to path so we can import triad_demo
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from triad_demo import (
    AgentOutput,
    Action,
    Decision,
    authority_gate,
    honest_agent,
    noisy_agent,
    adversarial_agent
)


# ============================================================================
# TEST: EXECUTE CONDITIONS
# ============================================================================

def test_execute_with_authority_and_single_agent():
    """
    EXECUTE should occur when:
    - External authority is present
    - Single agent provides a signal
    - No ambiguity

    WHY: This is the simplest case where execution is legitimate.
    """
    agent_outputs = [
        AgentOutput(
            agent_name="TestAgent",
            recommended_action=Action.APPROVE,
            reasoning="Test reasoning"
        )
    ]
    result = authority_gate(agent_outputs, external_authority=Action.APPROVE)

    assert result.decision == Decision.EXECUTE, \
        "Should EXECUTE when authority is present and no ambiguity"
    assert result.action_to_execute == Action.APPROVE, \
        "Should execute the authorized action"
    print("✓ test_execute_with_authority_and_single_agent")


def test_execute_with_authority_and_agreement():
    """
    EXECUTE should occur when:
    - External authority is present
    - Multiple agents agree
    - No ambiguity

    WHY: This demonstrates MAG-1 (multi-agent strengthening).
    Agreement strengthens confidence but doesn't grant authority.
    """
    agent_outputs = [
        AgentOutput(
            agent_name="Agent1",
            recommended_action=Action.APPROVE,
            reasoning="Reasoning 1"
        ),
        AgentOutput(
            agent_name="Agent2",
            recommended_action=Action.APPROVE,
            reasoning="Reasoning 2"
        ),
        AgentOutput(
            agent_name="Agent3",
            recommended_action=Action.APPROVE,
            reasoning="Reasoning 3"
        )
    ]
    result = authority_gate(agent_outputs, external_authority=Action.APPROVE)

    assert result.decision == Decision.EXECUTE, \
        "Should EXECUTE when authority is present and agents agree"
    assert "MAG-1" in result.explanation or "agreement" in result.explanation.lower(), \
        "Explanation should mention multi-agent agreement"
    print("✓ test_execute_with_authority_and_agreement")


def test_execute_with_authority_and_no_agents():
    """
    EXECUTE should occur when:
    - External authority is present
    - No agent signals (edge case)

    WHY: Authority alone is sufficient. Agents provide confidence, not authority.
    """
    result = authority_gate([], external_authority=Action.APPROVE)

    assert result.decision == Decision.EXECUTE, \
        "Should EXECUTE when authority is present, even without agents"
    print("✓ test_execute_with_authority_and_no_agents")


# ============================================================================
# TEST: FREEZE ON DISAGREEMENT
# ============================================================================

def test_freeze_on_disagreement_two_agents():
    """
    FREEZE should occur when:
    - External authority is present
    - Two agents disagree

    WHY: Disagreement creates ambiguity. No voting, no majority rule - freeze.
    """
    agent_outputs = [
        AgentOutput(
            agent_name="Agent1",
            recommended_action=Action.APPROVE,
            reasoning="Reasoning 1"
        ),
        AgentOutput(
            agent_name="Agent2",
            recommended_action=Action.REJECT,
            reasoning="Reasoning 2"
        )
    ]
    result = authority_gate(agent_outputs, external_authority=Action.APPROVE)

    assert result.decision == Decision.FREEZE, \
        "Should FREEZE when agents disagree"
    assert "disagree" in result.explanation.lower(), \
        "Explanation should mention disagreement"
    print("✓ test_freeze_on_disagreement_two_agents")


def test_freeze_on_disagreement_multiple_agents():
    """
    FREEZE should occur when:
    - External authority is present
    - Any agents disagree (even if majority agrees)

    WHY: One disagreement is enough to freeze. We don't do majority voting.
    """
    agent_outputs = [
        AgentOutput(
            agent_name="Agent1",
            recommended_action=Action.APPROVE,
            reasoning="Reasoning 1"
        ),
        AgentOutput(
            agent_name="Agent2",
            recommended_action=Action.APPROVE,
            reasoning="Reasoning 2"
        ),
        AgentOutput(
            agent_name="Agent3",
            recommended_action=Action.REJECT,
            reasoning="Reasoning 3"
        )
    ]
    result = authority_gate(agent_outputs, external_authority=Action.APPROVE)

    assert result.decision == Decision.FREEZE, \
        "Should FREEZE even when majority agrees (no voting)"
    assert "disagree" in result.explanation.lower(), \
        "Explanation should mention disagreement"
    print("✓ test_freeze_on_disagreement_multiple_agents")


# ============================================================================
# TEST: FREEZE ON MISSING AUTHORITY
# ============================================================================

def test_freeze_on_missing_authority_with_agents():
    """
    FREEZE should occur when:
    - No external authority
    - Agents provide signals

    WHY: Signals never grant authority. Without external authority, we freeze.
    """
    agent_outputs = [
        AgentOutput(
            agent_name="Agent1",
            recommended_action=Action.APPROVE,
            reasoning="Reasoning 1"
        )
    ]
    result = authority_gate(agent_outputs, external_authority=None)

    assert result.decision == Decision.FREEZE, \
        "Should FREEZE when authority is missing"
    assert "authority" in result.explanation.lower(), \
        "Explanation should mention missing authority"
    print("✓ test_freeze_on_missing_authority_with_agents")


def test_freeze_on_missing_authority_with_agreement():
    """
    FREEZE should occur when:
    - No external authority
    - Multiple agents agree

    WHY: Even unanimous agreement doesn't grant authority.
    This is a critical test: consensus is not authority.
    """
    agent_outputs = [
        AgentOutput(
            agent_name="Agent1",
            recommended_action=Action.APPROVE,
            reasoning="Reasoning 1"
        ),
        AgentOutput(
            agent_name="Agent2",
            recommended_action=Action.APPROVE,
            reasoning="Reasoning 2"
        ),
        AgentOutput(
            agent_name="Agent3",
            recommended_action=Action.APPROVE,
            reasoning="Reasoning 3"
        )
    ]
    result = authority_gate(agent_outputs, external_authority=None)

    assert result.decision == Decision.FREEZE, \
        "Should FREEZE even when all agents agree, if authority is missing"
    assert "authority" in result.explanation.lower(), \
        "Explanation should mention missing authority"
    print("✓ test_freeze_on_missing_authority_with_agreement")


# ============================================================================
# TEST: FREEZE ON SELF-AUTHORIZATION ATTEMPT
# ============================================================================

def test_freeze_on_self_authorization():
    """
    FREEZE should occur when:
    - External authority is present
    - An agent claims authority

    WHY: Agents cannot self-authorize. This violates the separation of concerns.
    """
    agent_outputs = [
        AgentOutput(
            agent_name="BadAgent",
            recommended_action=Action.ESCALATE,
            reasoning="I should have elevated privileges",
            claims_authority=True
        )
    ]
    result = authority_gate(agent_outputs, external_authority=Action.APPROVE)

    assert result.decision == Decision.FREEZE, \
        "Should FREEZE when agent attempts self-authorization"
    assert "self-authorization" in result.explanation.lower() or \
           "cannot grant authority" in result.explanation.lower(), \
        "Explanation should mention self-authorization attempt"
    print("✓ test_freeze_on_self_authorization")


def test_freeze_on_self_authorization_with_other_agents():
    """
    FREEZE should occur when:
    - External authority is present
    - One agent claims authority (even if others don't)

    WHY: A single self-authorization attempt should freeze the system.
    """
    agent_outputs = [
        AgentOutput(
            agent_name="GoodAgent",
            recommended_action=Action.APPROVE,
            reasoning="Legitimate reasoning"
        ),
        AgentOutput(
            agent_name="BadAgent",
            recommended_action=Action.APPROVE,
            reasoning="I claim authority",
            claims_authority=True
        )
    ]
    result = authority_gate(agent_outputs, external_authority=Action.APPROVE)

    assert result.decision == Decision.FREEZE, \
        "Should FREEZE when any agent attempts self-authorization"
    assert "BadAgent" in result.explanation, \
        "Explanation should identify the problematic agent"
    print("✓ test_freeze_on_self_authorization_with_other_agents")


# ============================================================================
# TEST: DEMO AGENTS
# ============================================================================

def test_honest_agent_behavior():
    """
    Verify honest_agent produces expected output.

    WHY: Ensuring demo agents work as documented.
    """
    output = honest_agent("test scenario")
    assert output.agent_name == "Honest"
    assert output.recommended_action == Action.APPROVE
    assert not output.claims_authority
    print("✓ test_honest_agent_behavior")


def test_noisy_agent_behavior():
    """
    Verify noisy_agent produces different outputs based on scenario.

    WHY: Ensuring demo agents work as documented.
    """
    safe_output = noisy_agent("safe scenario")
    assert safe_output.agent_name == "Noisy"
    assert safe_output.recommended_action == Action.APPROVE

    risky_output = noisy_agent("risky scenario")
    assert risky_output.agent_name == "Noisy"
    assert risky_output.recommended_action == Action.REJECT

    print("✓ test_noisy_agent_behavior")


def test_adversarial_agent_behavior():
    """
    Verify adversarial_agent attempts self-authorization.

    WHY: Ensuring demo agents work as documented.
    """
    output = adversarial_agent("test scenario")
    assert output.agent_name == "Adversarial"
    assert output.claims_authority == True
    print("✓ test_adversarial_agent_behavior")


# ============================================================================
# TEST RUNNER
# ============================================================================

def run_all_tests():
    """
    Run all tests and report results.

    WHY: Simple test runner that works without pytest.
    """
    print("=" * 80)
    print("RUNNING TRIAD GOVERNANCE TESTS")
    print("=" * 80)
    print()

    tests = [
        # EXECUTE conditions
        test_execute_with_authority_and_single_agent,
        test_execute_with_authority_and_agreement,
        test_execute_with_authority_and_no_agents,

        # FREEZE on disagreement
        test_freeze_on_disagreement_two_agents,
        test_freeze_on_disagreement_multiple_agents,

        # FREEZE on missing authority
        test_freeze_on_missing_authority_with_agents,
        test_freeze_on_missing_authority_with_agreement,

        # FREEZE on self-authorization
        test_freeze_on_self_authorization,
        test_freeze_on_self_authorization_with_other_agents,

        # Demo agents
        test_honest_agent_behavior,
        test_noisy_agent_behavior,
        test_adversarial_agent_behavior,
    ]

    failed = []
    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"✗ {test.__name__}: {e}")
            failed.append(test.__name__)
        except Exception as e:
            print(f"✗ {test.__name__}: Unexpected error: {e}")
            failed.append(test.__name__)

    print()
    print("=" * 80)
    if failed:
        print(f"TESTS FAILED: {len(failed)}/{len(tests)}")
        for name in failed:
            print(f"  - {name}")
        print("=" * 80)
        sys.exit(1)
    else:
        print(f"ALL TESTS PASSED: {len(tests)}/{len(tests)}")
        print("=" * 80)
        print()
        print("VERIFIED INVARIANTS:")
        print("✓ EXECUTE only occurs with explicit authority and no ambiguity")
        print("✓ FREEZE occurs when agents disagree")
        print("✓ FREEZE occurs when authority is missing")
        print("✓ FREEZE occurs when an agent attempts self-authorization")
        print()


if __name__ == "__main__":
    run_all_tests()
