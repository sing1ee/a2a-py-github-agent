# GitHub Agent with ADK

This example shows how to create an A2A Server that uses an ADK-based Agent for querying GitHub repositories and recent project updates.

## Prerequisites

- Python 3.10 or higher
- [UV](https://docs.astral.sh/uv/)
- A OpenRouter API Key
- A [GitHub Personal Access Token](https://github.com/settings/tokens) (optional, but recommended for higher rate limits)

## Running the example

1. Create the .env file with your API Key and GitHub token

   ```bash
   echo "OPENROUTER_API_KEY=your_openrouter_api_key_here" > .env
   echo "GITHUB_TOKEN=your_github_personal_access_token_here" >> .env
   ```

   **Note**: The GitHub token is optional. Without it, the agent will use unauthenticated access with limited rate limits.

2. Run the example

   ```bash
   uv run .
   ```

## Testing the agent

Try running the CLI host at samples/python/hosts/cli to interact with the agent.

```bash
uv run . --agent="http://localhost:10007"
```

## Example queries

The GitHub Agent can handle queries like:

- "Show recent repository updates for username 'octocat'"
- "Get recent commits for repository 'facebook/react'"
- "Search for popular Python repositories with recent activity"
- "What are the latest updates in machine learning repositories?"

## GitHub Token Setup

To create a GitHub Personal Access Token:

1. Go to [GitHub Settings > Tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Select the following scopes:
   - `repo` - Access to repositories
   - `user` - Access to user information
4. Copy the token and add it to your `.env` file