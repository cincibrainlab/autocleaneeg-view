# Contributing to AutoClean-View

Thank you for considering contributing to AutoClean-View! Here's how you can help improve this project.

## Development Setup

1. Fork the repository on GitHub

2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/autoclean-view.git
   cd autoclean-view
   ```

3. Create a virtual environment and install in development mode:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

4. Create a branch for your feature:
   ```bash
   git checkout -b feature-name
   ```

## Development Guidelines

- Follow PEP 8 style guidelines for Python code
- Use meaningful variable names and add docstrings to functions
- Write tests for new features or bug fixes
- Keep the codebase focused on the core functionality

## Testing

Run the test suite to ensure your changes don't break existing functionality:

```bash
pytest
```

## Pull Request Process

1. Update documentation if needed
2. Make sure all tests pass
3. Push your changes to your fork
4. Submit a pull request to the main repository

## Code of Conduct

- Be respectful to others
- Focus on constructive feedback
- Maintain the project's scope and goals

## Future Development Areas

- Support for additional EEG file formats
- Adding cleaning/preprocessing capabilities
- Exporting visualizations
- Integration with other EEG analysis tools

Thank you for contributing!