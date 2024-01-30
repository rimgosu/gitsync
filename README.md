## 1. overview
- ✅ (24/01/23 수정) 작업 스케쥴러 GUI ➡️ Powershell Script
- <https://github.com/rimgosu/gitsync>
- [https://velog.io/@rimgosu/windows-11-github](https://velog.io/@rimgosu/windows-11-github-%EB%AA%A8%EB%93%A0-repo%EC%99%80-%EC%9E%90%EB%8F%99%EC%9C%BC%EB%A1%9C-%EB%8F%99%EA%B8%B0%ED%99%94%ED%95%98%EA%B8%B0)

```
C:/gits	┬ allclone.py 
		└ runallclone.bat
```

### 사전 준비물
- python 3.10 버전
- git
- windows 10 이상

## 2. python 라이브러리 설치
- GitPython의 설치가 필요하다.
```bash
pip install requests GitPython
```


## 3. 파이썬 코드 작성
- `C:\gits\allclone.py`

```python
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
    if os.path.isdir(repo):
        try:
            print(f"Checking {repo}...")
            git_repo = Repo(repo)

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
                repo
            )
        except GitCommandError as e:
            print(f"Error cloning {repo}: {e}")

token = os.environ.get('GITHUB_TOKEN')
username = "rimgosu"
repos = get_user_repos(username, token)
print(f"{username}의 레포지토리 목록: {repos}")

for repo in repos:
    clone_or_update_repo(username, repo, token)
```

- **아래 username을 자기의 깃허브 닉네임으로 바꿔넣자.**
- private 상태의 레포지토리도 검색하여 모든 레포지토리의 이름을 담아둔다.
- 만약 해당 레포지토리의 폴더가 없으면 clone을, 해당 레포지토리의 폴더가 있으면 다음 명령어를 실행하는 것과 같다.

```bash
git pull origin [main/master]
git add .
git commit -m "$(date)"
git push origin master
```


## 4. 배치파일 작성
- `C:\gits\runallclone.bat`
```bash
cd "C:\gits"
python "C:\gits\allclone.py"
```


## 5. github PAT token 받기

1. github 계정 - Settings - Developer Settings - Personal access tokens (classic) - Generate New Token - 이름 쓰고 repo, workflow 클릭 - Generate new token
2. 받은 토큰 복사 (한 번 보여주고 그 뒤로 보여주지 않으므로 꼭 복사해놓자)


## 6. 윈도우 환경변수 설정
- `cmd`
```shell
setx GITHUB_TOKEN "[5번에서_발급받은_토큰_입력]"
```
- **다시시작** 해야 깃허브 토큰이 제대로 환경 변수로 등록된다.


## 7. 배치파일 직접 실행 or 작업 스케쥴러
- `runallclone.bat`을 더블 클릭하여 실행하면 파이썬 스크립트가 실행되어 모든 깃허브 레포지토리가 동기화 된다.
- 작업 스케쥴러 설정을 해주자. 
- `검색-Windows Powershell(관리자 권한으로 실행)-아래 스크립트 붙여넣기`

```shell
# 매시간 반복 실행될 작업의 액션 설정
$ActionEveryHour = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -Command `"& 'C:\gits\runallclone.bat'`""

# 매시간 반복될 트리거 설정
$TriggerEveryHour = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Hours 1)

# 작업을 실행할 사용자의 주요 설정
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive

# 작업의 추가 설정
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

# 작업 등록
Register-ScheduledTask -TaskName "RunBatchEveryHour" -Action $ActionEveryHour -Trigger $TriggerEveryHour -Principal $Principal -Settings $Settings
```

- TriggerEveryHour의 "New-TimeSpan -Hours 1"부분을 수정하여 원하는 주기로 동기화할 수 있다.
   - ex) 5분 단위로 커밋하고 싶다면 `-Minutes 5`
   - ex) 2시간 단위로 커밋하고 싶다면 `-Hours 2`
   
   
### 작업 스케쥴러 확인
- 확인 : `검색-작업 스케줄러-작업 스케줄러 라이브러리`
- "RunBatchEveryHour"가 다음과 같이 잡히면 성공!

![](https://velog.velcdn.com/images/rimgosu/post/a464039a-c3d1-4cef-ae60-c31d93d6f0d5/image.png)


## 8. 동작 확인
- 다음과 같이 일정 시간마다 내 모든 깃허브 레포지토리와 동기화 하는 것을 볼 수 있다.
- 나는 `c:/gits` 폴더를 기본 동기화 장소로 사용하고, 원하는 레포지토리의 바로가기를 만들어 사용할 예정이다. 

![](https://velog.velcdn.com/images/rimgosu/post/8b9900a4-181a-4dfd-8603-e17530019e3d/image.png)
