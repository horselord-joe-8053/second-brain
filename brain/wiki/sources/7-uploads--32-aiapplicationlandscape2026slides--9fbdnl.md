---
type: source
title: "Source: uploads/AI_Application_Landscape_2026_Slides.pptx"
created: 2026-10-03
updated: 2026-10-03
sources: ["uploads/AI_Application_Landscape_2026_Slides.pptx"]
tags: []
related: []
---

# Source: uploads/AI_Application_Landscape_2026_Slides.pptx

## Key Entities

*   **Hermes (Agent)**: Personal agent/harness. Page-worthy: yes (central example of persistent agent).
*   **OpenClaw**: Personal agent/harness. Page-worthy: yes (example of local/self-hosted agent layer).
*   **Cursor**: Software-engineering agent. Page-worthy: yes (industry standard for repo-centered agents).
*   **Claude Code**: Software-engineering agent. Page-worthy: yes (representative of repo-centered agents).
*   **Codex**: Software-engineering agent. Page-worthy: yes (representative of repo-centered agents).
*   **Antigravity**: Software-engineering agent. Page-worthy: no (passing mention).
*   **Meta Muse**: Consumer personal agent. Page-worthy: no (passing mention).
*   **Grok Bot**: Persistent cloud-computer teammate. Page-worthy: no (passing mention).
*   **OpenAI Computer Use**: Capability primitive. Page-worthy: yes (key technical primitive for GUI interaction).
*   **LangChain**: Framework/Source. Page-worthy: yes (cited for harness/loop research).
*   **Anthropic**: Organization. Page-worthy: yes (cited for multi-agent and skill research).
*   **Google Research**: Organization. Page-worthy: yes (cited for agent scaling research).

## Key Concepts

*   **Harness Engineering**: The design of the execution environment (context, memory, tools, oversight) that turns raw model intelligence into reliable work. Central to the source's thesis.
*   **Loop Engineering**: The design of repeated action/feedback cycles (Agent, Verification, Event-driven, Improvement) to ensure agents recover and continue.
*   **AI Skills**: Procedural knowledge (scripts, templates, rules) that defines *how* an agent performs a job, distinct from factual RAG.
*   **Jev (Decision Model)**: A lightweight, fast model used for routing, classification, and verification to separate "thinking" from "deciding."
*   **Post-training Scaling**: Using agent trajectories (reasoning + tool use + recovery) to update model weights, distinct from inference-time scaling.
*   **Inference-time Scaling**: Spending runtime compute (sampling/evaluating candidates) to improve output quality without changing weights.

## Main Arguments & Findings

*   **The Multiplier Effect**: AI system utility is a product of `Model Capability × Harness Quality × Context Quality × Tools × Verification`. Proprietary advantage is shifting from model weights to the harness, internal skills, and evaluation datasets.
*   **Architecture over Model**: For many tasks, harness and loop improvements yield higher performance gains than switching foundation models.
*   **Multi-Agent Patterns**: Multi-agent systems should be chosen based on task decomposability. Centralized coordination is highly effective for decomposable tasks (+80.8%), while sequential planning often suffers from error propagation.
*   **Procedural vs. Factual Knowledge**: Traditional RAG provides facts; AI Skills provide procedures. Skills should be versioned and loaded progressively to maintain context efficiency.
*   **Distributed Systems Reframe**: Modern AI applications are essentially distributed systems with a probabilistic worker. Infrastructure concerns (idempotency, retries, observability, permissions) are now core AI engineering requirements.

## Connections to Existing Wiki

