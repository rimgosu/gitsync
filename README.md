# git-synchronize

## 1. overview
- <https://github.com/rimgosu/git-synchronize>
```
┬ allclone.py 
└ runallclone.bat
```

### 사전 준비물
- python 3.10 버전
- git
- windows 10 이상

## 2. python 라이브러리 설치
- GitPython의 설치가 필요하다.
```
pip install requests GitPython
```


## 3. 파이썬 코드 작성
- `allclone.py`

```
import requests
from git import Repo, GitCommandError
import os
from datetime import datetime

def get_user_repos(username, token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"https://api.github.com/search/repositories?q=user:{username}", headers=headers)
        response.raise_for_status()
        repos = response.json()["items"]
        return [repo['name'] for repo in repos]
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

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
username = "[깃허브 사용자 닉네임 입력]"
# ex ) username = "rimgosu"
repos = get_user_repos(username, token)
print(f"{username}의 레포지토리 목록: {repos}")

for repo in repos:
    clone_or_update_repo(username, repo, token)
```

- 아래 username을 자기의 깃허브 닉네임으로 바꿔넣자.
- private 상태의 레포지토리도 검색하여 모든 레포지토리의 이름을 담아둔다.
- 만약 해당 레포지토리의 폴더가 없으면 clone을, 해당 레포지토리의 폴더가 있으면 다음 명령어를 실행한다.

```bash
git pull origin [main/master]
git add .
git commit -m "$(date)"
git push origin master
```


## 4. 배치파일 작성
- `runallclone.bat`
```
python [경로를 입력하세요]/allclone.py
pause
```

- 만약 실행된 내역을 보고싶지 않다면 pause를 삭제할 것.


## 5. github PAT token 받기

1. github 계정 - Settings - Developer Settings - Personal access tokens (classic) - Generate New Token - 이름 쓰고 repo, workflow 클릭 - Generate new token
2. 받은 토큰 복사 (한 번 보여주고 그 뒤로 보여주지 않으므로 꼭 복사해놓자)


## 6. 윈도우 환경변수 설정
- `cmd`
```
setx GITHUB_TOKEN "[5번에서_발급받은_토큰_입력]"
```
- **다시시작** 해야 깃허브 토큰이 제대로 환경 변수로 등록된다.


## 7. 배치파일 직접 실행 or 작업 스케쥴러
- `runallclone.bat`을 더블 클릭하여 실행하면 파이썬 스크립트가 실행되어 모든 깃허브 레포지토리가 동기화 된다.
- 만약 xx분 마다 깃허브와 로컬의 저장소를 동기화시키고 싶다면 작업 스케쥴러를 사용하자. 
- 리눅스는 crontab 쓰면 되니 더 간단하게 될 것이다. bat 파일을 sh로 바꾸고 실행해보자.
- `검색 - 작업 스케쥴러` 실행 후 다음과 같이 설정하자.
   
![](https://velog.velcdn.com/images/rimgosu/post/b4dd2802-5e58-4532-92ec-cb049f6f0fea/image.png)

![](https://velog.velcdn.com/images/rimgosu/post/1282b99f-ebde-4c81-b0e0-6efc61b08fd6/image.png)

- 트리거
![](https://velog.velcdn.com/images/rimgosu/post/9a628f18-e723-4260-aad9-32c712262687/image.png)

- 동작 
   - **시작위치, 배치파일 위치 나눠서 작성한다.**

![](https://velog.velcdn.com/images/rimgosu/post/2882834b-e9bf-4f34-8b1f-d3faca41c256/image.png)

- 조건

![](https://velog.velcdn.com/images/rimgosu/post/b8fded2b-1193-4169-8cd6-a5b27b205be9/image.png)

- 설정

![](https://velog.velcdn.com/images/rimgosu/post/05ef3723-a227-495c-8b8c-ba240b0fd500/image.png)

- **다시 시작**하거나 만든 스케쥴러를 선택 - `실행` 버튼을 누르면 자동으로 원격 저장소와 sync를 맞추게 된다.

## 8. 동작 확인
- 다음과 같이 일정 시간마다 내 모든 깃허브 레포지토리와 동기화 하는 것을 볼 수 있다.
- 나는 `c:/gits` 폴더를 기본 동기화 장소로 사용하고, 원하는 레포지토리의 바로가기를 만들어 사용할 예정이다. 

![](https://velog.velcdn.com/images/rimgosu/post/8b9900a4-181a-4dfd-8603-e17530019e3d/image.png)
