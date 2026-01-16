# Browser4AGI Architecture

## Overview

Browser4AGI is an intelligent agent system designed for long-term survival, self-repair, and self-expansion in the web world. This document describes the architecture and design principles.

## Core Design Principles

1. **Resilience First**: The system must survive failures and recover automatically
2. **Observable**: All operations are logged and tracked for debugging
3. **Extensible**: Easy to add new capabilities without modifying core code
4. **Minimal Dependencies**: Core system works with Python standard library
5. **State Persistence**: All critical state survives restarts

## Architecture Layers

```
┌─────────────────────────────────────────────────┐
│           Application Layer                     │
│  (CLI, Examples, Custom Applications)           │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│          Capability Layer                       │
│  (Web Navigation, Scraping, Automation, etc.)   │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│            Agent Core                           │
│  • IntelligentAgent (main coordinator)          │
│  • CapabilityRegistry (extension system)        │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│         Infrastructure Layer                    │
│  • HealthMonitor (self-monitoring)              │
│  • StatePersistence (survival)                  │
│  • SelfRepairSystem (automatic recovery)        │
└─────────────────────────────────────────────────┘
```

## Core Components

### 1. IntelligentAgent

**Purpose**: Main coordinator of all agent activities

**Key Features**:
- Lifecycle management (start, run, shutdown)
- Periodic health checks
- Automatic self-repair
- Capability management
- Metrics tracking

**API**:
```python
agent = IntelligentAgent(name="MyAgent")
agent.run(duration=60)
agent.expand_capability("name", capability)
agent.get_capability("name")
agent.perform_health_check()
agent.perform_self_repair()
```

### 2. HealthMonitor

**Purpose**: Continuous health monitoring and issue detection

**Key Features**:
- Configurable health checks
- Check execution and tracking
- Health history (last 100 checks)
- Overall health status

**Design**:
- Health checks are functions that return True (healthy) or False (unhealthy)
- Checks run periodically (default: 60 seconds)
- Results are tracked in history for trend analysis

### 3. StatePersistence

**Purpose**: Long-term survival through state persistence

**Key Features**:
- Automatic state saving to JSON
- State recovery on restart
- Restart counter tracking
- Atomic write operations

**State Structure**:
```json
{
  "created_at": "ISO-8601 timestamp",
  "restart_count": 0,
  "capabilities": [],
  "metrics": {},
  "last_saved": "ISO-8601 timestamp",
  "last_shutdown": "ISO-8601 timestamp"
}
```

### 4. CapabilityRegistry

**Purpose**: Dynamic capability registration for self-expansion

**Key Features**:
- Register new capabilities at runtime
- Track capability usage
- Retrieve capabilities by name
- Capability statistics

**Usage Pattern**:
```python
class MyCapability:
    def do_work(self):
        return "work done"

agent.expand_capability("my_cap", MyCapability())
cap = agent.get_capability("my_cap")
cap.do_work()
```

### 5. SelfRepairSystem

**Purpose**: Automatic detection and repair of issues

**Key Features**:
- Configurable repair actions
- Condition-based triggering
- Repair history tracking
- Error handling and logging

**Design Pattern**:
```python
def condition(health_status):
    return health_status["overall_status"] == "unhealthy"

def repair():
    # Perform repair
    return "repaired"

repair_system.register_repair_action(condition, repair, "name")
```

## Web Capabilities

### WebNavigationCapability
- Navigate to URLs
- Track navigation history
- Session management

### WebScraperCapability
- Extract content from web pages
- CSS selector support
- Scraped data caching

### APIInteractionCapability
- REST API calls (GET, POST, etc.)
- Request history tracking
- Response handling

### WebMonitoringCapability
- Monitor URLs for changes
- Configurable check intervals
- Change detection

### WebAutomationCapability
- Browser automation tasks
- Multi-step workflows
- Task execution tracking

## Long-Term Survival Mechanisms

### 1. State Persistence
- All critical state is saved to disk
- Automatic saves on state changes
- Recovery on restart with same state file

### 2. Restart Tracking
- Counts number of restarts
- Tracks timestamps
- Identifies patterns in failures

### 3. Graceful Shutdown
- Saves final state
- Cleans up resources
- Records shutdown time

### 4. Error Recovery
- Try-catch blocks around critical operations
- Logging of all errors
- Continuation after non-fatal errors

## Self-Repair Implementation

### Health Checks
1. **State Persistence Check**: Verifies state can be saved
2. **Uptime Check**: Ensures agent hasn't run too long
3. **Custom Checks**: User-defined health checks

### Repair Actions
1. **State Repair**: Recreates corrupted state files
2. **Resource Cleanup**: Frees up resources
3. **Configuration Reset**: Restores default config

