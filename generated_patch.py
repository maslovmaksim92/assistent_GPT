Ваш запрос содержит множество задач и информации, которые вы хотите реализовать, но я не уверен, что вы просите меня сгенерировать код для конкретной задачи. Могли бы вы уточнить, для какой задачи вам нужен код?

Тем не менее, для обновления файла `tasks_wiki.txt` на GitHub и на ПК, вы можете использовать следующий пример кода:

```python
import os
import git

def update_github_file(file_path, commit_msg, repo_dir='.'):
    repo = git.Repo(repo_dir)
    repo.git.add(file_path)
    repo.git.commit('-m', commit_msg)
    repo.git.push()

def update_local_file(file_path, new_content):
    with open(file_path, 'w') as f:
        f.write(new_content)

if __name__ == "__main__":
    file_path = "tasks_wiki.txt"
    commit_msg = "Updated tasks_wiki.txt with new tasks"
    new_content = "<ваше обновленное содержимое файла>"
    
    update_local_file(file_path, new_content)
    update_github_file(file_path, commit_msg)
```

Этот код сначала обновляет локальную версию файла `tasks_wiki.txt`, а затем обновляет версию файла на GitHub. Пожалуйста, замените `<ваше обновленное содержимое файла>` на ваше реальное обновленное содержимое.

Помните, что для работы этого кода на вашем компьютере должны быть установлены Git и библиотека GitPython (`pip install gitpython`). Кроме того, вы должны быть авторизованы в Git на вашем компьютере, чтобы иметь возможность отправлять коммиты и пуши в ваш репозиторий.