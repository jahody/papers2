---
name: claude-agent-sdk
description: Guide for building custom AI agents with the Claude Agent SDK in Python. Use when users want to build, configure, or troubleshoot Python agents using the SDK, need help with authentication, tool permissions, system prompts, MCP integration, or have questions about SDK features like subagents, skills, hooks, slash commands, or plugins.
---

# Claude Agent SDK

Build custom AI agents with the Claude Agent SDK - the same harness that powers Claude Code.

## Installation

```bash
pip install claude-agent-sdk
```

## Quick Start

### Basic Agent Setup

```python
from claude_agent_sdk import Agent

agent = Agent(
  system_prompt='You are a helpful coding assistant.',
  setting_sources=['project']  # Load CLAUDE.md files
)
```

## Core Configuration

### System Prompts

Define your agent's role, expertise, and behavior in the `system_prompt` parameter.

### Tool Permissions

Control tool access with:

- `allowed_tools` - Explicitly allow specific tools
- `disallowed_tools` - Block specific tools
- `permission_mode` - Set overall permission strategy

### File-Based Configuration

The SDK reads from the same file locations as Claude Code:

- **Subagents**: `./.claude/agents/*.md`
- **Skills**: `./.claude/skills/*/SKILL.md`
- **Hooks**: `./.claude/settings.json`
- **Slash Commands**: `./.claude/commands/*.md`
- **Memory**: `CLAUDE.md`, `.claude/CLAUDE.md`, or `~/.claude/CLAUDE.md`

**Note**: To load CLAUDE.md files, set `setting_sources=['project']`.

### Plugins

Load custom plugins programmatically via the `plugins` option to add commands, agents, skills, hooks, and MCP servers.

### MCP Integration

Extend agents with custom tools via Model Context Protocol servers for databases, APIs, and external services.

## Common Agent Types

**Coding**: SRE diagnostics, security audits, code review, incident triage
**Business**: Legal contract review, financial analysis, customer support, content creation

## Branding Guidelines

When building products with the SDK:

**Allowed**: "Claude Agent", "Claude", "{YourProduct} Powered by Claude"
**Not allowed**: "Claude Code", "Claude Code Agent", Claude Code branding elements

Maintain your own product branding - don't mimic Claude Code.

## Troubleshooting

**Bug reports:** <https://github.com/anthropics/claude-agent-sdk-python/issues>

**Changelog:** <https://github.com/anthropics/claude-agent-sdk-python/blob/main/CHANGELOG.md>

## Key Features

- **Context management**: Automatic compaction prevents context overflow
- **Rich tools**: File ops, code execution, web search, MCP extensibility
- **Production ready**: Error handling, session management, monitoring
- **Optimized**: Automatic prompt caching and performance tuning
