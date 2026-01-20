from core.trace import ExecutionReport
from rules.patch import PatchProposal


RULE_PATCH_PROMPT = """
Given the following execution trace,
suggest a rule patch proposal.
Do NOT modify rules directly.

Execution Report:
- Task ID: {task_id}
- Status: {status}
- Error: {error}
- Failed Rules: {failed_rules}

Suggest patches to fix the failure while maintaining system constraints:
- Use only allowed patch types (ADD_RULE, MODIFY_RULE, ADD_CONDITION, etc.)
- Keep patches minimal and focused
- Avoid rule explosion
"""


REFLECTION_PROMPT = """
Analyze the following execution failure and propose a minimal fix:

Task: {task_id}
Status: {status}
Error: {error_message}

Events:
{events}

Build Traces:
{build_traces}

Propose a rule patch that:
1. Addresses the root cause
2. Is as minimal as possible
3. Does not over-specialize
4. Maintains system consistency
"""


PLANNING_PROMPT = """
Plan actions to achieve the following goal:

Goal: {goal}

Current World State:
{world_state}

Available Actions:
- browser.open(url)
- browser.click(selector)
- browser.fill(selector, value)
- browser.wait_for(selector)
- browser.extract(selector)
- filesystem.write(path, content)
- filesystem.read(path)

Generate a sequence of actions with dependencies.
"""
