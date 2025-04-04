Для выполнения этой задачи необходимо написать скрипт на Python, который считывает файл `tasks_wiki.txt`, производит необходимые обновления и загружает обновленный файл на GitHub и на ПК. 

Вот пример такого скрипта:

```python
import os
from github import Github

# используйте свой персональный токен GitHub для аутентификации
g = Github(os.getenv("GITHUB_TOKEN"))

# получите репозиторий GitHub
repo = g.get_repo(os.getenv("GITHUB_REPO"))

# откройте файл `tasks_wiki.txt` для чтения
with open('tasks_wiki.txt', 'r') as file:
    content = file.read()

# обновите содержимое файла
updated_content = content + "\n\n# New task added by MaksimGPT"

# получите файл `tasks_wiki.txt` из репозитория
file = repo.get_contents("tasks_wiki.txt")

# обновите файл `tasks_wiki.txt` в репозитории
repo.update_file(file.path, "update tasks_wiki.txt", updated_content, file.sha)

# сохраните обновленный файл `tasks_wiki.txt` на ПК
with open('tasks_wiki.txt', 'w') as file:
    file.write(updated_content)

print("tasks_wiki.txt has been updated on GitHub and PC.")
```

Этот скрипт сначала считывает содержимое файла `tasks_wiki.txt`, затем добавляет новую строку к содержимому файла. Затем он загружает обновленное содержимое файла в репозиторий GitHub и сохраняет обновленное содержимое файла на ПК.

Обратите внимание, что для работы этого скрипта необходимо установить библиотеку PyGithub (`pip install PyGithub`) и иметь доступ к персональному токену GitHub и названию репозитория через переменные окружения.