# === Правки импортов и структуры проекта ===

# Обновление импорта generate_code_from_task в wiki_task_updater.py
sed -i 's/from code_writer import generate_code_from_task/from assistent_GPT.code_writer import write_code/' wiki_task_updater.py

# Обновление импорта deploy_code в wiki_task_updater.py
sed -i 's/from deployer import deploy_code/from assistent_GPT.deployer import deploy/' wiki_task_updater.py

# Обновление импорта в web_ui.py
sed -i 's/from code_writer import generate_code_from_task/from assistent_GPT.code_writer import write_code/' assistent_GPT/web_ui.py
sed -i 's/from deployer import deploy_code/from assistent_GPT.deployer import deploy/' assistent_GPT/web_ui.py

# Обновление импорта в self_editor.py
sed -i 's/from code_writer import generate_code_from_task/from assistent_GPT.code_writer import write_code/' assistent_GPT/self_editor.py
sed -i 's/from deployer import deploy_code/from assistent_GPT.deployer import deploy/' assistent_GPT/self_editor.py

# Гарантируем, что __init__.py есть для импорта как модуля
touch assistent_GPT/__init__.py

echo "✅ Импорты и структура обновлены. Теперь можешь запускать python3 wiki_task_updater.py"