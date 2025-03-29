# Contributing to G4Flow Repository

Thank you for considering contributing to the G4Flow repository! This repository is maintained by [kqlio67](https://github.com/kqlio67). This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Pull Requests](#pull-requests)
- [Development Setup](#development-setup)
- [Repository Structure](#repository-structure)
- [Style Guide](#style-guide)
  - [Code Style](#code-style)
  - [Commit Messages](#commit-messages)
- [Documentation](#documentation)
- [Testing](#testing)
- [Review Process](#review-process)
- [Issue Labels](#issue-labels)
- [Security Vulnerabilities](#security-vulnerabilities)
- [License](#license)
- [Communication Channels](#communication-channels)
- [Questions?](#questions)

## Code of Conduct

By participating in this repository, you agree to abide by our Code of Conduct. We expect all contributors to be respectful and considerate of others. This includes:

- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the repository and community
- Showing empathy towards other community members

Harassment and other exclusionary behavior are not acceptable. If you witness or experience any unacceptable behavior, please report it to the repository maintainer.

## Getting Started

Before you begin:

1. Ensure you have a [GitHub account](https://github.com/signup)
2. Familiarize yourself with the repository by reading the [README.md](README.md)
3. Check the existing [issues](https://github.com/kqlio67/g4flow/issues) to see if your bug or feature has already been reported

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with the following information:

1. A clear, descriptive title
2. A detailed description of the issue
3. Steps to reproduce the bug
4. Expected behavior
5. Screenshots (if applicable)
6. Your environment (OS, browser, Python version, etc.)
7. Any relevant logs or error messages

### Suggesting Enhancements

We welcome suggestions for enhancements! Please create an issue with:

1. A clear, descriptive title
2. A detailed description of the proposed enhancement
3. Any relevant examples or mockups
4. An explanation of why this enhancement would be useful to users of this repository

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature-name`)
3. Make your changes
4. Run tests if available
5. Commit your changes (see [Commit Messages](#commit-messages) below)
6. Push to the branch (`git push origin feature/your-feature-name`)
7. Open a Pull Request

#### Pull Request Guidelines

- Follow the existing code style
- Include comments in your code where necessary
- Update documentation if needed
- Add tests if applicable
- Ensure your code passes any existing tests
- Link to any related issues using the GitHub issue number (e.g., "Fixes #123")
- Provide a clear description of the changes
- Include screenshots or GIFs for UI changes

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/kqlio67/g4flow.git
   cd g4flow
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   streamlit run app.py
   ```

## Repository Structure

```
g4flow/
├── app.py                  # Main Streamlit application code
├── requirements.txt        # Repository dependencies
├── .gitignore             # Git ignore file
├── LICENSE                # MIT License
├── CONTRIBUTING.md        # Guidelines for contributors
└── README.md             # Repository documentation
```

When contributing, please maintain this structure and follow the existing patterns in the codebase.

## Style Guide

### Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines for Python code
- Use meaningful variable and function names
- Write clear, concise comments
- Keep functions small and focused on a single task
- Use docstrings for functions and classes
- Maintain consistent indentation (4 spaces, not tabs)
- Limit line length to 88 characters (compatible with Black formatter)

### Commit Messages

Good commit messages help others understand the changes you've made. Please follow these guidelines:

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests after the first line
- Consider using a structure like:
  - `feat:` for new features
  - `fix:` for bug fixes
  - `docs:` for documentation changes
  - `style:` for formatting changes
  - `refactor:` for code refactoring
  - `test:` for adding tests
  - `chore:` for maintenance tasks

Example: `feat: Add image analysis capability for Claude models`

## Documentation

Good documentation is crucial for the repository's usability. When contributing:

- Update the README.md if you're adding, removing, or changing features
- Document new functions, classes, and modules with docstrings
- Update any relevant comments in the code
- For significant changes, consider updating or creating wiki pages if applicable

## Testing

While the repository may not have formal tests yet, please manually test your changes thoroughly before submitting a pull request. Consider:

- Testing with different AI models
- Testing with various inputs (text, images)
- Testing edge cases and error handling
- Testing on different browsers and devices (for UI changes)

## Review Process

After you submit a pull request:

1. The maintainers will review your changes
2. They may suggest improvements or changes
3. Once approved, your changes will be merged into the main branch
4. Your contribution will be acknowledged in the repository

Please be patient during the review process and be open to feedback.

## Issue Labels

Issues are categorized with labels to help organize and prioritize work:

- `bug`: Something isn't working as expected
- `enhancement`: New feature or request
- `documentation`: Improvements to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `question`: Further information is requested

## Security Vulnerabilities

If you discover a security vulnerability, please do NOT open an issue. Instead, email the repository maintainer directly. Security issues will be addressed with the highest priority.

## License

By contributing to this repository, you agree that your contributions will be licensed under the repository's [MIT License](LICENSE).

## Communication Channels

For quick questions or discussions, you can:

- Open a [GitHub Discussion](https://github.com/kqlio67/g4flow/discussions) (if enabled)
- Comment on relevant issues
- Reach out to the maintainer directly for sensitive matters

## Questions?

If you have any questions about contributing, please open an issue with your question.

Thank you for your contributions!