*   **Extends**: [[concepts/smoke-test]] (the source emphasizes verification and observability, which are critical for smoke testing agentic workflows).
*   **Extends**: [[entities/second-brain]] (the source's focus on "Personal Computer Agents" and "Persistent Memory" aligns with the Second Brain concept).

## Contradictions & Tensions

*   **Model vs. Harness**: The source argues that harness quality is the primary differentiator, which may conflict with views that prioritize raw model scaling.
*   **Multi-Agent Complexity**: The source warns that multi-agent systems can amplify errors (4.4x to 17.2x) if not properly governed, creating a tension between the desire for agent autonomy and the need for centralized verification.

## Recommendations

*   **Create Page**: `concepts/harness-engineering` (define the six concerns: runtime, skills, tools, plugins, events, surfaces).
*   **Create Page**: `concepts/loop-engineering` (document the four loop types: Agent, Verification, Event-driven, Improvement).
*   **Create Page**: `concepts/ai-skills` (define as procedural RAG vs. factual RAG).
*   **Update Page**: [[entities/second-brain]] to include the role of "Personal Computer Agents" as persistent workers.
*   **Open Question**: How do we implement "Improvement Loops" (Section 3) within the current `nashsu-source-watch` workflow to automatically refine our own knowledge base?

<!-- llm-wiki:embedded-images -->
## Embedded Images

### Page 3

![The image appears to be a flowchart illustrating the relationship between various components of AI skills and applications. It includes the following key elements:  1. **Business application** (coding, research, operations, personal agent) is connected to **AI Skills** (reusable procedural knowledge). 2. **Agent Harness** (tools, memory, context, filesystem, permissions) is linked to **AI Skills**. 3. **Loop Engineering** (act, observe, evaluate, correct) leads to a **Decision Layer** (Jev, classifiers, judges, reward models). 4. At the bottom, **Foundation Models** (GPT, Claude, Gemini, Grok, open models) are connected to **Post-Training** (sampling, rollouts, evaluation, optimization), with an indication that this process "improves" the models.  The diagram uses colored boxes and arrows to represent these relationships.](../media/7-uploads--32-aiapplicationlandscape2026slides--9fbdnl/img-1.png)

### Page 6

![The image is a flowchart illustrating a system architecture. At the top, it features a box labeled "Foundation model or model router." Below it, a central box titled "Agent harness" contains several bullet points: "planning and loop control," "context and memory," "permissions and sandboxing," and "tool routing and subagents." Branching from the "Agent harness" are three boxes: "Skills" (with "SKILL.md"), "Tools" (listing "command-line interface (CLI)," "Model Context Protocol (MCP)," and "APIs"), and "Events" (noting "cron" and "webhooks"). Further down, the "Skills" box connects to "Workflow knowledge," while the "Tools" box leads to "Filesystem • browser," "shell • external services," and the "Events" box connects to "Channels and triggers" (including "Slack • GitHub • other systems").](../media/7-uploads--32-aiapplicationlandscape2026slides--9fbdnl/img-3.png)

### Page 7

![The image is a flowchart titled "Agent harness." It features a central blue box labeled "Agent harness," with several branches leading to other colored boxes. The branches connect to the following elements: "Core runtime" (orange), which includes "Models • agent loop and orchestration context manager • memory permissions and sandbox"; "Skills" (purple), which references "SKILL.md procedural workflow knowledge"; "Tools" (green), detailing "Native tools • command-line interface MCP • APIs"; "Plugins" (purple), indicating "Skills • tools or MCP servers lifecycle hooks"; "Events" (orange), which mentions "Cron schedules • webhooks external events"; and "Surfaces" (blue), describing "integrated development environment (IDE) CLI • web • Slack • Telegram • mobile."](../media/7-uploads--32-aiapplicationlandscape2026slides--9fbdnl/img-8.png)

### Page 10

![The image is a flowchart illustrating a process related to AI applications. It includes the following key components: "System prompt / goal" (blue box), "Context + memory" (purple box), "Model" (orange box), "Observation" (green box), "Verification" (red box), "Tool selection" (orange box), "Tool execution" (green box), and "Filesystem / browser / terminal / APIs" (blue box). Arrows indicate the flow of the process, connecting these elements in a structured manner.](../media/7-uploads--32-aiapplicationlandscape2026slides--9fbdnl/img-12.png)

### Page 13

![The image is a flowchart illustrating a process involving an "Agent" performing work. The steps include: "Collect traces," "Identify failures / weak trajectories," and "Human or AI analyzes failures." The final step suggests to "Improve prompts, skills, tools, policies or loop." The flowchart uses colored boxes and arrows to indicate the sequence and relationships between these steps.](../media/7-uploads--32-aiapplicationlandscape2026slides--9fbdnl/img-5.png)

### Page 15

![The image is a flowchart illustrating a process related to achieving a goal with shared constraints. It begins with "Goal + shared constraints" at the top, leading to "Manager plans and decomposes." From there, three branches lead to "Specialist A," "Specialist B," and "Specialist C," which converge at "Typed result + evidence." The flow continues to "Manager synthesizes," then diverges to "Independent verification," and concludes with "accepted" leading to "Final result." The phrase "gaps found" is noted in a side box.](../media/7-uploads--32-aiapplicationlandscape2026slides--9fbdnl/img-9.png)

### Page 16

![The image titled "Huawei MaaS Backend Observations" outlines three observations related to backend issues. Observation #1 notes a "High Error Rate" with 207 x 4XX errors, attributed to "DeepSeek-V4-Pro RPM Limitation," and suggests actions to understand production concurrency and recalculate RPM/TPM quota. Observation #2 highlights "Image Upload Errors" with 14 x 4XX errors, linked to the "GLM5.1 currently text-only endpoint used," recommending MCP integration and image pre-processing API. Observation #3 discusses "Cline Experience" issues, mentioning checkpoint failures and context losses, with a root cause of "Tool chain limitation" and a recommendation to use VS Code with GitHub Copilot or similar tools.](../media/7-uploads--32-aiapplicationlandscape2026slides--9fbdnl/img-10.png)

### Page 22

![The image is a flowchart depicting a decision-making process. It includes the following elements: a blue box labeled "Current state," an orange box labeled "Jev / decision model," a purple box labeled "Large reasoning model," and green boxes labeled "Action" and "Observation." There are arrows indicating the flow between these elements, with a pathway leading from "Current state" to "Jev / decision model," then branching to "uncertain / complex" and "confident," which both connect to "Large reasoning model." The flow continues from "Large reasoning model" to "Action" and "Observation."](../media/7-uploads--32-aiapplicationlandscape2026slides--9fbdnl/img-4.png)

### Page 23

![The image is a flowchart depicting a system involving a "User / employee" at the top, leading to a "Personal agent" in the center. Below the "Personal agent," there are three branches labeled "Memory," "Skills," and "Goals / tasks." At the bottom, a box labeled "Persistent computer / workspace" connects to four options: "Browser," "Terminal," "Desktop / apps," and "APIs / SaaS." The flowchart uses various colors for different sections, with arrows indicating the relationships between the elements.](../media/7-uploads--32-aiapplicationlandscape2026slides--9fbdnl/img-7.png)

### Page 29

![The image is a flowchart illustrating a process related to model optimization. It begins with a "Base / current model" at the top, leading to a box labeled "Sample many trajectories." From this box, three branches lead to "Candidate A," "Candidate B," and "Candidate C ... N," which are all in purple boxes. The flow continues to an orange box labeled "Evaluate / reward," which then connects to a green box titled "Identify useful behavior." Finally, the process concludes with a red box labeled "Optimize model." Arrows indicate the flow of the process throughout the diagram.](../media/7-uploads--32-aiapplicationlandscape2026slides--9fbdnl/img-2.png)

### Page 31

![The image is a flowchart illustrating a process related to AI application development. It includes several labeled boxes connected by arrows, indicating the flow of actions and decisions. Key components include "Foundation Model," "Agent Harness," "Agent Loop," "Decide next action," "Act," "Observe," "Verify," and "Post-training / evaluation." Notable text within the flowchart includes "complex reasoning," "fast structured decision," "successful traces," and "continue / retry" which are positioned near relevant boxes to indicate their relationships within the process.](../media/7-uploads--32-aiapplicationlandscape2026slides--9fbdnl/img-6.png)

### Page 36

![The image is a flowchart titled "Agent Harness," depicting various components and their relationships within an AI application framework. At the top, it shows "React / conversational UI" leading to "Agent API," which connects to the central "Agent Harness" box. From the "Agent Harness," several branches extend to components labeled "Context + memory," "Skills," "Policy + permissions," "Model router," "Tool registry / MCP," "Sandbox + filesystem," and "Subagents." Further down, the "Agent Loop" connects to "Tracing / evaluation," "Decision / judge model," and "Verifier." The flowchart includes specific tools like "Amazon Web Services," "PostgreSQL," and "SaaS APIs" under the "Tools" section.](../media/7-uploads--32-aiapplicationlandscape2026slides--9fbdnl/img-11.png)
<!-- llm-wiki:embedded-images -->
