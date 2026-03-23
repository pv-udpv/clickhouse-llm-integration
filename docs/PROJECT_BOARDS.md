# GitHub Project Boards

This project uses GitHub Projects for task management and workflow tracking.

## Project Boards

### 1. Main Development Board
**URL**: https://github.com/users/pv-udpv/projects/1

**Columns**:
- 📋 **Backlog** - All planned features and tasks
- 🎯 **Ready** - Prioritized and ready to start
- 🔨 **In Progress** - Currently being worked on
- 👀 **Review** - In code review or testing
- ✅ **Done** - Completed items

**Custom Fields**:
- **Phase**: 1-6 (Foundation, Embeddings, LLM, MindsDB, Agents, Production)
- **Priority**: Low, Medium, High, Critical
- **Component**: UDF, Skill, Agent, Tool, Docs, Infrastructure
- **Estimated Days**: 1, 2, 3, 5, 8, 13

### 2. Skills & Agents Board
**Focus**: Implementation of the Skills and Agents layer

**Columns**:
- 📦 **Skills Queue** - Atomic operations to implement
- 🤖 **Agents Queue** - Complex workflows to build
- 🧪 **Testing** - Unit and integration tests
- 📚 **Documentation** - Usage examples and guides
- ✅ **Deployed** - Live and documented

### 3. Integration Testing Board
**Focus**: End-to-end integration testing

**Columns**:
- 🧩 **Test Scenarios** - Test cases to implement
- ⚙️ **Setup** - Environment configuration
- 🏃 **Running** - Active test execution
- 🐛 **Issues Found** - Bugs discovered during testing
- ✅ **Verified** - Passing tests

## Workflow Automation

### Issue Labeling
Issues are automatically moved based on labels:

- `status: backlog` → Backlog column
- `status: ready` → Ready column
- `status: in-progress` → In Progress column
- `status: review` → Review column
- `status: done` → Done column

### Phase Labels
- `phase-1: foundation` - Core infrastructure
- `phase-2: embeddings` - Embedding integrations
- `phase-3: llm` - LLM integrations
- `phase-4: mindsdb` - MindsDB layer
- `phase-5: agents` - Agents and orchestration
- `phase-6: production` - Production readiness

### Component Labels
- `component: udf` - ClickHouse UDFs
- `component: skill` - Skills layer
- `component: agent` - Agents layer
- `component: tool` - Utility tools
- `component: docs` - Documentation
- `component: infra` - Infrastructure
- `component: test` - Testing

### Priority Labels
- `priority: critical` - Must be done immediately
- `priority: high` - Important features
- `priority: medium` - Standard priority
- `priority: low` - Nice to have

## Creating Issues

### Template: Feature Implementation
```markdown
## Feature Description
Brief description of the feature

## Phase
- [ ] Phase 1: Foundation
- [ ] Phase 2: Embeddings
- [x] Phase 3: LLM Integration

## Component
- UDF / Skill / Agent / Tool / Docs / Infrastructure

## Tasks
- [ ] Design interface
- [ ] Implement core logic
- [ ] Add unit tests
- [ ] Add integration tests
- [ ] Update documentation
- [ ] Add examples

## Dependencies
List of issues this depends on: #1, #2

## Estimated Effort
2-3 days

## Acceptance Criteria
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Example provided
```

### Template: Bug Report
```markdown
## Bug Description
What went wrong

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happened

## Environment
- ClickHouse version: 
- Python version:
- Component: UDF/Skill/Agent

## Logs
```
paste logs here
```

## Additional Context
Any other relevant information
```

## Milestones

### v0.1.0 - Foundation (Week 1-2)
- Basic project structure
- Docker environment
- Core UDF framework
- Initial documentation

### v0.2.0 - Embeddings (Week 3-4)
- HuggingFace integration
- Perplexity pplx-embed
- Local sentence-transformers
- Vector operations

### v0.3.0 - LLM Integration (Week 5-6)
- OpenAI integration
- Anthropic Claude
- Response caching
- Error handling

### v0.4.0 - MindsDB Layer (Week 7-8)
- MindsDB setup
- Custom handlers
- AutoML templates
- Performance optimization

### v0.5.0 - Agents & Skills (Week 9-10)
- Skills framework
- SearchAgent
- AnalysisAgent
- QA Agent

### v1.0.0 - Production Ready (Week 11-12)
- Performance benchmarks
- Security hardening
- Monitoring
- Complete documentation
- Example applications

## Project Views

### By Phase
Groups all issues by implementation phase

### By Priority
Shows high-priority items first

### By Component
Groups by system component

### Roadmap View
Timeline visualization of milestones

## Automation Rules

### Auto-assign based on component
- `component: udf` → Assign to UDF specialist
- `component: skill` → Assign to Skills developer
- `component: agent` → Assign to Agent architect

### Auto-label PRs
- PR to `src/udfs/*` → Add `component: udf`
- PR to `src/skills/*` → Add `component: skill`
- PR to `src/agents/*` → Add `component: agent`

### Close stale issues
Issues inactive for 30 days with label `status: stale`

## Getting Started

1. **Browse the board**: https://github.com/users/pv-udpv/projects/1
2. **Pick a task** from the "Ready" column
3. **Create a branch**: `git checkout -b feature/task-name`
4. **Move issue** to "In Progress"
5. **Create PR** when ready
6. **Move to Review** after PR created
7. **Merge** when approved → Auto-moves to "Done"

## Dashboard Metrics

The project board tracks:
- **Velocity**: Issues completed per week
- **Cycle Time**: Time from Ready → Done
- **Lead Time**: Time from Created → Done
- **Burndown**: Remaining work by phase
