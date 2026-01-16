# Browser4AGI

**Intelligent Agent System** - A Python-based agent framework capable of long-term survival, self-repair, and self-expansion in the web world.

## Features

### 🔄 Long-Term Survival
- **State Persistence**: Automatic state saving and recovery across restarts
- **Restart Tracking**: Monitors and tracks agent lifecycle
- **Graceful Shutdown**: Ensures state is saved before termination

### 🔧 Self-Repair
- **Health Monitoring**: Continuous health checks with configurable intervals
- **Automatic Repair**: Detects and fixes issues automatically
- **Repair History**: Tracks all repair attempts for analysis

### 📈 Self-Expansion
- **Capability Registry**: Dynamic registration of new capabilities
- **Plugin System**: Easy extension with new functionality
- **Usage Tracking**: Monitors capability usage and performance

### 🌐 Web Capabilities
- **Web Navigation**: Browse and navigate web pages
- **Web Scraping**: Extract data from websites
- **API Interaction**: Call REST APIs and handle responses
- **Web Monitoring**: Monitor URLs for changes
- **Browser Automation**: Automate web interactions and workflows

## Quick Start

### Basic Usage

```python
from agent import IntelligentAgent

# Create an agent
agent = IntelligentAgent(name="MyAgent")

# Run the agent
agent.run(duration=60)  # Run for 60 seconds
```

### With Web Capabilities

```python
from agent import IntelligentAgent
from web_capabilities import register_web_capabilities

# Create and expand agent
agent = IntelligentAgent(name="WebAgent")
register_web_capabilities(agent)

# Use capabilities
web_nav = agent.get_capability("web_navigation")
result = web_nav.navigate("https://example.com")

scraper = agent.get_capability("web_scraper")
data = scraper.scrape("https://example.com", selector=".content")
```

### Run Examples

```bash
# Run all examples
python examples.py all

# Run specific examples
python examples.py basic        # Basic usage
python examples.py expansion    # Self-expansion demo
python examples.py repair       # Self-repair demo
python examples.py survival     # Long-term survival demo
python examples.py automation   # Web automation demo
python examples.py api          # API interaction demo
```

## Architecture

### Core Components

1. **IntelligentAgent**: Main agent class with lifecycle management
2. **HealthMonitor**: Monitors agent health and detects issues
3. **StatePersistence**: Manages state persistence for survival
4. **CapabilityRegistry**: Registers and manages capabilities
5. **SelfRepairSystem**: Handles automatic repair mechanisms

### Web Capabilities

- **WebNavigationCapability**: Navigate web pages
- **WebScraperCapability**: Scrape web content
- **APIInteractionCapability**: Interact with APIs
- **WebMonitoringCapability**: Monitor web resources
- **WebAutomationCapability**: Automate browser tasks

## Configuration

Edit `config.json` to customize agent behavior:

```json
{
  "agent": {
    "name": "Browser4AGI",
    "state_file": "agent_state.json"
  },
  "health_monitoring": {
    "check_interval_seconds": 60
  },
  "self_repair": {
    "enabled": true
  }
}
```

## Requirements

Basic functionality requires only Python 3.7+. No external dependencies needed for core features.

Optional dependencies for production use:
```
requests>=2.31.0      # For real HTTP requests
beautifulsoup4>=4.12.0  # For web scraping
playwright>=1.40.0    # For browser automation
httpx>=0.25.0         # For async HTTP requests
```

## Design Principles

1. **Minimal Dependencies**: Core system works without external libraries
2. **Extensible**: Easy to add new capabilities
3. **Resilient**: Automatic recovery from failures
4. **Observable**: Comprehensive logging and metrics
5. **Persistent**: State survives restarts

## API Reference

### IntelligentAgent

```python
agent = IntelligentAgent(name="MyAgent", state_file="agent_state.json")

# Core methods
agent.run(duration=None)              # Run agent
agent.perform_health_check()           # Check health
agent.perform_self_repair()            # Trigger repair
agent.expand_capability(name, cap)     # Add capability
agent.get_capability(name)             # Get capability
agent.get_status()                     # Get status
agent.shutdown()                       # Graceful shutdown
```

### Capabilities

```python
# Web Navigation
web_nav = agent.get_capability("web_navigation")
web_nav.navigate(url)
web_nav.get_history()

# Web Scraping
scraper = agent.get_capability("web_scraper")
scraper.scrape(url, selector=None)
scraper.get_scraped_data(url)

# API Interaction
api = agent.get_capability("api_interaction")
api.call_api(endpoint, method="GET", data=None)
api.get_request_history()

# Web Monitoring
monitor = agent.get_capability("web_monitoring")
monitor.add_monitor(url, check_interval=300)
monitor.check_monitors()
monitor.get_monitored_urls()

# Web Automation
automation = agent.get_capability("web_automation")
automation.create_task(name, steps)
automation.execute_task(task_id)
automation.get_tasks()
```

## License

Open source - feel free to use and extend.

## Contributing

Contributions welcome! This is a foundational framework designed to be extended and improved.
