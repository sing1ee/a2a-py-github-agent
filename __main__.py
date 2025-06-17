import logging
import os

import click
import uvicorn
from adk_agent import create_agent  # type: ignore[import-not-found]
from adk_agent_executor import ADKAgentExecutor  # type: ignore[import-untyped]
from dotenv import load_dotenv
from google.adk.artifacts import (
    InMemoryArtifactService,  # type: ignore[import-untyped]
)
from google.adk.memory.in_memory_memory_service import (
    InMemoryMemoryService,  # type: ignore[import-untyped]
)
from google.adk.runners import Runner  # type: ignore[import-untyped]
from google.adk.sessions import (
    InMemorySessionService,  # type: ignore[import-untyped]
)
from starlette.applications import Starlette

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)


load_dotenv()

logging.basicConfig()


@click.command()
@click.option('--host', 'host', default='localhost')
@click.option('--port', 'port', default=10007)
def main(host: str, port: int):
    # Verify an API key is set.
    if not os.getenv('OPENROUTER_API_KEY'):
        raise ValueError(
            'OPENROUTER_API_KEY environment variable not set'
        )

    skill = AgentSkill(
        id='github_repositories',
        name='GitHub Repositories',
        description="Query GitHub repositories, recent updates, commits, and project activity",
        tags=['github', 'repositories', 'commits'],
        examples=[
            'Show my recent repository updates',
            'What are the latest commits in my project?',
            'Search for popular Python repositories with recent activity'
        ],
    )

    # Simplified AgentCard without authentication requirements
    agent_card = AgentCard(
        name='GitHub Agent',
        description="An agent that can query GitHub repositories and recent project updates",
        url=f'http://{host}:{port}/',
        version='1.0.0',
        defaultInputModes=['text'],
        defaultOutputModes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
    )

    # Create agent without OAuth credentials
    adk_agent = create_agent()
    runner = Runner(
        app_name=agent_card.name,
        agent=adk_agent,
        artifact_service=InMemoryArtifactService(),
        session_service=InMemorySessionService(),
        memory_service=InMemoryMemoryService(),
    )
    agent_executor = ADKAgentExecutor(runner, agent_card)

    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor, task_store=InMemoryTaskStore()
    )

    a2a_app = A2AStarletteApplication(
        agent_card=agent_card, http_handler=request_handler
    )
    routes = a2a_app.routes()
    
    app = Starlette(routes=routes)

    uvicorn.run(app, host=host, port=port)


if __name__ == '__main__':
    main()