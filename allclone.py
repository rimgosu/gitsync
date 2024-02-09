import requests
from git import Repo, GitCommandError
import os
from datetime import datetime

def get_user_repos(username, token):
    all_repos = []
    page = 1
    while True:
        headers = {"Authorization": f"Bearer {token}"}
        url = f"https://api.github.com/search/repositories?q=user:{username}&page={page}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        repos = response.json()["items"]
        if not repos:
            break
        all_repos.extend([repo['name'] for repo in repos])
        page += 1
    return all_repos

def get_default_branch(username, repo, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"https://api.github.com/repos/{username}/{repo}", headers=headers)
    response.raise_for_status()
    repo_data = response.json()
    return repo_data['default_branch']

def clone_or_update_repo(username, repo, token):
    repo_path = os.path.join("..", repo) # 상위 폴더에 레포지토리를 설정
    if os.path.isdir(repo_path):
        try:
            print(f"Checking {repo}...")
            git_repo = Repo(repo_path)

            default_branch = get_default_branch(username, repo, token)

            if 'origin' not in git_repo.remotes:
                git_repo.create_remote('origin', url=f'https://github.com/{username}/{repo}.git')

            git_repo.git.pull('origin', default_branch)
            git_repo.git.add(A=True)
            git_repo.git.commit('-m', datetime.now().strftime("Update on %Y-%m-%d %H:%M:%S"))
            git_repo.git.push('origin', default_branch)
        except GitCommandError as e:
            print(f"Error updating {repo}: {e}")
    else:
        try:
            print(f"Cloning {repo}...")
            Repo.clone_from(
                f"https://x-access-token:{token}@github.com/{username}/{repo}.git",
                repo_path
            )
        except GitCommandError as e:
            print(f"Error cloning {repo}: {e}")

token = os.environ.get('GITHUB_TOKEN')
username = "rimgosu"
repos = get_user_repos(username, token)
print(f"{username}의 레포지토리 목록: {repos}")

for repo in repos:
    clone_or_update_repo(username, repo, token)
