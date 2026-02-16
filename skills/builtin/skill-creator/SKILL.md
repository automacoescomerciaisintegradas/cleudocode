---
name: skill-creator
description: Meta-skill used to create, iterate, and refine other Cleudocode skills. Use this to generate SKILL.md files and associated instructions from natural language descriptions.
metadata:
  cleudocode:
    emoji: "🛠️"
    category: "productivity"
---

# Skill Creator (Meta-Skill)

This skill is designed to help the agent build new capabilities for the Cleudocode ecosystem.

## Workflow
1. **Identify the Need**: Determine what new capability is required.
2. **Draft the Manifesto**: Create the YAML frontmatter including:
   - `name`: Technical name of the skill.
   - `description`: Clear purpose of the skill.
   - `metadata.cleudocode.emoji`: A representative icon.
   - `metadata.cleudocode.category`: (builtin, productivity, ai_models, etc).
3. **Write the Instructions**: Use clear, concise Markdown to define the skill's logic, best practices, and constraints.
4. **Validation**: Ensure the skill follows the standard structure: `skills/builtin/[skill-name]/SKILL.md`.

## SKILL.md Template
```markdown
---
name: [skill-name]
description: [description]
metadata:
  cleudocode:
    emoji: "[emoji]"
    category: "[category]"
---

# [Title]
[Main content and instructions...]
```

## Best Practices
- Focus on specialized knowledge.
- Avoid generic instructions.
- Include examples and "never-do" guidelines.
