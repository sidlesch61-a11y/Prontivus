# Contributing to CliniCore

Thank you for your interest in contributing to CliniCore! This document provides guidelines and instructions for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone <your-fork-url>`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes
6. Commit your changes: `git commit -m "Add your feature"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Create a Pull Request

## Development Setup

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Configure your .env file
alembic upgrade head
```

### Frontend Setup
```bash
cd frontend
npm install
cp .env.local.example .env.local
# Configure your .env.local file
npm run dev
```

## Code Style Guidelines

### Backend (Python)
- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for functions and classes
- Keep functions focused and small
- Use async/await for database operations

### Frontend (TypeScript/React)
- Follow TypeScript best practices
- Use functional components with hooks
- Keep components small and reusable
- Use Tailwind CSS for styling
- Follow shadcn/ui patterns

## Commit Message Guidelines

Format: `type(scope): description`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
- `feat(auth): add user login endpoint`
- `fix(frontend): resolve sidebar navigation bug`
- `docs(readme): update installation instructions`

## Pull Request Guidelines

1. **Title**: Use a clear, descriptive title
2. **Description**: Explain what changes you made and why
3. **Testing**: Describe how you tested your changes
4. **Screenshots**: Include screenshots for UI changes
5. **Breaking Changes**: Clearly mark any breaking changes

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Code Review Process

1. All PRs require at least one review
2. Address review comments
3. Keep PRs focused and reasonably sized
4. Ensure CI/CD checks pass

## Reporting Issues

When reporting issues, please include:
- Clear description of the problem
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details (OS, browser, versions)
- Screenshots or error logs if applicable

## Feature Requests

We welcome feature requests! Please:
- Check if the feature already exists or is planned
- Provide a clear use case
- Explain the expected behavior
- Consider implementation complexity

## Questions?

Feel free to:
- Open a discussion in the repository
- Ask questions in pull requests
- Reach out to maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to CliniCore! 🎉

