---
name: prompt-engineering
description: System prompt structure, chain-of-thought prompting, few-shot examples, context window management, output format control, and RAG prompt design
---

# Prompt Engineering

Mastery of this skill enables you to craft prompts that reliably produce high-quality, consistent outputs from AI models. You can design system prompts, engineer context windows efficiently, and build effective RAG pipelines.

## When to Use This Skill
- Writing or optimizing system prompts for AI agents
- Designing few-shot examples for consistent outputs
- Building RAG prompts that use retrieved context effectively
- Managing long context windows without degradation
- Improving AI output quality for a specific task

## Core Concepts

### 1. Prompt Structure
Every effective prompt has these layers:
1. **Role/Persona**: who the model is
2. **Context**: relevant background information
3. **Task**: what to do
4. **Format**: how to structure the output
5. **Constraints**: what to avoid or limit

### 2. Chain-of-Thought (CoT)
Trigger reasoning before answering: `"Think step by step"` or `"Let's reason through this."` Most effective for multi-step problems, math, and logic. Use `<thinking>` tags for structured scratchpad reasoning.

### 3. Context Window Management
- Claude 3.5: 200K tokens. Place critical instructions at START and END (primacy + recency).
- Long docs: summarize first, then include summaries + key excerpts
- RAG: retrieved chunks at the bottom of user turn, not system prompt

## Quick Reference
```
Tokens ≈ 4 characters ≈ 0.75 words
Claude's 200K context ≈ 150K words ≈ 500 pages

Prompt hierarchy (highest to lowest priority):
1. System prompt
2. User turn (most recent)
3. Assistant prefill
4. Earlier conversation history
```

## Key Patterns

### Pattern 1: System Prompt Template
```xml
You are a [ROLE] specializing in [DOMAIN].

## Context
[Relevant background the model needs — project, user, constraints]

## Your Task
[What the model should do — be specific about scope]

## Output Format
[Exact format: JSON schema, markdown structure, or prose style]
Format your response as:
{
  "summary": "...",
  "items": [...],
  "confidence": "high|medium|low"
}

## Constraints
- Do not [specific prohibition]
- Always [specific requirement]
- If unsure, say "I don't know" rather than guessing
```

### Pattern 2: Few-Shot Examples
```
Classify the sentiment of these customer reviews.

Examples:
Input: "The product broke after 2 days. Terrible quality."
Output: { "sentiment": "negative", "intensity": "high", "topic": "product quality" }

Input: "Works as described. Shipping was fast."
Output: { "sentiment": "positive", "intensity": "medium", "topic": "shipping" }

Input: "It's okay I guess, nothing special."
Output: { "sentiment": "neutral", "intensity": "low", "topic": "general" }

Now classify:
Input: "Amazing! Best purchase I've made this year."
Output:
```

### Pattern 3: RAG Prompt Structure
```xml
You are a helpful assistant. Answer the user's question using ONLY
the provided context. If the answer is not in the context, say
"I don't have that information."

<context>
[RETRIEVED_CHUNK_1]
Source: documentation/api-auth.md

[RETRIEVED_CHUNK_2]
Source: documentation/getting-started.md
</context>

<question>
{user_question}
</question>

Answer based on the context above:
```

### Pattern 4: Structured Output Enforcement
```python
# Use XML tags for reliable parsing
system_prompt = """
Analyze the code and respond in this exact format:

<analysis>
<security_issues>
  <issue severity="HIGH|MEDIUM|LOW">
    <description>...</description>
    <line>...</line>
    <fix>...</fix>
  </issue>
</security_issues>
<summary>...</summary>
</analysis>
"""
```

## Best Practices
1. Be specific about output format — vague instructions produce inconsistent output
2. Put critical instructions both at the start AND end of long prompts
3. Use XML/JSON tags for structured data extraction — more reliable than prose instructions
4. Few-shot examples should cover edge cases, not just happy paths
5. For RAG: include source metadata with each chunk so the model can cite sources
6. Temperature 0 for deterministic tasks; 0.7-1.0 for creative/generative tasks
7. Test prompts against adversarial inputs — users will find the edge cases

## Common Issues
- **Inconsistent output format**: add explicit format instructions + a few-shot example in the exact format
- **Model ignores instructions**: move them to the end of the prompt; long prompts suffer from instruction forgetting
- **RAG hallucination**: add explicit "if not in context, say you don't know" and cite source documents
- **Prompt injection**: sanitize user input before inserting into prompts; use separate system/user channels
