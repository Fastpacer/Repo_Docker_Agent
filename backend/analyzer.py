import os
from collections import defaultdict

def analyze_repo(path):
    """
    Analyze repository to detect tech stacks with definitive fingerprints.
    Uses multi-layered detection: fingerprints > config files > source code counting.
    Returns the primary tech stack and all detected stacks.
    """
    
    # DEFINITIVE FINGERPRINTS - specific file combinations that conclusively identify stacks
    # If ANY of these combos are found, immediately return that stack (no calculation needed)
    fingerprints = {
        "node": [
            ["package.json"],  # package.json alone is 99% Node
            ["package.json", "vite.config.ts"],
            ["package.json", "next.config.js"],
            ["package.json", "webpack.config.js"],
        ],
        "rust": [["Cargo.toml"]],
        "go": [["go.mod"]],
        "java": [["pom.xml"]],
        "csharp": [[".csproj"], [".sln"]],
        "ruby": [["Gemfile"]],
        "php": [["composer.json"]],
    }
    
    # Stack priority order (used for tie-breaking when scores are equal)
    # More specific/modern stacks are prioritized over generic/older ones
    # TypeScript/Node frameworks come before generic Python
    STACK_PRIORITY = [
        "rust", "go", "java", "csharp", "ruby", "php", "node", "python",
        "static", "dockerized"
    ]
    
    # Define tech stack indicators with file signatures
    # Primary indicators are definitive markers (weight: 100)
    # Secondary indicators are supporting signals (weight: 10)
    # Tertiary indicators add extra confidence (weight: 5)
    tech_indicators = {
        "rust": {
            "primary": ["Cargo.toml"],
            "secondary": ["Cargo.lock"],
            "tertiary": []
        },
        "go": {
            "primary": ["go.mod"],
            "secondary": ["go.sum"],
            "tertiary": []
        },
        "java": {
            "primary": ["pom.xml"],
            "secondary": ["build.gradle", "build.gradle.kts", "gradlew"],
            "tertiary": []
        },
        "csharp": {
            "primary": [".csproj", ".sln"],
            "secondary": [".fsproj"],
            "tertiary": []
        },
        "ruby": {
            "primary": ["Gemfile"],
            "secondary": ["Rakefile", ".gemspec"],
            "tertiary": []
        },
        "php": {
            "primary": ["composer.json"],
            "secondary": ["composer.lock"],
            "tertiary": []
        },
        "python": {
            "primary": ["requirements.txt", "pyproject.toml"],
            "secondary": ["setup.py", "Pipfile", "poetry.lock"],
            "tertiary": ["setup.cfg", "tox.ini", "pytest.ini"]
        },
        "node": {
            "primary": ["package.json"],
            "secondary": ["yarn.lock", "pnpm-lock.yaml", "npm-shrinkwrap.json", "package-lock.json"],
            "tertiary": [".npmrc", ".eslintrc.json", "next.config.js", "webpack.config.js", "tsconfig.json"]
        },
        "static": {
            "primary": ["index.html"],
            "secondary": ["style.css"],
            "tertiary": []
        },
        "dockerized": {
            "primary": ["Dockerfile"],
            "secondary": ["docker-compose.yml"],
            "tertiary": [".dockerignore"]
        },
    }
    
    # Source file extensions - STRONG SIGNAL
    source_extensions = {
        "rust": [".rs"],
        "go": [".go"],
        "java": [".java"],
        "csharp": [".cs", ".fs"],
        "ruby": [".rb"],
        "php": [".php"],
        "python": [".py"],
        "node": [".ts", ".tsx", ".js", ".jsx", ".mjs", ".vue"],
        "static": [".html"],
    }
    
    detected_stacks = defaultdict(int)
    source_file_counts = defaultdict(int)
    files_in_repo = set()
    
    # Scan repository for tech indicators and source files
    for root, dirs, files in os.walk(path):
        # Skip common non-essential directories to speed up scan
        dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '.venv', 'venv', '__pycache__', 'dist', 'build', '.next', '.nuxt', 'build_files']]
        
        for f in files:
            files_in_repo.add(f)
            
            # Count source files
            for stack, extensions in source_extensions.items():
                for ext in extensions:
                    if f.endswith(ext):
                        source_file_counts[stack] += 1
    
    # STEP 1: Check definitive fingerprints FIRST - if found, return immediately
    # This handles obvious cases like package.json
    for stack, fingerprint_combos in fingerprints.items():
        for combo in fingerprint_combos:
            if all(fname in files_in_repo for fname in combo):
                return {
                    "repo_type": stack,
                    "detected_stacks": {stack: 1000},
                    "source_file_counts": dict(source_file_counts),
                    "files": list(files_in_repo)[:50],
                    "detection_method": "fingerprint"
                }
    
    # STEP 2: Check config files (if no fingerprint matched)
    for stack, indicators in tech_indicators.items():
        # Primary indicators: 100 points each
        for indicator in indicators.get("primary", []):
            if indicator in files_in_repo or any(f.endswith(indicator) for f in files_in_repo if indicator.startswith(".")):
                detected_stacks[stack] += 100
        
        # Secondary indicators: 10 points each
        for indicator in indicators.get("secondary", []):
            if indicator in files_in_repo or any(f.endswith(indicator) for f in files_in_repo if indicator.startswith(".")):
                detected_stacks[stack] += 10
        
        # Tertiary indicators: 5 points each
        for indicator in indicators.get("tertiary", []):
            if indicator in files_in_repo or any(f.endswith(indicator) for f in files_in_repo if indicator.startswith(".")):
                detected_stacks[stack] += 5
    
    # STEP 3: Add source file counts (weight: 15 per file to dominate config signals)
    for stack, count in source_file_counts.items():
        if count > 0:
            detected_stacks[stack] += (count * 15)
    
    # Select primary stack
    primary_stack = "unknown"
    if detected_stacks:
        max_score = max(detected_stacks.values())
        tied_stacks = [s for s, score in detected_stacks.items() if score == max_score]
        
        # Break ties using priority order
        for stack in STACK_PRIORITY:
            if stack in tied_stacks:
                primary_stack = stack
                break
        
        if primary_stack == "unknown" and tied_stacks:
            primary_stack = tied_stacks[0]
    
    return {
        "repo_type": primary_stack,
        "detected_stacks": dict(detected_stacks),
        "source_file_counts": dict(source_file_counts),
        "files": list(files_in_repo)[:50],
        "detection_method": "scoring"
    }