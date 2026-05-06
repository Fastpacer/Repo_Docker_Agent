import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Tech stack specific Docker templates and context
STACK_TEMPLATES = {
    "rust": {
        "dockerfile_base": "FROM rust:latest",
        "build_stage": "RUN cargo build --release",
        "runtime": "COPY --from=builder /app/target/release /app",
        "context": "Rust project with Cargo.toml. Use multi-stage build for optimization."
    },
    "go": {
        "dockerfile_base": "FROM golang:1.21-alpine",
        "build_stage": "RUN go build -o app .",
        "runtime": "FROM alpine:latest\nCOPY --from=builder /app/app /app/app",
        "context": "Go project with go.mod. Use Alpine for minimal image size."
    },
    "java": {
        "dockerfile_base": "FROM maven:3.9-eclipse-temurin-21",
        "build_stage": "RUN mvn clean package",
        "runtime": "FROM eclipse-temurin:21-jre\nCOPY --from=builder /app/target/*.jar /app/app.jar",
        "context": "Java project using Maven or Gradle. Use multi-stage build to reduce image size."
    },
    "csharp": {
        "dockerfile_base": "FROM mcr.microsoft.com/dotnet/sdk:8.0",
        "build_stage": "RUN dotnet build && dotnet publish -c Release",
        "runtime": "FROM mcr.microsoft.com/dotnet/runtime:8.0\nCOPY --from=builder /app/bin/Release/net8.0/publish .",
        "context": ".NET Core application. Use multi-stage builds with separate SDK and runtime stages."
    },
    "python": {
        "dockerfile_base": "FROM python:3.11-slim",
        "build_stage": "RUN pip install --no-cache-dir -r requirements.txt",
        "runtime": "COPY . /app",
        "context": "Python application with requirements.txt. Use slim image for efficiency."
    },
    "node": {
        "dockerfile_base": "FROM node:20-alpine",
        "build_stage": "RUN npm install && npm run build",
        "runtime": "COPY . /app",
        "context": "Node.js application with package.json. Use Alpine for smaller image footprint."
    },
    "ruby": {
        "dockerfile_base": "FROM ruby:3.3-alpine",
        "build_stage": "RUN bundle install",
        "runtime": "COPY . /app",
        "context": "Ruby application with Gemfile. Use Alpine for minimal image size."
    },
    "php": {
        "dockerfile_base": "FROM php:8.2-fpm-alpine",
        "build_stage": "RUN composer install",
        "runtime": "COPY . /app",
        "context": "PHP application with composer.json. Pair with nginx in docker-compose."
    },
    "static": {
        "dockerfile_base": "FROM nginx:alpine",
        "build_stage": "",
        "runtime": "COPY . /usr/share/nginx/html",
        "context": "Static website. Use nginx for efficient serving."
    }
}

def generate_compose(repo_info):
    """
    Generate docker-compose.yml tailored to the detected tech stack.
    Uses stack-specific knowledge to create appropriate configurations.
    """
    repo_type = repo_info["repo_type"]
    detected_stacks = repo_info.get("detected_stacks", {})
    
    # Build context about detected stacks
    stack_context = ""
    if detected_stacks:
        stack_context = f"Detected stacks: {', '.join([f'{k} (confidence: {v})' for k, v in sorted(detected_stacks.items(), key=lambda x: x[1], reverse=True)])}\n"
    
    # Get template context for the primary stack
    template_info = STACK_TEMPLATES.get(repo_type, STACK_TEMPLATES["python"])
    
    prompt = f"""
You are an expert Docker configuration generator. Generate a production-ready docker-compose.yml file.

Primary detected tech stack: {repo_type}
{stack_context}

Context about this stack: {template_info['context']}

For a {repo_type} application, ensure:
- Appropriate base image for the language/framework
- Correct build and runtime dependencies
- Best practices for image optimization
- Proper service configuration in docker-compose
- Health checks where applicable
- Port mappings suitable for {repo_type} applications
- Environment variable handling
- Volume mounts for development if applicable

Output ONLY valid docker-compose.yml (version 3 or higher) with no additional text.
Do NOT include Dockerfile content - only docker-compose.yml.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": "You are a Docker expert. Generate only valid docker-compose.yml files. Output YAML only, no explanations."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content

def generate_dockerfile(repo_info):
    """
    Generate a Dockerfile tailored to the detected tech stack.
    Returns tech-specific Dockerfile with multi-stage builds where appropriate.
    """
    repo_type = repo_info["repo_type"]
    template_info = STACK_TEMPLATES.get(repo_type, STACK_TEMPLATES["python"])
    
    prompt = f"""
You are an expert Docker configuration generator. Generate a production-ready Dockerfile.

Tech stack: {repo_type}
Context: {template_info['context']}

Requirements:
- Use multi-stage builds for compiled languages (Rust, Go, Java, C#)
- Minimize final image size
- Use appropriate Alpine/slim images when possible
- Include health checks
- Set proper working directory
- Expose relevant ports
- Handle dependencies installation
- Include proper error handling

Base image hint: {template_info['dockerfile_base']}

Output ONLY valid Dockerfile with no additional text or explanations.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": "You are a Docker expert. Generate only valid Dockerfiles. Output Dockerfile content only, no explanations."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content