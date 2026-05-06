import os
from git import Repo

def clone_repo(repo_url, clone_path="repo"):

    if os.path.exists(clone_path):
        return clone_path

    Repo.clone_from(repo_url, clone_path)

    return clone_path


def build_tree(path):

    tree = ""

    for root, dirs, files in os.walk(path):

        level = root.replace(path, "").count(os.sep)
        indent = "  " * level

        tree += f"{indent}📁 {os.path.basename(root)}\n"

        for f in files:
            tree += f"{indent}  📄 {f}\n"

    return tree