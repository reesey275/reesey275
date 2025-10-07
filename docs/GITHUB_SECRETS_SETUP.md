# GitHub Actions Secrets Setup

This document explains how to configure the required secrets for the Codex workflows to run successfully.

## Required Secrets

### OPENAI_API_KEY

The Codex workflows require an OpenAI API key to authenticate with the OpenAI API.

**To set up the OPENAI_API_KEY secret:**

1. Go to your GitHub repository settings
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Set the following values:
   - **Name**: `OPENAI_API_KEY`
   - **Secret**: Your OpenAI API key (starts with `sk-`)
5. Click **Add secret**

**To obtain an OpenAI API key:**

1. Visit [OpenAI API Platform](https://platform.openai.com/api-keys)
2. Sign in to your OpenAI account
3. Click **Create new secret key**
4. Copy the generated key (it starts with `sk-`)
5. Store it securely - you won't be able to see it again

## Workflow Dependencies

The following workflows require the `OPENAI_API_KEY` secret:

- **Update Profile with Codex** (`.github/workflows/codex-profile-update.yml`)
- **Deploy Pages with Codex** (`.github/workflows/deploy-pages.yml`)

## Security Notes

- Never commit API keys directly to your repository
- Use GitHub Secrets to store sensitive information
- API keys should be treated as passwords and kept confidential
- Consider setting up API usage limits in your OpenAI account to prevent unexpected charges

## Troubleshooting

If you see `401 Unauthorized` errors in the workflow logs:

1. Verify the `OPENAI_API_KEY` secret is set in repository settings
2. Check that the API key is valid and active in your OpenAI account
3. Ensure your OpenAI account has sufficient credits/quota
4. Verify the API key has access to the required models (e.g., gpt-4, gpt-3.5-turbo)

## Testing

After setting up the secret, you can test the workflow by:

1. Making a small change to any file in the `projects/` directory
2. Committing and pushing the change
3. Checking the **Actions** tab in your repository to see if the workflow runs successfully
