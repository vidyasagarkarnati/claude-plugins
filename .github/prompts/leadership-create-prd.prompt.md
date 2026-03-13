---
mode: agent
description: "Create a Product Requirements Document for a new feature or product"
# argument-hint: <feature-name-or-description>
---


# Create PRD

Generate a complete Product Requirements Document (PRD) for a new feature or product. Uses a Product Manager persona to drive structured requirements discovery and documentation.

## Pre-flight Checks
1. Confirm the feature name or description has been provided as `${input:arguments}`
2. Check `docs/` for existing PRDs to avoid duplication
3. Read `.claude/memory/project-state.md` for tech stack and constraints

## Phase 1: Requirements Gathering
- Identify primary and secondary user personas affected by this feature
- If the argument is ambiguous, state your assumptions explicitly at the top
- List constraints: compliance, platform, timeline, budget
- Review any referenced tickets or issues for context

## Phase 2: Problem Statement
- Write a crisp 2–4 sentence problem statement: what is broken, who is affected, what is the current workaround
- Quantify the problem where possible (e.g., "users drop off at step 3 in 40% of sessions")
- State what is explicitly out of scope

## Phase 3: Solution Overview
- Describe the proposed solution at a high level — avoid implementation details
- List 2–3 alternative approaches considered and why they were ruled out
- Highlight key product decisions and the rationale behind them

## Phase 4: User Stories
- Write user stories: `As a <persona>, I want to <action>, so that <outcome>.`
- Cover the happy path, edge cases, and error states
- Group stories by epic or workflow if there are more than five

## Phase 5: Acceptance Criteria
- For each user story, write concrete, testable criteria using Given/When/Then format
- Include accessibility, localization, and performance criteria where relevant
- Flag any criteria requiring sign-off before work begins

## Phase 6: Success Metrics
- Define 3–5 measurable KPIs (adoption rate, error rate, NPS delta, etc.)
- Specify measurement method and data source for each metric
- Set baseline (current state) and target values with timeframe

## Phase 7: Timeline
- Propose phased rollout: MVP → Beta → GA
- List dependencies (other teams, external APIs, design assets) and lead times
- Risk section: what could delay or derail, and mitigations

## Output Format
Save as `docs/prd-${input:arguments}.md` with sections:
1. Executive Summary
2. Problem Statement
3. Solution Overview
4. User Personas
5. User Stories & Acceptance Criteria
6. Success Metrics
7. Timeline & Milestones
8. Risks & Dependencies
9. Open Questions

## Error Handling
- Ambiguous input: state assumptions explicitly under an "Assumptions" callout
- Missing stakeholder context: flag with `[NEEDS INPUT]` inline and continue
- Conflicting requirements: surface in "Open Questions" rather than silently picking one path
