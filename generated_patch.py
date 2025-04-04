Сначала давайте напишем Python-скрипт, который считывает содержимое файла `tasks_wiki.txt`, добавляет новую задачу в конец и сохраняет обновленный файл. Затем мы можем использовать GitHub API для обновления файла `tasks_wiki.txt` на GitHub.

```python
import os
from github import Github

# Определите свои переменные окружения
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_REPO = os.getenv('GITHUB_REPO')
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME')

# Инициализируйте объект Github с помощью токена
g = Github(GITHUB_TOKEN)

# Получите репозиторий
repo = g.get_user().get_repo(GITHUB_REPO)

# Откройте файл tasks_wiki.txt и прочитайте его содержимое
with open('tasks_wiki.txt', 'r') as file:
    content = file.read()

# Добавьте новую задачу в конец
content += "\n\n### 14. 🧠 Новая задача\n- Описание новой задачи"

# Обновите файл tasks_wiki.txt с новым содержимым
with open('tasks_wiki.txt', 'w') as file:
    file.write(content)

# Получите содержимое файла tasks_wiki.txt в репозитории
file = repo.get_contents("tasks_wiki.txt", ref="master")

# Обновите файл tasks_wiki.txt на GitHub
repo.update_file(file.path, "Update tasks_wiki.txt", content, file.sha, branch="master")
```

Примечание: Для работы с GitHub API вам нужно установить библиотеку PyGithub. Если у вас ее нет, вы можете установить ее, запустив `pip install PyGithub` в командной строке.