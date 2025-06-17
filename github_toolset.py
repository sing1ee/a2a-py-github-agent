import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from github import Github, Auth
from google.adk.tools import Tool
from pydantic import BaseModel, Field


class GitHubUser(BaseModel):
    """GitHub user information"""
    login: str
    name: Optional[str] = None
    email: Optional[str] = None


class GitHubRepository(BaseModel):
    """GitHub repository information"""
    name: str
    full_name: str
    description: Optional[str] = None
    url: str
    updated_at: str
    pushed_at: str
    language: Optional[str] = None
    stars: int
    forks: int
    
    
class GitHubCommit(BaseModel):
    """GitHub commit information"""
    sha: str
    message: str
    author: str
    date: str
    url: str


class GitHubToolset:
    """GitHub API toolset for querying repositories and recent updates"""
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self._github_client = None
        
        # Initialize tools
        self.get_user_repos = Tool(
            name="get_user_repositories",
            description="Get user's repositories with recent updates",
            parameters={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "GitHub username (optional, defaults to authenticated user)"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days to look back for updates (default: 30)",
                        "default": 30
                    },
                    "limit": {
                        "type": "integer", 
                        "description": "Maximum number of repositories to return (default: 10)",
                        "default": 10
                    }
                }
            },
            func=self._get_user_repositories
        )
        
        self.get_recent_commits = Tool(
            name="get_recent_commits",
            description="Get recent commits for a repository",
            parameters={
                "type": "object",
                "properties": {
                    "repo_name": {
                        "type": "string",
                        "description": "Repository name in format 'owner/repo'"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days to look back for commits (default: 7)",
                        "default": 7
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of commits to return (default: 10)", 
                        "default": 10
                    }
                },
                "required": ["repo_name"]
            },
            func=self._get_recent_commits
        )
        
        self.search_repositories = Tool(
            name="search_repositories",
            description="Search for repositories with recent activity",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for repositories"
                    },
                    "sort": {
                        "type": "string",
                        "description": "Sort results by: 'updated', 'stars', 'forks' (default: 'updated')",
                        "default": "updated"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of repositories to return (default: 10)",
                        "default": 10
                    }
                },
                "required": ["query"]
            },
            func=self._search_repositories
        )
    
    def _get_github_client(self, access_token: Optional[str] = None) -> Github:
        """Get GitHub client with authentication"""
        if access_token:
            auth = Auth.Token(access_token)
        else:
            # Use environment variable as fallback
            github_token = os.getenv('GITHUB_TOKEN')
            if github_token:
                auth = Auth.Token(github_token)
            else:
                # Use without authentication (limited rate)
                auth = None
        
        return Github(auth=auth)
    
    def _get_user_repositories(self, username: Optional[str] = None, days: int = 30, limit: int = 10, **kwargs) -> List[Dict[str, Any]]:
        """Get user's repositories with recent updates"""
        try:
            access_token = kwargs.get('access_token')
            github = self._get_github_client(access_token)
            
            if username:
                user = github.get_user(username)
            else:
                user = github.get_user()
            
            repos = []
            cutoff_date = datetime.now() - timedelta(days=days)
            
            for repo in user.get_repos(sort='updated', direction='desc'):
                if len(repos) >= limit:
                    break
                    
                if repo.updated_at >= cutoff_date:
                    repos.append({
                        'name': repo.name,
                        'full_name': repo.full_name,
                        'description': repo.description,
                        'url': repo.html_url,
                        'updated_at': repo.updated_at.isoformat(),
                        'pushed_at': repo.pushed_at.isoformat() if repo.pushed_at else None,
                        'language': repo.language,
                        'stars': repo.stargazers_count,
                        'forks': repo.forks_count
                    })
            
            return repos
        except Exception as e:
            return [{'error': f'Failed to get repositories: {str(e)}'}]
    
    def _get_recent_commits(self, repo_name: str, days: int = 7, limit: int = 10, **kwargs) -> List[Dict[str, Any]]:
        """Get recent commits for a repository"""
        try:
            access_token = kwargs.get('access_token')
            github = self._get_github_client(access_token)
            
            repo = github.get_repo(repo_name)
            commits = []
            cutoff_date = datetime.now() - timedelta(days=days)
            
            for commit in repo.get_commits(since=cutoff_date):
                if len(commits) >= limit:
                    break
                    
                commits.append({
                    'sha': commit.sha[:8],
                    'message': commit.commit.message.split('\n')[0],  # First line only
                    'author': commit.commit.author.name,
                    'date': commit.commit.author.date.isoformat(),
                    'url': commit.html_url
                })
            
            return commits
        except Exception as e:
            return [{'error': f'Failed to get commits: {str(e)}'}]
    
    def _search_repositories(self, query: str, sort: str = 'updated', limit: int = 10, **kwargs) -> List[Dict[str, Any]]:
        """Search for repositories with recent activity"""
        try:
            access_token = kwargs.get('access_token')
            github = self._get_github_client(access_token)
            
            # Add recent activity filter to query
            search_query = f"{query} pushed:>={datetime.now() - timedelta(days=30):%Y-%m-%d}"
            
            repos = []
            results = github.search_repositories(query=search_query, sort=sort, order='desc')
            
            for repo in results[:limit]:
                repos.append({
                    'name': repo.name,
                    'full_name': repo.full_name,
                    'description': repo.description,
                    'url': repo.html_url,
                    'updated_at': repo.updated_at.isoformat(),
                    'pushed_at': repo.pushed_at.isoformat() if repo.pushed_at else None,
                    'language': repo.language,
                    'stars': repo.stargazers_count,
                    'forks': repo.forks_count
                })
            
            return repos
        except Exception as e:
            return [{'error': f'Failed to search repositories: {str(e)}'}]
    
    def get_tools(self) -> List[Tool]:
        """Return list of available tools"""
        return [
            self.get_user_repos,
            self.get_recent_commits,
            self.search_repositories
        ] 