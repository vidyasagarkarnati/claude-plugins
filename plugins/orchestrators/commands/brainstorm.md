---
description: "Brainstorming session: CTO sets direction, PM explores product angle, AI/ML Architect evaluates technical possibilities"
argument-hint: "<topic-or-problem-statement>"
---

# Brainstorm

Multi-perspective brainstorming session on a topic, problem, or opportunity. Chains CTO → Product Manager → AI/ML Architect for strategic, product, and technical dimensions.

## Chain

```
use_agent: cto
```
**Input**: `$ARGUMENTS` (topic or problem)
**Task**: Strategic framing and direction-setting:
- What is the strategic opportunity or threat?
- What technology trends are relevant?
- What are the build vs buy vs partner options?
- What are the key constraints (time, cost, risk)?
- Propose 2–3 strategic directions to explore
**Handoff artifact**: Strategic brief with 2–3 directions + constraints

---

```
use_agent: product-manager
```
**Input**: CTO strategic brief
**Task**: Product angle and user value exploration:
- Who are the users affected?
- What is the pain point or opportunity from the user's perspective?
- For each strategic direction: what does the user experience look like?
- What are the measurable success outcomes?
- Which direction has the strongest product-market fit?
**Handoff artifact**: Product perspective per direction + recommended direction + why

---

```
use_agent: ai-ml-architect
```
**Input**: CTO brief + PM product perspective
**Task**: Technical possibilities and AI/ML opportunities:
- Is there an AI/ML component that could enhance any direction?
- What data would be needed? Is it available?
- What are the build complexity and risk trade-offs?
- Recommend the most technically feasible direction
**Output**: Final brainstorm synthesis with recommended direction, key open questions, and next steps

## Output
A structured brainstorm report covering:
1. **Strategic context** (CTO view)
2. **Product opportunities** per direction (PM view)
3. **Technical feasibility** per direction (AI/ML view)
4. **Recommended direction** with rationale
5. **Next steps**: who needs to do what to move forward

## Usage
```
/orchestrators:brainstorm "how should we approach AI-powered customer support?"
```
