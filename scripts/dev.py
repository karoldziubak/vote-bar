# Development scripts for vote-bar project
# Run with: uv run scripts/dev.py [command]

import sys
import subprocess

def run_tests():
    """Run pytest with coverage."""
    print("🧪 Running tests with coverage...")
    subprocess.run(["uv", "run", "pytest"], check=True)

def run_app():
    """Start the Streamlit application."""
    print("🚀 Starting Streamlit app...")
    subprocess.run(["uv", "run", "streamlit", "run", "app.py"], check=True)

def format_code():
    """Format code with black and isort."""
    print("🎨 Formatting code with black...")
    subprocess.run(["uv", "run", "black", "."], check=True)
    print("📦 Organizing imports with isort...")
    subprocess.run(["uv", "run", "isort", "."], check=True)

def lint_code():
    """Lint code with flake8 and mypy."""
    print("🔍 Linting with flake8...")
    subprocess.run(["uv", "run", "flake8", "."], check=True)
    print("🔬 Type checking with mypy...")
    subprocess.run(["uv", "run", "mypy", "logic/", "app.py"], check=True)

def main():
    commands = {
        "test": run_tests,
        "app": run_app,
        "format": format_code,
        "lint": lint_code,
    }
    
    if len(sys.argv) != 2 or sys.argv[1] not in commands:
        print("Usage: uv run scripts/dev.py [test|app|format|lint]")
        sys.exit(1)
    
    commands[sys.argv[1]]()

if __name__ == "__main__":
    main()