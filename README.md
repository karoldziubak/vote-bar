# vote-bar

Experimental voting system using a drag-and-drop bar interface to express preferences and rankings. Built with Python, Streamlit, Docker, and uv. Designed for flexible preferences testing and open-source research on collective decision-making.

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

## 🎯 How It Works

Vote-bar implements an experimental "100% bar" voting concept with **drag-and-drop positioning**:

### Core Concept
Instead of traditional voting or even percentage sliders, users **position option icons directly on a visual bar**. The position and width of each option on the bar represents its share of the vote.

### Key Features

1. **🎯 Position-Based Voting** - Place options anywhere on a 100% bar using intuitive sliders
2. **📏 Visual Allocation** - The space each option occupies represents its percentage
3. **❌ Zero for Unused** - Options not placed on the bar automatically receive 0%
4. **🚫 No Overlaps** - Smart validation prevents conflicting positions
5. **👁️ Real-time Preview** - See your exact bar configuration as you build it
6. **📊 Live Results** - Aggregated results from all submitted position votes
7. **🔄 Backwards Compatible** - Still supports traditional percentage-based votes

### Example Voting Scenarios

- **Full Allocation**: Position 3 options covering the entire 100% bar
- **Partial Voting**: Only position your top 2 choices, leaving others at 0%
- **Unequal Weighting**: Give your favorite 60%, second choice 25%, third choice 15%
- **Binary Choice**: Position one option for 100%, ignore all others

## 🧪 Project Structure

```
vote-bar/
├── app.py                    # Main drag-and-drop Streamlit application
├── app_slider.py            # Original slider-based app (backup)
├── logic/                    # Core business logic
│   ├── __init__.py          
│   └── vote_logic.py        # VoteBar and PositionVote classes
├── tests/                    # Unit tests (17 tests, 99% coverage)
│   └── test_vote_logic.py   # Comprehensive test suite
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

The project maintains 99% test coverage with 17 comprehensive tests:

```bash
# Run all tests
docker-compose --profile testing run --rm test

# Or locally
uv run pytest -v --cov=logic
```

### Test Coverage
- ✅ Position-based voting logic
- ✅ Traditional percentage voting (backward compatibility)
- ✅ Vote validation (overlaps, ranges, unknown options)
- ✅ Results calculation and aggregation
- ✅ Mixed vote type handling

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

## 🔬 Technical Implementation

### Position-Based Voting Logic

The system converts visual positions to percentages:

```python
# Example: User positions options on bar
positions = {
    "Option A": (0.0, 50.0),    # Start at 0%, end at 50% = 50% allocation
    "Option B": (60.0, 100.0),  # Start at 60%, end at 100% = 40% allocation
    # Option C not positioned = 0% allocation
}
```

### Smart Validation

- **Range checking**: Positions must be 0-100%
- **Overlap detection**: No two options can occupy same space
- **Option validation**: Only known options can be positioned
- **Flexible allocation**: Total can be less than 100% (partial voting)

### Visualization

Real-time bar visualization using Plotly:
- Color-coded option segments
- Percentage labels
- Dynamic resizing
- Responsive design

## 📈 Research Applications

Perfect for studying:

- **Preference intensity** - How much do people really care about each option?
- **Partial participation** - What happens when people only vote for some options?
- **Visual vs. numerical** - Does positioning feel more natural than typing percentages?
- **Decision-making patterns** - How do people distribute their preferences?
- **Collective intelligence** - How do visual votes aggregate differently?

## 🚀 Future Enhancements

- [ ] **True drag-and-drop** - Mouse/touch dragging of option icons
- [ ] **Mobile optimization** - Touch-friendly interface
- [ ] **Data persistence** - Database integration for vote storage
- [ ] **User authentication** - Session management and user tracking
- [ ] **Advanced visualizations** - Heatmaps, distribution plots
- [ ] **Export functionality** - CSV, JSON, PDF reports
- [ ] **API endpoints** - Programmatic access to voting data
- [ ] **Multi-language support** - Internationalization
- [ ] **Real-time collaboration** - Live voting sessions
- [ ] **A/B testing framework** - Compare different voting interfaces

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Ensure code quality checks pass (`uv run python scripts/dev.py lint`)
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Submit a pull request

## 📄 License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.

---

**Ready to experiment with visual voting?** 🎯

```bash
docker-compose up -d
# Visit http://localhost:8501
```