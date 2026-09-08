# Contributing Guide — Project Volusia

> How to contribute to Project Volusia.

---

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR-USERNAME/project-volusia.git`
3. Create a branch: `git checkout -b feature/your-feature`
4. Make changes
5. Commit: `git commit -m "Add your feature"`
6. Push: `git push origin feature/your-feature`
7. Open a Pull Request

---

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 20+ (for frontend)
- Git

### Backend Setup

```bash
cd project-volusia
pip install -r requirements-dev.txt
cd Tools/volusia_data
python portal_app.py
```

### Frontend Setup

```bash
cd volusia-portal
npm install
npm run dev
```

---

## Code Style

### Python

- Follow PEP 8
- Use type hints
- Docstrings for all functions
- Max line length: 100 characters

### TypeScript/React

- Follow ESLint config
- Use functional components
- TypeScript strict mode
- Tailwind CSS for styling

---

## Pull Request Process

1. Update documentation if needed
2. Add tests for new features
3. Ensure all tests pass
4. Request review from maintainers
5. Address review comments
6. Squash commits if requested

---

## Issue Reporting

### Bug Reports

Include:
- Steps to reproduce
- Expected behavior
- Actual behavior
- Screenshots (if applicable)
- Environment info (OS, browser, etc.)

### Feature Requests

Include:
- Problem statement
- Proposed solution
- Alternatives considered
- Additional context

---

## Data Contributions

See [Data Source Contribution](../data-sources/adding-sources.md) for how to add new data sources.

---

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Respect different perspectives

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Last Updated**: 2026-09-08
**Maintainer**: ZQM Labs / ZQM Computing
