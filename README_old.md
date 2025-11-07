# vote-bar

# vote-bar

Experimental voting system using a bar to express preferences and rankings. Built with Python, Streamlit, Docker, and uv. Designed for flexible preferences testing and open-source research on collective decision-making.

## 🚀 Quick Start

### Prerequisites

- **Docker Desktop** - [Install Docker Desktop](https://www.docker.com/products/docker-desktop/)
- **Git** - For cloning the repository

### Running with Docker (Recommended)

1. **Clone and navigate to the repository:**
   ```bash
   git clone https://github.com/karoldziubak/vote-bar.git
   cd vote-bar
   ```

2. **Start the development environment:**
   ```bash
   docker-compose up -d
   ```

3. **Open your browser and visit:**
   ```
   http://localhost:8501
   ```

4. **View logs (optional):**
   ```bash
   docker-compose logs -f vote-bar
   ```

5. **Stop the environment when done:**
   ```bash
   docker-compose down
   ```

### Development Commands

We provide convenient scripts for common development tasks:

```bash
# Using Docker helper script
python scripts/docker.py up          # Start development environment
python scripts/docker.py down        # Stop environment
python scripts/docker.py logs        # View logs
python scripts/docker.py test        # Run tests in container
python scripts/docker.py lint        # Run code quality checks
python scripts/docker.py shell       # Open shell in container

# Direct docker-compose commands
docker-compose up -d                  # Start in background
docker-compose down                   # Stop all services
docker-compose logs -f vote-bar       # Follow logs
docker-compose exec vote-bar bash     # Shell into container
```

## 🛠️ Local Development (Advanced)

If you prefer to run without Docker, you'll need Python 3.11+ and `uv`:

### Setup

1. **Install uv (Python package manager):**
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Run the application:**
   ```bash
   uv run streamlit run app.py
   ```

4. **Run tests:**
   ```bash
   uv run pytest
   ```

### Development Scripts

```bash
# Run tests with coverage
uv run python scripts/dev.py test

# Start Streamlit app
uv run python scripts/dev.py app

# Format code
uv run python scripts/dev.py format

# Lint code
uv run python scripts/dev.py lint
```

## 📊 How It Works

Vote-bar implements an experimental "100% bar" voting concept:

1. **Distribute 100%** - Users allocate percentages across multiple options
2. **Flexible preferences** - Unlike traditional voting, express nuanced preferences
3. **Real-time results** - See aggregated results with visualizations
4. **Research-focused** - Designed for testing collective decision-making approaches

## 🧪 Project Structure

```
vote-bar/
├── app.py                    # Main Streamlit application
├── logic/                    # Core business logic
│   ├── __init__.py          
│   └── vote_logic.py        # VoteBar class and voting logic
├── tests/                    # Unit tests
│   └── test_vote_logic.py   # Test suite with 100% coverage
├── data/                     # Data files (empty initially)
├── scripts/                  # Development helper scripts
│   ├── dev.py               # Local development commands
│   └── docker.py            # Docker development commands
├── pyproject.toml           # Project dependencies and configuration
├── Dockerfile               # Multi-stage Docker build
├── docker-compose.yml       # Development environment setup
└── README.md               # This file
```

## 🐳 Docker Configuration

### Multi-stage Build

- **Base stage** - Python 3.11 with uv package manager
- **Dependencies stage** - Cached dependency installation
- **Development stage** - Includes dev dependencies and hot reload
- **Production stage** - Minimal image without dev dependencies

### Development Features

- **Live reload** - Code changes automatically refresh the app
- **Volume mounting** - Source code mounted for development
- **Health checks** - Automatic container health monitoring
- **Port mapping** - Access at `localhost:8501`

### Production Ready

- **Security** - Non-root user, minimal attack surface
- **Optimization** - Compiled bytecode, efficient caching
- **Health monitoring** - Built-in health checks
- **CORS protection** - Security headers enabled

## 🧪 Testing

The project maintains 100% test coverage:

```bash
# Run all tests
docker-compose --profile testing run --rm test

# Or locally
uv run pytest -v --cov=logic
```

## 🔧 Code Quality

Automated code quality checks:

```bash
# Run all quality checks
docker-compose --profile quality run --rm lint

# Or individually
uv run black .           # Code formatting
uv run isort .           # Import sorting  
uv run flake8 .          # Linting
uv run mypy logic/ app.py # Type checking
```

## 📈 Future Enhancements

- [ ] Data persistence with database integration
- [ ] User authentication and session management
- [ ] Advanced visualization options
- [ ] Export results to various formats
- [ ] API endpoints for programmatic access
- [ ] Multi-language support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure code quality checks pass
5. Submit a pull request

## 📄 License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.

## 🚀 Quick Start

### Prerequisites

- **Docker Desktop** - [Install Docker Desktop](https://www.docker.com/products/docker-desktop/)
- **Git** - For cloning the repository

### Running with Docker (Recommended)

1. **Clone and navigate to the repository:**
   ```bash
   git clone https://github.com/karoldziubak/vote-bar.git
   cd vote-bar
   ```

2. **Start the development environment:**
   ```bash
   docker-compose up -d
   ```

3. **Open your browser and visit:**
   ```
   http://localhost:8501
   ```

4. **View logs (optional):**
   ```bash
   docker-compose logs -f vote-bar
   ```

5. **Stop the environment when done:**
   ```bash
   docker-compose down
   ```

### Development Commands

We provide convenient scripts for common development tasks:

```bash
# Using Docker helper script
python scripts/docker.py up          # Start development environment
python scripts/docker.py down        # Stop environment
python scripts/docker.py logs        # View logs
python scripts/docker.py test        # Run tests in container
python scripts/docker.py lint        # Run code quality checks
python scripts/docker.py shell       # Open shell in container

# Direct docker-compose commands
docker-compose up -d                  # Start in background
docker-compose down                   # Stop all services
docker-compose logs -f vote-bar       # Follow logs
docker-compose exec vote-bar bash     # Shell into container
```

## 🛠️ Local Development (Advanced)

If you prefer to run without Docker, you'll need Python 3.11+ and `uv`:

### Setup

1. **Install uv (Python package manager):**
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Run the application:**
   ```bash
   uv run streamlit run app.py
   ```

4. **Run tests:**
   ```bash
   uv run pytest
   ```

### Development Scripts

```bash
# Run tests with coverage
uv run python scripts/dev.py test

# Start Streamlit app
uv run python scripts/dev.py app

# Format code
uv run python scripts/dev.py format

# Lint code
uv run python scripts/dev.py lint
```

## 📊 How It Works

Vote-bar implements an experimental "100% bar" voting concept:

1. **Distribute 100%** - Users allocate percentages across multiple options
2. **Flexible preferences** - Unlike traditional voting, express nuanced preferences
3. **Real-time results** - See aggregated results with visualizations
4. **Research-focused** - Designed for testing collective decision-making approaches

## 🧪 Project Structure

```
vote-bar/
├── app.py                    # Main Streamlit application
├── logic/                    # Core business logic
│   ├── __init__.py          
│   └── vote_logic.py        # VoteBar class and voting logic
├── tests/                    # Unit tests
│   └── test_vote_logic.py   # Test suite with 100% coverage
├── data/                     # Data files (empty initially)
├── scripts/                  # Development helper scripts
│   ├── dev.py               # Local development commands
│   └── docker.py            # Docker development commands
├── pyproject.toml           # Project dependencies and configuration
├── Dockerfile               # Multi-stage Docker build
├── docker-compose.yml       # Development environment setup
└── README.md               # This file
```

## 🐳 Docker Configuration

### Multi-stage Build

- **Base stage** - Python 3.11 with uv package manager
- **Dependencies stage** - Cached dependency installation
- **Development stage** - Includes dev dependencies and hot reload
- **Production stage** - Minimal image without dev dependencies

### Development Features

- **Live reload** - Code changes automatically refresh the app
- **Volume mounting** - Source code mounted for development
- **Health checks** - Automatic container health monitoring
- **Port mapping** - Access at `localhost:8501`

### Production Ready

- **Security** - Non-root user, minimal attack surface
- **Optimization** - Compiled bytecode, efficient caching
- **Health monitoring** - Built-in health checks
- **CORS protection** - Security headers enabled

## 🧪 Testing

The project maintains 100% test coverage:

```bash
# Run all tests
docker-compose --profile testing run --rm test

# Or locally
uv run pytest -v --cov=logic
```

## 🔧 Code Quality

Automated code quality checks:

```bash
# Run all quality checks
docker-compose --profile quality run --rm lint

# Or individually
uv run black .           # Code formatting
uv run isort .           # Import sorting  
uv run flake8 .          # Linting
uv run mypy logic/ app.py # Type checking
```

## 📈 Future Enhancements

- [ ] Data persistence with database integration
- [ ] User authentication and session management
- [ ] Advanced visualization options
- [ ] Export results to various formats
- [ ] API endpoints for programmatic access
- [ ] Multi-language support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure code quality checks pass
5. Submit a pull request

## 📄 License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.
