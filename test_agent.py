"""
Test suite for Browser4AGI intelligent agent system.
Tests core functionality: long-term survival, self-repair, and self-expansion.
"""

import unittest
import os
import json
import time
from pathlib import Path
from agent import IntelligentAgent, HealthMonitor, StatePersistence, CapabilityRegistry, SelfRepairSystem
from web_capabilities import (
    WebNavigationCapability,
    WebScraperCapability,
    APIInteractionCapability,
    WebMonitoringCapability,
    WebAutomationCapability,
    register_web_capabilities
)


class TestHealthMonitor(unittest.TestCase):
    """Test health monitoring system."""
    
    def test_health_check_creation(self):
        """Test creating health checks."""
        monitor = HealthMonitor()
        
        def dummy_check():
            return True
        
        monitor.add_check("test_check", dummy_check)
        self.assertEqual(len(monitor.checks), 1)
        self.assertEqual(monitor.checks[0]["name"], "test_check")
    
    def test_health_check_execution(self):
        """Test executing health checks."""
        monitor = HealthMonitor()
        
        monitor.add_check("pass_check", lambda: True)
        monitor.add_check("fail_check", lambda: False)
        
        results = monitor.run_checks()
        
        self.assertIn("checks", results)
        self.assertIn("pass_check", results["checks"])
        self.assertIn("fail_check", results["checks"])
        self.assertEqual(results["checks"]["pass_check"]["status"], "pass")
        self.assertEqual(results["checks"]["fail_check"]["status"], "fail")
        self.assertEqual(results["overall_status"], "unhealthy")
    
    def test_health_status(self):
        """Test getting health status."""
        monitor = HealthMonitor()
        
        self.assertEqual(monitor.get_health_status(), "unknown")
        
        monitor.add_check("pass_check", lambda: True)
        monitor.run_checks()
        
        self.assertEqual(monitor.get_health_status(), "healthy")


class TestStatePersistence(unittest.TestCase):
    """Test state persistence for long-term survival."""
    
    def setUp(self):
        """Set up test state file."""
        self.test_state_file = "test_state.json"
        if os.path.exists(self.test_state_file):
            os.remove(self.test_state_file)
    
    def tearDown(self):
        """Clean up test state file."""
        if os.path.exists(self.test_state_file):
            os.remove(self.test_state_file)
    
    def test_state_creation(self):
        """Test creating new state."""
        state = StatePersistence(self.test_state_file)
        
        self.assertIn("created_at", state.state)
        self.assertIn("restart_count", state.state)
        self.assertEqual(state.state["restart_count"], 0)
    
    def test_state_persistence(self):
        """Test state saves and loads correctly."""
        # Create and save state
        state1 = StatePersistence(self.test_state_file)
        state1.set("test_key", "test_value")
        
        # Load state in new instance
        state2 = StatePersistence(self.test_state_file)
        
        self.assertEqual(state2.get("test_key"), "test_value")
    
    def test_restart_count(self):
        """Test restart counter increments."""
        state1 = StatePersistence(self.test_state_file)
        state1.increment_restart_count()
        self.assertEqual(state1.get("restart_count"), 1)
        
        state2 = StatePersistence(self.test_state_file)
        state2.increment_restart_count()
        self.assertEqual(state2.get("restart_count"), 2)


class TestCapabilityRegistry(unittest.TestCase):
    """Test capability registry for self-expansion."""
    
    def test_capability_registration(self):
        """Test registering capabilities."""
        registry = CapabilityRegistry()
        
        class DummyCapability:
            pass
        
        cap = DummyCapability()
        registry.register("test_cap", cap)
        
        self.assertIn("test_cap", registry.capabilities)
        self.assertEqual(registry.get("test_cap"), cap)
    
    def test_capability_usage_tracking(self):
        """Test capability usage is tracked."""
        registry = CapabilityRegistry()
        
        class DummyCapability:
            pass
        
        cap = DummyCapability()
        registry.register("test_cap", cap)
        
        # Use capability multiple times
        registry.get("test_cap")
        registry.get("test_cap")
        registry.get("test_cap")
        
        stats = registry.get_capability_stats()
        self.assertEqual(stats["test_cap"]["usage_count"], 3)
    
    def test_list_capabilities(self):
        """Test listing capabilities."""
        registry = CapabilityRegistry()
        
        registry.register("cap1", object())
        registry.register("cap2", object())
        
        caps = registry.list_capabilities()
        self.assertEqual(len(caps), 2)
        self.assertIn("cap1", caps)
        self.assertIn("cap2", caps)


