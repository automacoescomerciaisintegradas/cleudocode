---
name: ralph-wiggum
description: autonomous, iterative development loops. named after the simpsons character because of his "stubborn persistence". use this for complex tasks that require multiple steps and verification.
metadata:
  cleudocode:
    emoji: "🖍️"
    category: "productivity"
---

# Ralph Wiggum: Iterative Autonomous Loop

This skill enables Claude to work on a task repeatedly until a specific success criteria is met. It is based on the idea of a "Loop Hook" that prevents exiting the session until the job is truly done.

## Core Philosophy
- **Stubborn Persistence**: Do not give up on a task if it fails initially.
- **Failures are Data**: Every error message or failed test is a hint for the next iteration.
- **Goal-Oriented**: Focus purely on the defined completion criteria.

## Usage Guidelines
1. **Define a "Completion Promise"**: A specific state or output that signals success (e.g., "All tests passing and coverage > 80%").
2. **Iterate Locally**: Use git history and previous logs to refine the approach in each loop.
3. **Self-Correction**: If a modification breaks the system, revert and try a different path.

## Operational Commands (Simulated)
- `/ralph-loop [prompt]`: Starts the iterative process.
- `/cancel-ralph`: Terminates the current loop.

When this skill is active, you are in "Ralph Mode". You must continue working on the task until you are certain the completion criteria is met, or the maximum iteration limit is reached.
