# Contributing to PQC Migration Auditor

First off, thank you for considering contributing to the PQC Migration Auditor! It's people like you that make this tool valuable for the cybersecurity community.

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** (code snippets, commands, file samples)
- **Describe the behavior you observed and what you expected**
- **Include screenshots** if relevant
- **Note your environment** (OS, Python version, dependency versions)

#### Bug Report Template

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Run command '...'
2. Scan directory '...'
3. See error

**Expected behavior**
What you expected to happen.

**Environment:**
 - OS: [e.g. Ubuntu 22.04]
 - Python version: [e.g. 3.11.2]
 - Tool version: [e.g. 1.0.1]

**Additional context**
Any other relevant information.
```

### Suggesting Enhancements

Enhancement suggestions are welcome! Please provide:

- **Clear use case**: Explain the problem you're trying to solve
- **Proposed solution**: Describe how you envision the enhancement
- **Alternatives considered**: What other approaches did you think about?
- **Impact**: Who benefits and how?

### Contributing Code

#### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/PQCMA.git
   cd PQCMA
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev,all]"
   ```

4. **Install pre-commit hooks** (if available)
   ```bash
   pre-commit install
   ```

#### Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clear, concise code
   - Follow PEP 8 style guidelines
   - Add type hints where appropriate
   - Include docstrings for public APIs

3. **Write tests**
   - Add unit tests for new functionality
   - Ensure existing tests pass
   - Aim for >80% code coverage

4. **Run tests locally**
   ```bash
   pytest tests/ -v
   python test_basic.py
   python test_integration.py
   ```

5. **Update documentation**
   - Update README.md if adding features
   - Update CHANGELOG.md following [Keep a Changelog](https://keepachangelog.com/)
   - Add docstrings and comments

6. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new PQC algorithm detection"
   ```

   **Commit Message Guidelines:**
   - Use conventional commits format: `type: description`
   - Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
   - Keep first line under 72 characters
   - Add detailed description if needed

7. **Push and create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

#### Pull Request Process

1. **Ensure all tests pass**
2. **Update documentation** as needed
3. **Add yourself to CONTRIBUTORS** if you'd like
4. **Fill out the PR template** completely
5. **Link related issues** using keywords (fixes #123, closes #456)
6. **Request review** from maintainers
7. **Address review comments** promptly

#### Code Style Guidelines

- **Follow PEP 8** for Python code style
- **Use type hints** for function signatures
- **Write descriptive variable names** (no single letters except loop counters)
- **Keep functions focused** (single responsibility)
- **Add comments** for complex logic
- **Maximum line length**: 100 characters (flexible for readability)

#### Testing Guidelines

- **Write tests for all new code**
- **Test edge cases** and error conditions
- **Use descriptive test names**: `test_scanner_detects_rsa_2048_bit_keys()`
- **Use fixtures** for reusable test data
- **Mock external dependencies** (file system, network)

### Adding New Algorithm Detection

If you're adding support for detecting a new cryptographic algorithm:

1. **Update `analysis/rules.py`**
   - Add algorithm to `VULNERABLE_ALGORITHMS` or `PQC_ALGORITHMS`
   - Add detection patterns to `CODE_PATTERNS`
   - Add PQC recommendation in `get_pqc_recommendation()`

2. **Update tests**
   - Add test cases in `tests/test_rules.py`
   - Add example code to `examples/dummy_repo/`
   - Verify detection in integration tests

3. **Update documentation**
   - Add to README.md algorithm list
   - Update CHANGELOG.md

### Adding New Programming Language Support

To add detection patterns for a new programming language:

1. **Update `utils/file_utils.py`**
   - Add file extensions to `text_extensions`

2. **Update `analysis/rules.py`**
   - Add language-specific patterns to `CODE_PATTERNS`

3. **Create test file**
   - Add example vulnerable code in that language to `examples/`

4. **Test thoroughly**
   - Ensure patterns don't cause false positives
   - Test with real-world code samples

## Project Structure

```
PQCMA/
├── pqc_migration_auditor/    # Main package
│   ├── scanner/              # Detection modules
│   ├── analysis/             # Rules and recommendations
│   ├── reporting/            # Output formats
│   └── utils/                # Helper functions
├── tests/                    # Test suite
├── examples/                 # Example vulnerable code
├── docs/                     # Additional documentation
└── .github/                  # GitHub-specific files
```

## Community

- **Questions?** Open a GitHub Discussion
- **Security issues?** See [SECURITY.md](SECURITY.md)
- **Want to chat?** Open an issue with the "question" label

## Recognition

Contributors will be recognized in:
- README.md (Contributors section)
- Release notes
- CONTRIBUTORS.md file

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Australian Government & Defence Contributions

If you're contributing on behalf of Australian government agencies or defence organizations:

- Ensure contributions align with current ASD guidance
- Reference specific policy documents where applicable
- Note any classification or handling requirements
- Follow your organization's open source contribution policies

## Questions?

Don't hesitate to ask questions! The maintainers are here to help. Open an issue with the "question" label or start a GitHub Discussion.

---

**Thank you for contributing to making the post-quantum future more secure!** 🔐🇦🇺
