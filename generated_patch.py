Сначала давайте создадим Python скрипт, который будет считывать и обновлять файл `tasks_wiki.txt`. Для этого нам понадобится библиотека `os` для работы с операционной системой и `github` для взаимодействия с GitHub.

```python
import os
from github import Github

# Используем токен GitHub для аутентификации
g = Github(os.getenv("GITHUB_TOKEN"))

# Получаем репозиторий
repo = g.get_repo(os.getenv("GITHUB_REPO"))

# Получаем файл tasks_wiki.txt
file = repo.get_contents("tasks_wiki.txt")

# Считываем содержимое файла
content = file.decoded_content.decode()

# Добавляем новую задачу в конец файла
content += "\n\n### 14. 🧠 Новая задача\n- Описание новой задачи"

# Обновляем файл на GitHub
repo.update_file("tasks_wiki.txt", "Update tasks_wiki.txt", content, file.sha)

# Обновляем файл на ПК
with open("tasks_wiki.txt", "w") as f:
    f.write(content)

print("Файл tasks_wiki.txt успешно обновлен.")
```

Этот код сначала получает доступ к вашему репозиторию на GitHub с помощью вашего токена GitHub. Затем он считывает содержимое файла `tasks_wiki.txt`, добавляет новую задачу в конец файла и обновляет файл на GitHub и на вашем ПК.