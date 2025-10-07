# Codex Configuration Guide

This document explains how Codex is configured in this repository for both local development and CI/CD automation.

## Overview

We use OpenAI's Codex CLI for automated code generation and documentation
updates. The configuration is designed to work seamlessly in both local
development and GitHub Actions environments.

## Configuration Files

### `.codex/config.toml`
Main configuration file that defines:
- Default models and providers
- Approval policies for different environments
- Sandbox settings for security
- Environment variable handling
- Multiple profiles for different use cases

## Profiles

### CI Profile (`--profile ci`)
Optimized for automated GitHub Actions workflows:
- **Model**: `gpt-4o-mini` (confirmed compatible with standard OpenAI API)
- **Approval Policy**: `never` (no interactive prompts)
- **Sandbox**: `workspace-write` (can modify files in the repository)
- **Reasoning**: `medium` (balanced performance/quality)

### Local Profile (`--profile local`)
For interactive development:
- **Model**: `gpt-4o` (higher capability when available)
- **Approval Policy**: `on-request` (prompts for confirmation)
- **Sandbox**: `workspace-write` (safe local development)
- **Reasoning**: `high` (maximum quality for complex tasks)

## Authentication

### Local Development
Configure your OpenAI API key in your shell environment:

```bash
export OPENAI_API_KEY="sk-proj-your-key-here"
```

### GitHub Actions
The workflow uses GitHub Secrets to securely store the API key:
- Secret name: `OPENAI_API_KEY`
- Configure via: Repository Settings → Secrets and variables → Actions

## Model Selection

### Why gpt-4o-mini for CI?
Through testing, we determined that:
- `gpt-5-codex` requires specialized endpoints not available in standard chat completions
- `gpt-4o-mini` provides excellent code generation with standard API compatibility
- Reliable performance in automated environments
- Cost-effective for CI/CD usage

### Available Models
See `docs/OPENAI_MODELS.md` for comprehensive model reference including:
- Token limits and rate limits
- Model capabilities and use cases
- Compatibility notes

## Agents

### profile_writer
Located at `.codex/agent_profile_writer.md`
- **Purpose**: Updates project README files based on Git history and metadata
- **Scope**: Portfolio-wide documentation maintenance
- **Role**: Technical writer with DevOps focus
- **Triggers**: Changes to `projects/**` or `.codex/**` paths

## Workflow Integration

### GitHub Actions Workflows

#### Profile Update Workflow
File: `.github/workflows/codex-profile-update.yml`

**Implementation:**
- Uses official `openai/codex-action@v1` from OpenAI
- Provides better security and reliability than custom scripts
- Handles Codex CLI installation and configuration automatically

**Triggers:**
- Push to `projects/**` paths (project updates)
- Push to `.codex/**` paths (agent configuration changes)
- Manual dispatch for testing

**Process:**
1. Checkout repository
2. Run Codex using official GitHub Action with inline prompt
3. Commit and push any generated changes

#### Auto-Fix Workflow
File: `.github/workflows/codex-autofix.yml`

**Implementation:**
- Automatically responds to CI failures with targeted fixes
- Uses `workflow_run` trigger to monitor other workflows
- Creates pull requests for review rather than direct commits

**Triggers:**
- When `Lint` workflow fails
- When `Update Profile with Codex` workflow fails
- Runs on workflow completion with failure status

**Process:**
1. Checkout the failing commit
2. Run Codex with context about the failure
3. Verify the fix by running the same checks that failed
4. Create a pull request with the proposed fix

### Error Handling
The workflow includes robust error handling:
- API authentication failures are logged but don't fail the build
- Network timeouts are handled gracefully
- Invalid responses are caught and reported

## Local Usage

### Running Agents

```bash
# Direct codex execution (recommended for local development)
npx codex exec "Update README files for all projects" --profile local

# Using our custom script (legacy, still functional)
./scripts/run_codex_agent.sh profile_writer --profile local

# Interactive mode for development
npx codex
```

### Testing Configuration

```bash
# Verify codex installation
npx codex --version

# Test API connectivity
npx codex exec "echo 'Configuration test'" --profile ci
```

## Troubleshooting

### Common Issues
1. **401 Unauthorized**: Check API key configuration and model compatibility
2. **Model not found**: Verify model availability in your OpenAI account
3. **Timeout errors**: Check network connectivity and API rate limits

### Debugging Steps
1. Verify API key is set: `echo ${#OPENAI_API_KEY}` should show ~164 characters
2. Test with simple command: `npx codex exec "echo hello"`
3. Check logs in `logs/` directory for detailed error information

### Getting Help
- Codex CLI documentation: https://github.com/openai/codex
- OpenAI API documentation: https://platform.openai.com/docs
- Repository issues: Use GitHub Issues for project-specific problems

## Security Considerations

### API Key Management
- Never commit API keys to version control
- Use GitHub Secrets for CI/CD environments
- Rotate keys regularly following security best practices

### Sandbox Settings
- `workspace-write`: Allows file modifications within repository only
- Network access is controlled by approval policies
- Commands are logged for audit trails

### Environment Variables
Only essential variables are forwarded to Codex:
- `PATH`, `HOME`: Basic shell functionality
- `OPENAI_API_KEY`: API authentication
- `GITHUB_*`: Repository context for CI

## Performance Optimization

### Optimal Model Usage
- Use `gpt-4o-mini` for most tasks (fast, cost-effective)
- Reserve `gpt-4o` for complex reasoning tasks
- Avoid `gpt-5-codex` unless using specialized endpoints

### Rate Limiting
### Model Selection for Performance
Monitor usage against OpenAI limits:
- `gpt-4o-mini`: 200,000 TPM, 500 RPM
- Configure retry logic for rate limit handling
- Consider batch processing for multiple operations

## GitHub Action Benefits

### Security Features
- **Privilege Management**: Runs with `drop-sudo` by default
- **Sandbox Control**: `workspace-write` mode for safe file operations
- **API Key Protection**: Secure proxy to OpenAI Responses API
- **No Network Access**: Codex cannot access external networks during execution

### Reliability Improvements
- **Official Support**: Maintained by OpenAI team
- **Automatic Installation**: Handles Codex CLI setup
- **Error Handling**: Built-in retry logic and failure reporting
- **Version Control**: Pinned to stable releases

## Future Enhancements

### Planned Improvements
- Additional agents for different project types
- Enhanced error recovery and retry logic
- Integration with other development tools
- Custom model fine-tuning for repository-specific tasks

### Migration to Official Action
We've transitioned from a custom script to the official `openai/codex-action`:
- **Better Security**: Official action includes privilege management
- **Improved Reliability**: Maintained by OpenAI with proper error handling
- **Simplified Configuration**: Direct prompt specification in workflow
- **Legacy Support**: Custom script remains available for local development

### Configuration Updates
As new models and features become available:
- Update GitHub Action model parameter
- Test compatibility in CI environment
- Document changes and migration steps
