#!/usr/bin/env python3
"""
Quick start script for LeetCode Rating Prediction API

This script provides easy commands to run the application in different modes.
"""

import sys
import subprocess
import os

PORT:str = os.getenv("PORT", "7667")

def print_banner():
    """Print application banner."""
    print("=" * 60)
    print("🚀 LeetCode Rating Prediction API")
    print("=" * 60)
    print()


def check_env_file():
    """Check if .env file exists."""
    if not os.path.exists(".env"):
        print("⚠️  Warning: .env file not found!")
        print("Creating .env file with default values...")
        
        with open(".env", "w") as f:
            f.write("PORT=7667\n")
            f.write("FIREBASE_CREDENTIALS_PATH=db_config/discordbot1-*.json\n")
            f.write("ALLOWED_ORIGINS=http://localhost:3000\n")
        
        print("✅ .env file created. Please update with your configuration.")
        print()


def run_dev():
    """Run in development mode with auto-reload."""
    print("🔧 Starting development server...")
    print("📚 Swagger UI: http://localhost:{PORT}/docs")
    print("📖 ReDoc: http://localhost:{PORT}/redoc")
    print()
    
    subprocess.run([
        "uv", "run", "fastapi", "dev", "--port", PORT
    ])


def run_prod():
    """Run in production mode."""
    print("🚀 Starting production server...")
    print()
    
    subprocess.run([
        "uv", "run", "uvicorn", "main:app",
        "--host", "0.0.0.0",
        "--port", PORT
    ])


def run_test():
    """Run tests."""
    print("🧪 Running tests...")
    print()
    
    # Check if pytest is installed
    try:
        subprocess.run(["uv", "run", "pytest", "-v"])
    except FileNotFoundError:
        print("❌ pytest not found. Install with: uv add pytest")


def show_help():
    """Show help message."""
    print("Usage: python start.py [command]")
    print()
    print("Commands:")
    print("  dev     - Run development server with auto-reload (default)")
    print("  prod    - Run production server")
    print("  test    - Run tests")
    print("  help    - Show this help message")
    print()


def main():
    """Main entry point."""
    print_banner()
    check_env_file()
    
    # Get command from arguments
    command = sys.argv[1] if len(sys.argv) > 1 else "dev"
    
    if command == "dev":
        run_dev()
    elif command == "prod":
        run_prod()
    elif command == "test":
        run_test()
    elif command == "help":
        show_help()
    else:
        print(f"❌ Unknown command: {command}")
        print()
        show_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
