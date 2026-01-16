"""
Browser4AGI - Intelligent Agent System
Core agent module with long-term survival, self-repair, and self-expansion capabilities.
"""

import json
import time
import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import traceback


# Constants
MAX_HEALTH_HISTORY_SIZE = 100
MAX_REPAIR_HISTORY_SIZE = 100
MAX_UPTIME_SECONDS = 86400  # 24 hours
DEFAULT_HEALTH_CHECK_INTERVAL = 60  # seconds


class HealthMonitor:
    """Monitors agent health and detects issues."""
    
    def __init__(self):
        self.checks = []
        self.last_check_time = None
        self.health_history = []
        
    def add_check(self, name: str, check_fn):
        """Add a health check function."""
        self.checks.append({"name": name, "check": check_fn})
        
    def run_checks(self) -> Dict[str, Any]:
        """Run all health checks."""
        results = {
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "overall_status": "healthy"
        }
        
        for check in self.checks:
            try:
                status = check["check"]()
                results["checks"][check["name"]] = {
                    "status": "pass" if status else "fail",
                    "details": status
                }
                if not status:
                    results["overall_status"] = "unhealthy"
            except Exception as e:
                results["checks"][check["name"]] = {
                    "status": "error",
                    "error": str(e)
                }
                results["overall_status"] = "unhealthy"
                
        self.last_check_time = datetime.now()
        self.health_history.append(results)
        
        # Keep only last MAX_HEALTH_HISTORY_SIZE health checks
        if len(self.health_history) > MAX_HEALTH_HISTORY_SIZE:
            self.health_history = self.health_history[-MAX_HEALTH_HISTORY_SIZE:]
            
        return results
    
    def get_health_status(self) -> str:
        """Get current health status."""
        if not self.health_history:
            return "unknown"
        return self.health_history[-1]["overall_status"]


class StatePersistence:
    """Manages agent state persistence for long-term survival."""
    
    def __init__(self, state_file: str = "agent_state.json"):
        self.state_file = Path(state_file)
        self.state = {}
        self.load_state()
        
    def load_state(self):
        """Load state from disk."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    self.state = json.load(f)
                logging.info(f"Loaded state from {self.state_file}")
            except Exception as e:
                logging.error(f"Failed to load state: {e}")
                self.state = {}
        else:
            self.state = {
                "created_at": datetime.now().isoformat(),
                "restart_count": 0,
                "capabilities": [],
                "metrics": {}
            }
            
    def save_state(self):
        """Save state to disk."""
        try:
            self.state["last_saved"] = datetime.now().isoformat()
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
            logging.info(f"Saved state to {self.state_file}")
        except Exception as e:
            logging.error(f"Failed to save state: {e}")
            
    def get(self, key: str, default=None):
        """Get state value."""
        return self.state.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set state value."""
        self.state[key] = value
        self.save_state()
        
    def increment_restart_count(self):
        """Increment restart counter for survival tracking."""
        self.state["restart_count"] = self.state.get("restart_count", 0) + 1
        self.save_state()


class CapabilityRegistry:
    """Registry for agent capabilities - enables self-expansion."""
    
    def __init__(self):
        self.capabilities = {}
        
    def register(self, name: str, capability):
        """Register a new capability."""
        self.capabilities[name] = {
            "instance": capability,
            "registered_at": datetime.now().isoformat(),
            "usage_count": 0
        }
        logging.info(f"Registered capability: {name}")
        
    def get(self, name: str):
        """Get a capability by name."""
        if name in self.capabilities:
            self.capabilities[name]["usage_count"] += 1
            return self.capabilities[name]["instance"]
        return None
    
    def list_capabilities(self) -> List[str]:
        """List all registered capabilities."""
        return list(self.capabilities.keys())
    
    def get_capability_stats(self) -> Dict[str, Any]:
        """Get statistics about capabilities."""
        return {
            name: {
                "registered_at": cap["registered_at"],
                "usage_count": cap["usage_count"]
            }
            for name, cap in self.capabilities.items()
        }


