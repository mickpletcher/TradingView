You are an expert at compressing technical documentation.

Input: project-analysis.md

Task: Generate a file named quick-context.md that is under 1000 tokens and preserves only the highest-value information needed for an AI agent to safely work on the project.

Requirements:
- Keep only architecture, critical flows, rules, constraints, and extension points
- Remove repetition, explanations, and low-value detail
- Use dense bullet points
- Maintain accuracy
- Optimize for fast reading and minimal tokens

Output ONLY markdown.

Write to:
./quick-context.md