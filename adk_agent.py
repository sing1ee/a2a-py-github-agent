import datetime
import os
from google.adk.agents import LlmAgent  # type: ignore[import-untyped]
from google.adk.models.lite_llm import LiteLlm
from github_toolset import GitHubToolset  # type: ignore[import-untyped]

openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

model = LiteLlm(
    model="openrouter/anthropic/claude-3.5-sonnet",
    api_key=openrouter_api_key,
    base_url="https://openrouter.ai/api/v1",
)


def create_agent() -> LlmAgent:
    """Constructs the ADK agent."""
    toolset = GitHubToolset()
    return LlmAgent(
        model=model,
        name="github_agent",
        description="An agent that can help query GitHub repositories and recent project updates",
        instruction=f"""
You are a GitHub agent that can help users query information about GitHub repositories and recent project updates.

Users will request information about:
- Recent updates to their repositories
- Recent commits in specific repositories  
- Search for repositories with recent activity
- General GitHub project information

Use the provided tools for interacting with the GitHub API.

When displaying repository information, include relevant details like:
- Repository name and description
- Last updated time
- Programming language
- Stars and forks count
- Recent commit information when available

Today is {datetime.datetime.now()}.
""",
        tools=[toolset],
    )