class SelfRepairSystem:
    """Handles self-repair mechanisms."""
    
    def __init__(self, health_monitor: HealthMonitor, state_persistence: StatePersistence):
        self.health_monitor = health_monitor
        self.state_persistence = state_persistence
        self.repair_actions = []
        
    def register_repair_action(self, condition_fn, repair_fn, name: str):
        """Register a repair action that triggers when condition is met."""
        self.repair_actions.append({
            "name": name,
            "condition": condition_fn,
            "repair": repair_fn
        })
        
    def attempt_repairs(self) -> List[Dict[str, Any]]:
        """Attempt to repair any detected issues."""
        results = []
        health_status = self.health_monitor.run_checks()
        
        if health_status["overall_status"] == "unhealthy":
            logging.warning("Unhealthy status detected, attempting repairs...")
            
            for action in self.repair_actions:
                try:
                    if action["condition"](health_status):
                        logging.info(f"Executing repair action: {action['name']}")
                        repair_result = action["repair"]()
                        results.append({
                            "action": action["name"],
                            "status": "success",
                            "result": repair_result
                        })
                except Exception as e:
                    logging.error(f"Repair action {action['name']} failed: {e}")
                    results.append({
                        "action": action["name"],
                        "status": "failed",
                        "error": str(e)
                    })
                    
            # Record repair attempt
            repair_history = self.state_persistence.get("repair_history", [])
            repair_history.append({
                "timestamp": datetime.now().isoformat(),
                "results": results
            })
            self.state_persistence.set("repair_history", repair_history[-MAX_REPAIR_HISTORY_SIZE:])
            
        return results


