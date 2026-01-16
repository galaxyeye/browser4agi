# Quick Start Guide

Get started with Browser4AGI in 5 minutes!

## Installation

No installation required! Just Python 3.7+.

```bash
git clone https://github.com/galaxyeye/browser4agi.git
cd browser4agi
```

## Run Your First Agent

### Option 1: Using Python Directly

```python
from agent import IntelligentAgent
from web_capabilities import register_web_capabilities

# Create agent
agent = IntelligentAgent(name="MyFirstAgent")

# Add web capabilities
register_web_capabilities(agent)

# Check status
print(agent.get_status())

# Run for 30 seconds
agent.run(duration=30)
```

### Option 2: Using CLI

```bash
# Start agent with web capabilities
python cli.py start --with-web --duration 30

# Check agent status
python cli.py status --with-web

# Check health
python cli.py health

# List capabilities
python cli.py capabilities --with-web

# Navigate to a URL
python cli.py navigate https://example.com

# Scrape a URL
python cli.py scrape https://example.com --selector .content
```

### Option 3: Run Examples

```bash
# Run all examples
python examples.py all

# Or run specific examples
python examples.py basic        # Basic usage
python examples.py expansion    # Self-expansion
python examples.py repair       # Self-repair
python examples.py survival     # Long-term survival
python examples.py automation   # Web automation
python examples.py api          # API interaction
```

## Core Concepts

### 1. Long-Term Survival

The agent automatically saves its state to disk and can recover after restarts:

```python
# First run
agent = IntelligentAgent(name="SurvivalAgent", state_file="my_agent.json")
agent.state.set("data", "important info")
agent.shutdown()

# Second run - state is recovered
agent = IntelligentAgent(name="SurvivalAgent", state_file="my_agent.json")
print(agent.state.get("data"))  # "important info"
```

### 2. Self-Repair

The agent monitors its health and repairs issues automatically:

```python
# Health check runs automatically every 60 seconds
agent.run()

# Or trigger manually
health = agent.perform_health_check()
if health["overall_status"] == "unhealthy":
    agent.perform_self_repair()
```

### 3. Self-Expansion

Add new capabilities dynamically:

```python
# Define a custom capability
class MyCapability:
    def do_work(self):
        return "work completed"

# Add to agent
agent.expand_capability("my_capability", MyCapability())

# Use it
cap = agent.get_capability("my_capability")
result = cap.do_work()
```

## Common Tasks

### Navigate Web Pages

```python
agent = IntelligentAgent()
register_web_capabilities(agent)

nav = agent.get_capability("web_navigation")
result = nav.navigate("https://example.com")
print(result)
```

### Scrape Web Content

```python
scraper = agent.get_capability("web_scraper")
data = scraper.scrape("https://example.com", selector=".main-content")
print(data)
```

### Call APIs

```python
api = agent.get_capability("api_interaction")
response = api.call_api("https://api.example.com/data", method="GET")
print(response)
```

### Monitor URLs

```python
monitor = agent.get_capability("web_monitoring")
monitor.add_monitor("https://example.com/status", check_interval=60)
results = monitor.check_monitors()
print(results)
```

### Automate Browser Tasks

```python
automation = agent.get_capability("web_automation")

steps = [
    {"action": "navigate", "url": "https://example.com"},
    {"action": "click", "selector": "#button"},
    {"action": "fill", "selector": "#input", "value": "test"}
]

task = automation.create_task("My Task", steps)
result = automation.execute_task(task["id"])
print(result)
```

## Testing

Run the test suite:

```bash
python -m unittest test_agent.py -v
```

All 22 tests should pass!

## Next Steps

1. Read the [README.md](README.md) for detailed documentation
2. Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand the design
3. Explore [examples.py](examples.py) for more usage patterns
4. Create your own capabilities and extend the agent

## Production Use

For production environments:

1. Install optional dependencies:
```bash
pip install -r requirements.txt
```

2. Configure logging and monitoring

3. Use a process manager (systemd, supervisor, etc.)

4. Set up state file backups

5. Implement security measures (see ARCHITECTURE.md)

## Troubleshooting

### Agent won't start
- Check Python version (3.7+ required)
- Verify state file permissions
- Check logs in `agent.log`

### Health checks failing
- Run `python cli.py health` to see details
- Check disk space for state file writes
- Review logs for specific errors

### Capabilities not working
- Verify capabilities are registered with `--with-web` flag
- Check capability statistics: `python cli.py capabilities --with-web`
- Review capability-specific logs

## Getting Help

- Read the documentation files
- Check the examples
- Review the test cases for usage patterns
- Examine the code - it's well-commented!

## License

Open source - use and extend freely!
