# Contributing to PTSandbox Python Client

Thank you for your interest in contributing to PTSandbox Python Client! We welcome contributions from the community.

## 🤝 Code of Conduct

This project follows a [Code of Conduct](CODE_OF_CONDUCT.md). Please be respectful in all interactions.

## 📝 Issue Templates

When creating issues, please use the appropriate templates:
- [Bug Report Template](https://github.com/Security-Experts-Community/py-ptsandbox/issues/new?template=form_for_bugs.yml) - for reporting bugs
- [Feature Request Template](https://github.com/Security-Experts-Community/py-ptsandbox/issues/new?template=form_for_features.yml) - for suggesting new features

### Bug Reports

Found a bug? Please help us improve by reporting it:

1. **Check [existing issues](https://github.com/Security-Experts-Community/py-ptsandbox/issues)** first to avoid duplicates
2. **Use the [Bug Report Template](https://github.com/Security-Experts-Community/py-ptsandbox/issues/new?template=form_for_bugs.yml)** and include:
   - Python version and OS
   - PTSandbox client version  
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages (if any)

### Feature Requests

Have an idea for a new feature?

1. **Check [existing issues](https://github.com/Security-Experts-Community/py-ptsandbox/issues)** to see if it's already requested
2. **Use the [Feature Request Template](https://github.com/Security-Experts-Community/py-ptsandbox/issues/new?template=form_for_features.yml)** and describe:
   - The problem you're trying to solve
   - Your proposed solution
   - Why it would be useful for other users

## 🔧 Development Setup

### Prerequisites
- Python 3.11+
- Git

### Setup
```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/py-ptsandbox.git
cd py-ptsandbox

# Install uv (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync --all-groups

# Install pre-commit hooks
uv run pre-commit install
```

### Code Style

This project follows **PEP8** coding standards. Please ensure your code adheres to PEP8 guidelines:

```bash
# Format code according to PEP8
uv run ruff format ptsandbox/

# Check code style and linting
uv run ruff check ptsandbox/

# Type checking
uv run mypy ptsandbox/
```

## 📝 Submitting Changes

### Pull Request Process

1. **Fork** the repository on GitHub
2. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** following these guidelines:
   - Follow PEP8 coding standards
   - Update documentation if needed
   - Include type hints
4. **Ensure code quality** by running linting and type checking
5. **Commit** with a clear message:
   ```bash
   git commit -m "feat: add new scanning feature"
   ```
6. **Push** to your fork and create a pull request

### Commit Message Format
- `feat:` new feature
- `fix:` bug fix  
- `docs:` documentation changes
- `test:` adding tests
- `refactor:` code refactoring

### Code Requirements
- **PEP8 compliance** for code style
- **Type hints** for all functions
- **Docstrings** for public APIs
- **Async/await** for I/O operations

## 📚 Documentation

To build and serve documentation locally:
```bash
uv sync --group docs
uv run mkdocs serve
```

## Getting Help

Need assistance or have questions?

- **[Issues](https://github.com/Security-Experts-Community/py-ptsandbox/issues)**: For bugs, feature requests, development questions, and general discussion

Feel free to create an issue if you need help with development, have questions about the codebase, or want to contribute but aren't sure where to start!

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🎉 