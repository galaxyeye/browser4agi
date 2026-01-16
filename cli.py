#!/usr/bin/env python3
"""
Command-line interface for Browser4AGI intelligent agent system.
"""

import sys
import json
import argparse
from agent import IntelligentAgent
from web_capabilities import register_web_capabilities


def cmd_start(args):
    """Start the agent."""
    agent = IntelligentAgent(name=args.name, state_file=args.state_file)
    
    if args.with_web:
        print("Registering web capabilities...")
        register_web_capabilities(agent)
    
    print(f"Starting agent '{args.name}'...")
    print(f"State file: {args.state_file}")
    print(f"Duration: {args.duration if args.duration else 'indefinite'}")
    
    agent.run(duration=args.duration)


def cmd_status(args):
    """Show agent status."""
    agent = IntelligentAgent(name=args.name, state_file=args.state_file)
    
    if args.with_web:
        register_web_capabilities(agent)
    
    status = agent.get_status()
    print(json.dumps(status, indent=2))


def cmd_health(args):
    """Check agent health."""
    agent = IntelligentAgent(name=args.name, state_file=args.state_file)
    
    health = agent.perform_health_check()
    print(json.dumps(health, indent=2))
    
    if health["overall_status"] == "unhealthy":
        print("\nAgent is unhealthy!")
        if args.repair:
            print("Attempting repairs...")
            results = agent.perform_self_repair()
            print(json.dumps(results, indent=2))


def cmd_capabilities(args):
    """List available capabilities."""
    agent = IntelligentAgent(name=args.name, state_file=args.state_file)
    
    if args.with_web:
        register_web_capabilities(agent)
    
    caps = agent.capabilities.list_capabilities()
    stats = agent.capabilities.get_capability_stats()
    
    print(f"Registered capabilities ({len(caps)}):")
    for cap_name in caps:
        cap_stats = stats.get(cap_name, {})
        print(f"  - {cap_name}")
        print(f"    Registered: {cap_stats.get('registered_at', 'N/A')}")
        print(f"    Usage count: {cap_stats.get('usage_count', 0)}")


def cmd_navigate(args):
    """Navigate to a URL."""
    agent = IntelligentAgent(name=args.name, state_file=args.state_file)
    register_web_capabilities(agent)
    
    nav = agent.get_capability("web_navigation")
    if not nav:
        print("Error: web_navigation capability not available")
        return
    
    result = nav.navigate(args.url)
    print(json.dumps(result, indent=2))


def cmd_scrape(args):
    """Scrape a URL."""
    agent = IntelligentAgent(name=args.name, state_file=args.state_file)
    register_web_capabilities(agent)
    
    scraper = agent.get_capability("web_scraper")
    if not scraper:
        print("Error: web_scraper capability not available")
        return
    
    result = scraper.scrape(args.url, selector=args.selector)
    print(json.dumps(result, indent=2))


def cmd_reset(args):
    """Reset agent state."""
    import os
    
    if os.path.exists(args.state_file):
        if args.force:
            os.remove(args.state_file)
            print(f"State file '{args.state_file}' removed.")
        else:
            print(f"State file '{args.state_file}' exists.")
            print("Use --force to remove it.")
    else:
        print(f"State file '{args.state_file}' does not exist.")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Browser4AGI - Intelligent Agent System CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s start --with-web --duration 60
  %(prog)s status
  %(prog)s health --repair
  %(prog)s capabilities --with-web
  %(prog)s navigate https://example.com
  %(prog)s scrape https://example.com --selector .content
        """
    )
    
    parser.add_argument(
        '--name',
        default='Browser4AGI',
        help='Agent name (default: Browser4AGI)'
    )
    
    parser.add_argument(
        '--state-file',
        default='agent_state.json',
        help='State file path (default: agent_state.json)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start the agent')
    start_parser.add_argument('--duration', type=int, help='Run duration in seconds')
    start_parser.add_argument('--with-web', action='store_true', help='Register web capabilities')
    start_parser.set_defaults(func=cmd_start)
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show agent status')
    status_parser.add_argument('--with-web', action='store_true', help='Register web capabilities')
    status_parser.set_defaults(func=cmd_status)
    
    # Health command
    health_parser = subparsers.add_parser('health', help='Check agent health')
    health_parser.add_argument('--repair', action='store_true', help='Attempt repairs if unhealthy')
    health_parser.set_defaults(func=cmd_health)
    
    # Capabilities command
    caps_parser = subparsers.add_parser('capabilities', help='List capabilities')
    caps_parser.add_argument('--with-web', action='store_true', help='Register web capabilities')
    caps_parser.set_defaults(func=cmd_capabilities)
    
    # Navigate command
    nav_parser = subparsers.add_parser('navigate', help='Navigate to URL')
    nav_parser.add_argument('url', help='URL to navigate to')
    nav_parser.set_defaults(func=cmd_navigate)
    
    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Scrape URL')
    scrape_parser.add_argument('url', help='URL to scrape')
    scrape_parser.add_argument('--selector', help='CSS selector to scrape')
    scrape_parser.set_defaults(func=cmd_scrape)
    
    # Reset command
    reset_parser = subparsers.add_parser('reset', help='Reset agent state')
    reset_parser.add_argument('--force', action='store_true', help='Force reset without confirmation')
    reset_parser.set_defaults(func=cmd_reset)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        args.func(args)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