class TestIntelligentAgent(unittest.TestCase):
    """Test main intelligent agent."""
    
    def setUp(self):
        """Set up test agent."""
        self.test_state_file = "test_agent_state.json"
        if os.path.exists(self.test_state_file):
            os.remove(self.test_state_file)
    
    def tearDown(self):
        """Clean up test files."""
        if os.path.exists(self.test_state_file):
            os.remove(self.test_state_file)
        if os.path.exists("agent.log"):
            os.remove("agent.log")
    
    def test_agent_initialization(self):
        """Test agent initializes correctly."""
        agent = IntelligentAgent(name="TestAgent", state_file=self.test_state_file)
        
        self.assertEqual(agent.name, "TestAgent")
        self.assertFalse(agent.running)
        self.assertEqual(agent.state.get("restart_count"), 1)
    
    def test_agent_status(self):
        """Test getting agent status."""
        agent = IntelligentAgent(name="TestAgent", state_file=self.test_state_file)
        
        status = agent.get_status()
        
        self.assertIn("name", status)
        self.assertIn("running", status)
        self.assertIn("uptime_seconds", status)
        self.assertIn("health_status", status)
        self.assertIn("capabilities", status)
    
    def test_agent_capability_expansion(self):
        """Test agent can expand with new capabilities."""
        agent = IntelligentAgent(name="TestAgent", state_file=self.test_state_file)
        
        class TestCapability:
            def do_something(self):
                return "done"
        
        cap = TestCapability()
        agent.expand_capability("test_cap", cap)
        
        retrieved_cap = agent.get_capability("test_cap")
        self.assertIsNotNone(retrieved_cap)
        self.assertEqual(retrieved_cap.do_something(), "done")
    
    def test_agent_health_check(self):
        """Test agent health check."""
        agent = IntelligentAgent(name="TestAgent", state_file=self.test_state_file)
        
        health = agent.perform_health_check()
        
        self.assertIn("overall_status", health)
        self.assertIn("checks", health)
    
    def test_agent_run_with_duration(self):
        """Test agent runs for specified duration."""
        agent = IntelligentAgent(name="TestAgent", state_file=self.test_state_file)
        
        start_time = time.time()
        agent.run(duration=2)
        end_time = time.time()
        
        # Should run for approximately 2 seconds
        elapsed = end_time - start_time
        self.assertGreater(elapsed, 1.5)
        self.assertLess(elapsed, 3.0)


class TestWebCapabilities(unittest.TestCase):
    """Test web interaction capabilities."""
    
    def test_web_navigation(self):
        """Test web navigation capability."""
        nav = WebNavigationCapability()
        
        result = nav.navigate("https://example.com")
        
        self.assertEqual(result["url"], "https://example.com")
        self.assertEqual(result["status"], "success")
        
        history = nav.get_history()
        self.assertEqual(len(history), 1)
    
    def test_web_scraper(self):
        """Test web scraping capability."""
        scraper = WebScraperCapability()
        
        result = scraper.scrape("https://example.com", selector=".content")
        
        self.assertEqual(result["url"], "https://example.com")
        self.assertEqual(result["selector"], ".content")
    
    def test_api_interaction(self):
        """Test API interaction capability."""
        api = APIInteractionCapability()
        
        result = api.call_api("https://api.example.com/users", method="GET")
        
        self.assertEqual(result["endpoint"], "https://api.example.com/users")
        self.assertEqual(result["method"], "GET")
        
        history = api.get_request_history()
        self.assertEqual(len(history), 1)
    
    def test_web_monitoring(self):
        """Test web monitoring capability."""
        monitor = WebMonitoringCapability()
        
        config = monitor.add_monitor("https://example.com", check_interval=60)
        
        self.assertEqual(config["url"], "https://example.com")
        self.assertEqual(config["check_interval"], 60)
        self.assertEqual(config["status"], "active")
        
        results = monitor.check_monitors()
        self.assertEqual(len(results), 1)
    
    def test_web_automation(self):
        """Test web automation capability."""
        automation = WebAutomationCapability()
        
        steps = [
            {"action": "navigate", "url": "https://example.com"},
            {"action": "click", "selector": "#button"}
        ]
        
        task = automation.create_task("Test Task", steps)
        
        self.assertEqual(task["name"], "Test Task")
        self.assertEqual(len(task["steps"]), 2)
        
        result = automation.execute_task(task["id"])
        
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["executed_steps"], 2)
    
    def test_register_all_capabilities(self):
        """Test registering all web capabilities."""
        agent = IntelligentAgent(name="TestAgent", state_file="test_web_agent.json")
        
        register_web_capabilities(agent)
        
        caps = agent.capabilities.list_capabilities()
        
        self.assertIn("web_navigation", caps)
        self.assertIn("web_scraper", caps)
        self.assertIn("api_interaction", caps)
        self.assertIn("web_monitoring", caps)
        self.assertIn("web_automation", caps)
        
        # Clean up
        if os.path.exists("test_web_agent.json"):
            os.remove("test_web_agent.json")


class TestSelfRepairSystem(unittest.TestCase):
    """Test self-repair mechanisms."""
    
    def setUp(self):
        """Set up test repair system."""
        self.test_state_file = "test_repair_state.json"
        if os.path.exists(self.test_state_file):
            os.remove(self.test_state_file)
        
        self.monitor = HealthMonitor()
        self.state = StatePersistence(self.test_state_file)
        self.repair_system = SelfRepairSystem(self.monitor, self.state)
    
    def tearDown(self):
        """Clean up test files."""
        if os.path.exists(self.test_state_file):
            os.remove(self.test_state_file)
    
    def test_repair_action_registration(self):
        """Test registering repair actions."""
        def condition(health):
            return True
        
        def repair():
            return "repaired"
        
        self.repair_system.register_repair_action(condition, repair, "test_repair")
        
        self.assertEqual(len(self.repair_system.repair_actions), 1)
    
    def test_repair_execution(self):
        """Test repair actions execute when needed."""
        # Add a failing health check
        self.monitor.add_check("fail_check", lambda: False)
        
        # Add a repair action
        repair_executed = {"value": False}
        
        def condition(health):
            return health["overall_status"] == "unhealthy"
        
        def repair():
            repair_executed["value"] = True
            return "repaired"
        
        self.repair_system.register_repair_action(condition, repair, "test_repair")
        
        # Attempt repairs
        results = self.repair_system.attempt_repairs()
        
        self.assertTrue(repair_executed["value"])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["status"], "success")


if __name__ == "__main__":
    # Run all tests
    unittest.main(verbosity=2)
