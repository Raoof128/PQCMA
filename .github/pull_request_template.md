# Pull Request

## Description

Provide a clear and concise description of what this PR does.

Fixes # (issue)

## Type of Change

Please select the relevant option:

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Code refactoring
- [ ] Performance improvement
- [ ] Test coverage improvement
- [ ] Dependency update

## Changes Made

List the key changes in this PR:

-
-
-

## Testing

**How has this been tested?**

Describe the tests you ran to verify your changes:

- [ ] Unit tests pass (`pytest tests/`)
- [ ] Integration tests pass (`python test_integration.py`)
- [ ] Basic tests pass (`python test_basic.py`)
- [ ] Manual testing completed
- [ ] Tested on example vulnerable code
- [ ] Tested with PCAP files (if applicable)
- [ ] Tested with certificates (if applicable)

**Test Configuration:**
- Python Version:
- OS:
- Dependencies installed:

## Test Coverage

If adding new code, please confirm:

- [ ] I have added tests that cover my changes
- [ ] All new and existing tests passed
- [ ] Code coverage has been maintained or improved

## Code Quality

- [ ] My code follows the project's style guidelines (PEP 8)
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] My changes generate no new warnings
- [ ] I have added type hints where appropriate

## Documentation

- [ ] I have updated the README.md (if needed)
- [ ] I have updated the CHANGELOG.md
- [ ] I have updated docstrings for public APIs
- [ ] I have updated USAGE_EXAMPLES.md (if adding features)
- [ ] I have added myself to CONTRIBUTORS (optional)

## Algorithm Detection (if applicable)

If adding/modifying algorithm detection:

- [ ] Updated `analysis/rules.py` with new patterns
- [ ] Added test cases to verify detection
- [ ] Updated documentation with supported algorithms
- [ ] Tested for false positives
- [ ] Tested with real-world code samples

**Algorithms affected:**
-

## Breaking Changes

If this PR includes breaking changes, describe:

**What breaks:**


**Migration path:**


**Deprecation warnings added:**
- [ ] Yes
- [ ] No
- [ ] N/A

## Dependencies

Does this PR add, update, or remove dependencies?

- [ ] No dependency changes
- [ ] Added new dependency: ____________
- [ ] Updated dependency: ____________
- [ ] Removed dependency: ____________

If yes, explain why and confirm:
- [ ] Dependency is necessary and well-maintained
- [ ] Updated `pyproject.toml` and `requirements.txt`
- [ ] Tested with new dependency versions
- [ ] Optional dependency (not required for core functionality)

## Performance Impact

- [ ] No performance impact
- [ ] Performance improved
- [ ] Performance degraded (explain below)

If performance is affected, provide benchmarks:

```
Before:
After:
```

## Screenshots (if applicable)

Add screenshots showing the changes, especially for output format changes.

## Security Considerations

- [ ] This PR does not introduce security vulnerabilities
- [ ] I have considered input validation
- [ ] I have considered path traversal risks
- [ ] I have considered injection vulnerabilities
- [ ] Code handles untrusted input safely

If security-relevant, explain:


## Australian Government/Defence Context (if applicable)

If this PR affects ASD-related features:

- [ ] Changes align with current ASD guidance
- [ ] Updated ASD references to latest versions
- [ ] Considered classification/handling requirements
- [ ] Updated compliance documentation

## Additional Notes

Add any additional notes, concerns, or questions for reviewers:


## Checklist

Before submitting this PR, please ensure:

- [ ] I have read the [CONTRIBUTING.md](../CONTRIBUTING.md) guide
- [ ] My branch is up to date with the main branch
- [ ] All commits have clear, descriptive messages
- [ ] I have tested my changes thoroughly
- [ ] I have updated relevant documentation
- [ ] I am willing to address review feedback

## Reviewer Notes

Leave notes for reviewers about areas that need special attention:


---

**Thank you for contributing to PQC Migration Auditor!** 🔐
