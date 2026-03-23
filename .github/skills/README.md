# ClickHouse LLM Integration - Agent Skills

This directory contains Agent Skills following the [agentskills.io](https://agentskills.io) specification. These skills enable AI agents to effectively use the ClickHouse LLM integration system.

## Available Skills

### 1. clickhouse-llm-embedding
**Purpose**: Generate vector embeddings for text using ClickHouse UDFs  
**Providers**: HuggingFace, Perplexity, OpenAI, Local  
**Use Cases**: Semantic search, RAG systems, similarity matching

**When to use**: Activate when you need to generate embeddings for text data, build vector databases, or perform semantic similarity operations.

### 2. clickhouse-llm-chat
**Purpose**: Execute LLM inference directly in ClickHouse  
**Providers**: OpenAI (GPT-4), Anthropic (Claude), Perplexity (Sonar)  
**Use Cases**: Sentiment analysis, classification, summarization, Q&A

**When to use**: Activate when you need to perform text analysis, classification, or generation tasks at scale within SQL queries.

### 3. clickhouse-rag-pipeline
**Purpose**: Build production RAG systems with ClickHouse  
**Components**: Vector search + LLM generation + context retrieval  
**Use Cases**: Knowledge bases, chatbots, document Q&A

**When to use**: Activate when building question-answering systems that need to retrieve relevant context before generating answers.

## Quick Start

### For AI Agents

Skills are automatically discovered when placed in:
- `.github/skills/` (repository-scoped)
- `~/.skills/` (user-scoped)

### For Developers

1. **Copy a skill template**:
```bash
cp -r .github/skills/clickhouse-llm-embedding myproject/
```

2. **Reference in your prompts**:
```
I need to build a semantic search system for customer reviews.
(Agent will automatically discover and use clickhouse-llm-embedding skill)
```

3. **Use the implementations**:
```python
from src.skills.embedding_skill import EmbeddingSkill
from src.agents.qa_agent import QAAgent

# Skills provide the guidance
# Implementations provide the code
```

## Skill Format

Each skill follows the agentskills.io specification:

```
skill-name/
├── SKILL.md              # Required: Instructions + metadata
├── references/           # Optional: Detailed documentation
└── scripts/              # Optional: Helper scripts
```

### SKILL.md Structure

```markdown
---
name: skill-name
description: Clear description for AI agent discovery
---

# Skill Title

## Purpose
What this skill does and why

## When to Use
Specific triggers and contexts

## Quick Start
Minimal working examples

## Step-by-Step
Detailed instructions

## Best Practices
Expert guidance

## References
Links to implementation and examples
```

## Progressive Disclosure

Skills use a three-level architecture:

1. **Level 1 - Metadata** (~100 tokens)
   - `name` and `description` in YAML frontmatter
   - Agent sees what skills are available

2. **Level 2 - Instructions** (<5000 tokens)
   - Full SKILL.md content loaded when activated
   - Detailed steps, examples, best practices

3. **Level 3 - Resources** (on demand)
   - Scripts, references, assets loaded only when needed
   - `scripts/`, `references/`, `assets/`

## Skills vs Implementations

| Aspect | Skills | Python Code |
|--------|--------|-------------|
| **Purpose** | Guide agents on *how* to use | Provide *what* to execute |
| **Format** | Markdown instructions | Python classes/functions |
| **Audience** | AI agents | Developers |
| **Location** | `.github/skills/` | `src/skills/`, `src/agents/` |

**Principle**: "Skills teach. Code executes."

## Integration with Project

### Skills Reference Code

```markdown
# In SKILL.md
- See `../../src/skills/embedding_skill.py` for implementation
- See `../../src/udfs/hf_embed.py` for UDF
- See `../../examples/semantic_search/` for examples
```

### Code Uses Skills

```python
# In qa_agent.py
"""
This agent implements the clickhouse-rag-pipeline skill.
See: .github/skills/clickhouse-rag-pipeline/SKILL.md
"""
```

## Best Practices

### Writing Skills

1. **Clear descriptions**: Help agents know when to activate
2. **Concrete examples**: Show actual SQL/Python code
3. **Step-by-step**: Break down complex workflows
4. **Edge cases**: Document limitations and gotchas
5. **References**: Link to implementation and docs

### Using Skills

1. **Trust the skill**: Follow instructions precisely
2. **Check prerequisites**: Verify environment is ready
3. **Adapt examples**: Customize for your use case
4. **Monitor results**: Validate outputs
5. **Iterate**: Refine based on outcomes

## Related Skills from agents-repo

The parent [pv-udpv/agents](https://github.com/pv-udpv/agents) repository contains additional skills that may be useful:

- **core/**: Observability, filesystem indexing
- **automation/**: MCP agents, research agents
- **network/**: Tailscale, network monitoring
- **research/**: Code graphs, RTR graphs

## Contributing

Skills follow the [agentskills.io specification](https://agentskills.io/specification):

1. **Required**: `SKILL.md` with YAML frontmatter
2. **Name**: Lowercase, hyphens, matches directory name
3. **Description**: 1-1024 chars, clear and specific
4. **Format**: Gerund form preferred (processing-*, analyzing-*)

## Resources

- [agentskills.io](https://agentskills.io) - Official specification
- [pv-udpv/agents](https://github.com/pv-udpv/agents) - Parent skills repository
- [Claude Skills Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills)
- [Skills Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

---

**Version**: 1.0.0  
**Updated**: 2026-03-23  
**Maintainer**: ClickHouse LLM Integration Project
