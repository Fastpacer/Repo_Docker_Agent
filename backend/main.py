from fastapi import FastAPI

from backend.utils import clone_repo, build_tree
from backend.analyzer import analyze_repo
from backend.agent import generate_compose, generate_dockerfile

app = FastAPI()


@app.get("/analyze")
def analyze(repo_url: str, include_dockerfile: bool = True):
    """
    Analyze a repository and generate appropriate Docker configurations.
    
    Args:
        repo_url: GitHub repository URL
        include_dockerfile: Whether to generate both Dockerfile and docker-compose (default: True)
    
    Returns:
        Repository analysis with detected tech stacks and Docker configurations
    """
    
    try:

        repo_path = clone_repo(repo_url)

        tree = build_tree(repo_path)

        repo_info = analyze_repo(repo_path)

        compose_output = generate_compose(repo_info)
        
        dockerfile_output = ""
        if include_dockerfile:
            dockerfile_output = generate_dockerfile(repo_info)

        return {
            "tree": tree,
            "repo_info": repo_info,
            "docker_compose": compose_output,
            "dockerfile": dockerfile_output,
            "primary_stack": repo_info["repo_type"],
            "detected_stacks": repo_info.get("detected_stacks", {})
        }

    except Exception as e:

        return {
            "error": str(e)
        }