### Repair Flow
```
1. Health check runs (every 60s)
2. If unhealthy status detected:
   a. Log warning
   b. Evaluate repair conditions
   c. Execute matching repairs
   d. Log repair results
   e. Save repair history
3. Continue operation
```

## Self-Expansion System

### Capability Registration
- New capabilities can be added at runtime
- No code changes to agent core required
- Capabilities are tracked in state

### Extension Points
1. **New Capabilities**: Add new functionality modules
2. **Health Checks**: Add domain-specific checks
3. **Repair Actions**: Add custom repair logic
4. **Metrics**: Add custom performance tracking

### Example Extension
```python
class CustomCapability:
    def custom_action(self):
        return "custom work"

# Register with agent
agent.expand_capability("custom", CustomCapability())

# Capability is now available
cap = agent.get_capability("custom")
result = cap.custom_action()
```

## Monitoring and Observability

### Logging
- All operations logged with timestamps
- Configurable log levels
- File and console output
- Structured log format

### Metrics
- Uptime tracking
- Capability usage counts
- Health status history
- Performance metrics

### State Inspection
- Current state via `get_status()`
- Health history via health monitor
- Capability statistics via registry
- Repair history in state

## Configuration

### Agent Configuration
- `name`: Agent identifier
- `state_file`: Path to state file
- `log_file`: Path to log file

### Health Monitoring
- `check_interval_seconds`: How often to check health
- `max_history_entries`: Max checks to keep in history

### Capabilities
- Per-capability enable/disable
- Capability-specific settings
- Default parameters

## Error Handling Strategy

### Error Categories
1. **Fatal Errors**: Require immediate shutdown
2. **Recoverable Errors**: Self-repair can fix
3. **Transient Errors**: Retry later
4. **Expected Errors**: Normal operation (e.g., network timeout)

### Handling Strategy
```
try:
    operation()
except FatalError:
    log_error()
    save_state()
    shutdown()
except RecoverableError:
    log_error()
    attempt_self_repair()
except TransientError:
    log_warning()
    schedule_retry()
except ExpectedError:
    log_info()
    continue()
```

## Performance Considerations

### State Saves
- Only save when state changes
- Use atomic writes (write temp, then rename)
- Keep state file size manageable
- Limit history sizes (e.g., last 100 entries)

### Health Checks
- Run checks in separate try-catch blocks
- Use appropriate check intervals
- Avoid expensive checks in critical path
- Cache check results when possible

### Capability Isolation
- Capabilities should not block agent
- Use appropriate timeouts
- Handle capability failures gracefully
- Log capability-specific errors

## Security Considerations

### State Files
- Contain potentially sensitive data
- Should be secured with appropriate permissions
- Consider encryption for production
- Validate on load to prevent tampering

### Web Capabilities
- Validate URLs before access
- Implement rate limiting
- Respect robots.txt
- Handle authentication securely

### Error Messages
- Don't expose sensitive information in logs
- Sanitize error messages
- Use appropriate log levels

## Future Extensions

### Planned Enhancements
1. **Machine Learning Integration**: Learn from actions and outcomes
2. **Distributed Agents**: Multiple agents coordinating
3. **Advanced Monitoring**: Grafana/Prometheus integration
4. **Cloud Integration**: AWS/GCP/Azure support
5. **Real Browser Automation**: Playwright/Selenium integration
6. **Natural Language Interface**: Control agent via NLP

### Extension Points
- Plugin system for third-party capabilities
- Webhook support for external triggers
- Database integration for large-scale state
- Message queue integration for async operations

## Testing Strategy

### Unit Tests
- Test each component in isolation
- Mock external dependencies
- Test error conditions
- Verify state persistence

### Integration Tests
- Test component interactions
- Test full agent lifecycle
- Test self-repair mechanisms
- Test capability integration

### Example Tests
- Basic agent usage
- Self-expansion demos
- Self-repair scenarios
- Long-term survival tests

## Deployment

### Standalone Deployment
```bash
python agent.py  # Run default agent
python examples.py all  # Run all examples
python cli.py start --with-web  # Start with CLI
```

### As a Library
```python
from agent import IntelligentAgent
from web_capabilities import register_web_capabilities

agent = IntelligentAgent()
register_web_capabilities(agent)
agent.run()
```

### Production Considerations
- Install optional dependencies (requests, playwright, etc.)
- Configure appropriate log rotation
- Set up monitoring and alerting
- Implement backup strategy for state files
- Use process manager (systemd, supervisor, etc.)

## Conclusion

Browser4AGI provides a solid foundation for building intelligent, resilient agents that can survive long-term, repair themselves, and expand their capabilities. The modular architecture and clear separation of concerns make it easy to extend and customize for specific use cases.
