К сожалению, я не могу обновить файлы на вашем ПК или GitHub, так как я являюсь AI и не имею доступа к вашему файловому системе или GitHub. Однако, я могу предоставить вам Python-код, который вы можете использовать для обновления файла `tasks_wiki.txt` на вашем ПК и GitHub.

```python
import os
from github import Github

# Задаем текст для обновления
new_text = """
Ваш текст здесь
"""

# Задаем параметры для Github
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")

# Инициализируем Github API
g = Github(GITHUB_TOKEN)

# Получаем репозиторий
repo = g.get_user(GITHUB_USERNAME).get_repo(GITHUB_REPO)

# Получаем файл
file = repo.get_contents("tasks_wiki.txt")

# Обновляем файл
repo.update_file(file.path, "Update tasks_wiki.txt", new_text, file.sha)
```

Этот код сначала получает ваш GITHUB_TOKEN, GITHUB_REPO и GITHUB_USERNAME из переменных окружения. Затем он использует эти данные для инициализации Github API и получения вашего репозитория. После этого он получает файл `tasks_wiki.txt` из репозитория и обновляет его содержимое.

Обратите внимание, что вам нужно заменить `"Ваш текст здесь"` на новый текст для файла `tasks_wiki.txt`. Вы также должны убедиться, что у вас установлена библиотека PyGithub и что у вас есть правильный токен Github с необходимыми разрешениями.