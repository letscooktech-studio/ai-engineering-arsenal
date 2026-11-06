# Compatibility

Developed by the LetsCookTech Open Source Team.

OutcomeLab's source of truth is portable Markdown. A skill works anywhere an agent can receive a task-specific instruction file.

| Surface | Use now | Adapter status |
| --- | --- | --- |
| Codex | Copy `skills/<name>` into the Codex skills directory; invoke `$<name>`. | Native-compatible |
| Claude Code / Claude Projects | Attach or paste `SKILL.md` as project/task guidance. | Portable source |
| ChatGPT / Gemini | Paste the skill and task context in the same conversation. | Portable source |
| Cursor / Windsurf | Reference the selected `SKILL.md` from a workspace rule. | Portable source |
| Cline / Roo Code / Aider | Include the selected `SKILL.md` in the task context. | Portable source |
| Agent SDKs / MCP clients | Load skill text at task routing time; keep tool permissions outside the skill. | Integration pattern |

Adapters must preserve the original safety boundaries, output contract, and version. Do not claim native support for a platform until a tested adapter is published.
