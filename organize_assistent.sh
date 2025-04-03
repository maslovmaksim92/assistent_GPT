# вставь туда код и нажми Ctrl+O, Enter, затем Ctrl+X

#!/bin/bash

echo "🔧 Организация проекта MaksimGPT..."
TARGET_DIR="assistent_examples"

# Создаём папку, если не существует
mkdir -p $TARGET_DIR

# Список файлов для переноса
FILES_TO_MOVE=(
  "calendar.py"
  "chat.py"
  "crm.py"
  "gpt.py"
  "logistic.py"
  "bot_daily_plan.py"
  "finance.py"
)

# Перемещение
for FILE in "${FILES_TO_MOVE[@]}"; do
  if [ -f "$FILE" ]; then
    echo "📦 Перемещаю: $FILE → $TARGET_DIR/"
    mv "$FILE" "$TARGET_DIR/"
  else
    echo "⚠️ Не найден: $FILE"
  fi
done

echo "✅ Готово. Все вспомогательные файлы теперь в $TARGET_DIR/"

