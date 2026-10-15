---
title: Agent Harness Architecture Comparison and Evolution
date: 2026-10-06
type: technical-study
description: A comparative analysis of agent harness architectures, focusing on paradigms, design patterns, and the shift from linear pipelines to loop-driven autonomous systems.
---

## Agent Harness Evolution: Anatomy and Patterns

Agent harnesses have evolved from simple task executors into specialized infrastructure layers that provide the execution substrate for autonomous reasoning.

### 1. Architectural Paradigms
Current production harnesses follow three recurring design paradigms:

*   **Plugin-First (Kernel-Centric):** e.g., DeepSeek Harness. Prioritizes modularity; models, tools, and sandboxes are swappable plugins. Focuses on preventing architectural lock-in.
*   **Mechanism-First (Fixed-Primitive):** e.g., Claude Code, Deep Agents. Centers on four fixed pillars: **Planning** (step-by-step logic), **Virtual Filesystem** (isolated repository access), **Subagent Delegation**, and **Context Compression**.
*   **Skill-First (Compounding):** e.g., Hermes Agent. Focuses on persistent, across-session growth. Solutions for non-trivial tasks are compiled into a versioned `SKILL.md` library, allowing the agent to perform recurring tasks with increasing efficiency.

### 2. Harness Engineering vs. Loop Engineering
*   **Harness Engineering (Inner Loop):** Manages the execution environment: context, memory, tool routing, and permissions. It provides the "工地" (workplace) for the model.
*   **Loop Engineering (Outer Loop):** Composes the inner cycle into self-sustaining workflows via triggers, topological planning, verifiers, and exit criteria (e.g., failure detection, retry logic, automated trajectory improvement).

### 3. Structural Trends
*   **Persistence & State:** Modern harnesses (e.g., OpenHands, Hermes) treat execution as an **Event-Sourced Engine**. System state is a projection of an `EventLog`, enabling first-class history navigation, branching, and replay.
*   **Interoperability:** The **Model Context Protocol (MCP)** has become the dominant standard for tool discovery and extension, enabling third-party developer growth.
*   **Improvement Loops:** The most advanced systems are implementing autonomous "Improvement Loops" where agents analyze their own failure traces (weak trajectories) and automatically update prompts, tools, or policy settings without human intervention.

### 4. Selection Criteria
*   **Reliability:** Use Claude Code/Deep Agents if task decomposability and sandbox safety are the primary requirements.
*   **Vendor Lock-in:** Use modular systems like DeepSeek Harness if switching LLM providers or toolkits is frequent.
*   **Compounding Growth:** Use Hermes if the domain features recurring, high-complexity tasks that benefit from a cumulative procedural library.
