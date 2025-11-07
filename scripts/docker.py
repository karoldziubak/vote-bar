# Docker development commands for vote-bar
# Run with: python scripts/docker.py [command]

import sys
import subprocess

def build_dev():
    """Build development Docker image."""
    print("🐳 Building development Docker image...")
    subprocess.run([
        "docker", "build", 
        "--target", "development",
        "-t", "vote-bar:dev", 
        "."
    ], check=True)

def build_prod():
    """Build production Docker image."""
    print("🐳 Building production Docker image...")
    subprocess.run([
        "docker", "build", 
        "--target", "production",
        "-t", "vote-bar:prod", 
        "."
    ], check=True)

def up():
    """Start the development environment with docker-compose."""
    print("🚀 Starting development environment...")
    subprocess.run(["docker-compose", "up", "-d"], check=True)
    print("✅ Vote-bar is running at http://localhost:8501")

def down():
    """Stop the development environment."""
    print("🛑 Stopping development environment...")
    subprocess.run(["docker-compose", "down"], check=True)

def logs():
    """Show logs from the running container."""
    print("📋 Showing container logs...")
    subprocess.run(["docker-compose", "logs", "-f", "vote-bar"], check=True)

def test():
    """Run tests in Docker container."""
    print("🧪 Running tests in Docker...")
    subprocess.run([
        "docker-compose", "--profile", "testing", 
        "run", "--rm", "test"
    ], check=True)

def lint():
    """Run code quality checks in Docker container."""
    print("🔍 Running code quality checks in Docker...")
    subprocess.run([
        "docker-compose", "--profile", "quality", 
        "run", "--rm", "lint"
    ], check=True)

def shell():
    """Open shell in running container."""
    print("🐚 Opening shell in vote-bar container...")
    subprocess.run([
        "docker-compose", "exec", "vote-bar", "/bin/bash"
    ], check=True)

def main():
    commands = {
        "build-dev": build_dev,
        "build-prod": build_prod,
        "up": up,
        "down": down,
        "logs": logs,
        "test": test,
        "lint": lint,
        "shell": shell,
    }
    
    if len(sys.argv) != 2 or sys.argv[1] not in commands:
        print("Usage: python scripts/docker.py [build-dev|build-prod|up|down|logs|test|lint|shell]")
        print("\nCommands:")
        print("  build-dev   - Build development Docker image")
        print("  build-prod  - Build production Docker image") 
        print("  up          - Start development environment")
        print("  down        - Stop development environment")
        print("  logs        - Show container logs")
        print("  test        - Run tests in container")
        print("  lint        - Run code quality checks")
        print("  shell       - Open shell in container")
        sys.exit(1)
    
    commands[sys.argv[1]]()

if __name__ == "__main__":
    main()