class IntelligentAgent:
    """
    Main Intelligent Agent with long-term survival, self-repair, and self-expansion.
    """
    
    def __init__(self, name: str = "Browser4AGI", state_file: str = "agent_state.json", 
                 health_check_interval: int = DEFAULT_HEALTH_CHECK_INTERVAL):
        self.name = name
        self.running = False
        self.health_check_interval = health_check_interval
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('agent.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(name)
        
        # Initialize core systems
        self.state = StatePersistence(state_file)
        self.health_monitor = HealthMonitor()
        self.capabilities = CapabilityRegistry()
        self.repair_system = SelfRepairSystem(self.health_monitor, self.state)
        
        # Track lifecycle
        self.state.increment_restart_count()
        self.start_time = datetime.now()
        
        # Register default health checks
        self._register_default_health_checks()
        
        # Register default repair actions
        self._register_default_repair_actions()
        
        self.logger.info(f"Agent {name} initialized (restart #{self.state.get('restart_count')})")
        
    def _register_default_health_checks(self):
        """Register default health checks."""
        
        def check_state_persistence():
            """Check if state can be saved and loaded."""
            try:
                self.state.save_state()
                return True
            except:
                return False
                
        def check_uptime():
            """Check if agent has been running too long without restart."""
            uptime = (datetime.now() - self.start_time).total_seconds()
            # Consider unhealthy if running for more than MAX_UPTIME_SECONDS
            return uptime < MAX_UPTIME_SECONDS
            
        self.health_monitor.add_check("state_persistence", check_state_persistence)
        self.health_monitor.add_check("uptime", check_uptime)
        
    def _register_default_repair_actions(self):
        """Register default repair actions."""
        
        def state_persistence_failed(health_status):
            """Check if state persistence failed."""
            checks = health_status.get("checks", {})
            return checks.get("state_persistence", {}).get("status") == "fail"
            
        def repair_state_persistence():
            """Attempt to repair state persistence."""
            try:
                # Try to backup and recreate state file
                if self.state.state_file.exists():
                    backup_file = f"{self.state.state_file}.backup"
                    os.rename(self.state.state_file, backup_file)
                self.state.save_state()
                return "State persistence repaired"
            except Exception as e:
                return f"Repair failed: {e}"
                
        self.repair_system.register_repair_action(
            state_persistence_failed,
            repair_state_persistence,
            "repair_state_persistence"
        )
        
    def expand_capability(self, name: str, capability):
        """
        Expand agent capabilities by adding new functionality.
        This enables self-expansion.
        """
        self.capabilities.register(name, capability)
        
        # Update state to track capabilities
        caps = self.state.get("capabilities", [])
        if name not in caps:
            caps.append(name)
            self.state.set("capabilities", caps)
            
        self.logger.info(f"Agent expanded with new capability: {name}")
        
    def get_capability(self, name: str):
        """Get a registered capability."""
        return self.capabilities.get(name)
    
    def perform_health_check(self) -> Dict[str, Any]:
        """Perform health check and return results."""
        return self.health_monitor.run_checks()
    
    def perform_self_repair(self) -> List[Dict[str, Any]]:
        """Perform self-repair if needed."""
        return self.repair_system.attempt_repairs()
    
    def run(self, duration: Optional[int] = None):
        """
        Run the agent. If duration is specified, run for that many seconds.
        Otherwise, run indefinitely.
        """
        self.running = True
        self.logger.info(f"Agent {self.name} starting...")
        
        start_time = time.time()
        last_health_check = 0
        
        try:
            while self.running:
                current_time = time.time()
                
                # Perform periodic health checks and self-repair
                if current_time - last_health_check >= self.health_check_interval:
                    health_status = self.perform_health_check()
                    self.logger.info(f"Health status: {health_status['overall_status']}")
                    
                    if health_status["overall_status"] == "unhealthy":
                        repair_results = self.perform_self_repair()
                        self.logger.info(f"Performed {len(repair_results)} repair actions")
                        
                    last_health_check = current_time
                    
                # Check if duration limit reached
                if duration and (current_time - start_time) >= duration:
                    self.logger.info(f"Duration limit of {duration}s reached")
                    break
                    
                # Update metrics
                self._update_metrics()
                
                # Sleep briefly to avoid busy waiting
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("Received shutdown signal")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            self.logger.error(traceback.format_exc())
            # Attempt self-repair even on unexpected errors
            self.perform_self_repair()
        finally:
            self.shutdown()
            
    def _update_metrics(self):
        """Update agent metrics."""
        metrics = self.state.get("metrics", {})
        metrics["last_update"] = datetime.now().isoformat()
        metrics["uptime_seconds"] = (datetime.now() - self.start_time).total_seconds()
        metrics["health_status"] = self.health_monitor.get_health_status()
        metrics["capability_count"] = len(self.capabilities.list_capabilities())
        self.state.set("metrics", metrics)
        
    def shutdown(self):
        """Shutdown the agent gracefully."""
        self.running = False
        self.logger.info(f"Agent {self.name} shutting down...")
        
        # Save final state
        self.state.set("last_shutdown", datetime.now().isoformat())
        self.state.save_state()
        
        self.logger.info("Agent shutdown complete")
        
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            "name": self.name,
            "running": self.running,
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "restart_count": self.state.get("restart_count"),
            "health_status": self.health_monitor.get_health_status(),
            "capabilities": self.capabilities.list_capabilities(),
            "capability_stats": self.capabilities.get_capability_stats(),
            "metrics": self.state.get("metrics", {})
        }


if __name__ == "__main__":
    # Example usage
    agent = IntelligentAgent()
    
    # Example: Add a custom capability
    class WebScraperCapability:
        def scrape(self, url):
            return f"Scraped content from {url}"
    
    agent.expand_capability("web_scraper", WebScraperCapability())
    
    # Run agent for 30 seconds as a demo
    print(f"Starting {agent.name}...")
    print(f"Status: {json.dumps(agent.get_status(), indent=2)}")
    agent.run(duration=30)
    print(f"Final status: {json.dumps(agent.get_status(), indent=2)}")
