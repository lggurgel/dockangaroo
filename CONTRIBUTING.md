# Contributing to Bitcoin Puzzle Solver

Thank you for your interest in contributing! This project welcomes contributions from the community.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your system info (OS, CPU, RAM, Docker version)
- Relevant log output

### Suggesting Enhancements

Have an optimization idea? Open an issue with:
- Clear description of the enhancement
- Why it would be useful
- Performance impact (if applicable)
- Implementation suggestions (optional)

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**
4. **Test thoroughly**: Verify your changes work correctly
5. **Document your changes**: Update README.md if needed
6. **Commit**: `git commit -m "Add: descriptive message"`
7. **Push**: `git push origin feature/your-feature-name`
8. **Open a Pull Request**: Describe what your changes do

## Development Guidelines

### Code Style

- **Python**: Follow PEP 8
- **Comments**: Explain complex logic
- **Type hints**: Use where appropriate
- **Error handling**: Handle edge cases gracefully

### Testing

Before submitting a PR:
- Test with small puzzles (e.g., Puzzle 40) to verify correctness
- Check Docker builds successfully: `docker-compose build`
- Verify workers start correctly: `docker-compose up -d`
- Monitor for errors: `docker-compose logs`

### Performance Improvements

If your PR improves performance:
- Provide before/after benchmarks
- Explain the optimization technique
- Document any tradeoffs (memory vs speed, etc.)

## Areas for Contribution

We especially welcome contributions in:

- **GPU Optimization**: CUDA kernel improvements
- **Algorithm Enhancements**: Better DP strategies, work distribution
- **Monitoring**: Better dashboards, statistics, visualizations
- **Multi-Machine**: Coordination across multiple machines/cloud
- **Documentation**: Tutorials, guides, examples
- **Testing**: Validation against known puzzles

## Questions?

Open an issue for questions or discussion!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

