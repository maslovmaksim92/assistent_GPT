# bots/bot_daily_plan.py

import os
import datetime
import requests
import openai

from app.db import db, DailyPlan, DailyTask

# Инициализируем глобальный ключ для OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# URLs из .env
BITRIX_MESSAGE_ADD_URL = os.getenv("BITRIX_MESSAGE_ADD_URL")
BITRIX_TASK_LIST_URL = os.getenv("BITRIX_TASK_LIST_URL")  # пример: "https://vas-dom.bitrix24.ru/rest/1/xyz/tasks.task.list"

def schedule_daily_plan(user_id: int):
    """
    Функция для автоматического формирования плана дня (по желанию).
    """
    carry_over_incomplete_tasks(user_id)

    today_str = datetime.date.today().isoformat()
    plan = DailyPlan.query.filter_by(user_id=user_id, date=today_str).first()
    if not plan:
        plan = DailyPlan(user_id=user_id, date=today_str, status="PLANNED")
        db.session.add(plan)
        db.session.commit()

    tasks_from_bitrix = fetch_todays_bitrix_tasks(user_id)
    for btx in tasks_from_bitrix:
        existing = DailyTask.query.filter_by(plan_id=plan.id, task_name=btx["TITLE"]).first()
        if not existing:
            new_task = DailyTask(plan_id=plan.id, task_name=btx["TITLE"], status="PLANNED")
            db.session.add(new_task)
    db.session.commit()

    morning_advice = get_gpt_plan_overview_advice(user_id, plan.id)

    message_text = (
        f"Доброе утро!\n"
        f"Сформирован план на сегодня (статус PLANNED).\n"
        f"Задач из Bitrix24: {len(tasks_from_bitrix)}\n\n"
        f"GPT-рекомендации на утро:\n{morning_advice}\n\n"
        f"Введите /start_day, чтобы начать рабочий день."
    )
    send_message_to_bitrix(user_id, message_text)


def carry_over_incomplete_tasks(user_id: int):
    """Переносим незавершённые задачи вчерашнего дня в сегодняшний план (PLANNED)."""
    yesterday_str = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    today_str = datetime.date.today().isoformat()

    old_plan = DailyPlan.query.filter_by(user_id=user_id, date=yesterday_str).first()
    if not old_plan:
        return

    incomplete_tasks = DailyTask.query.filter(
        DailyTask.plan_id == old_plan.id,
        DailyTask.status.in_(["PLANNED", "IN_PROGRESS"])
    ).all()
    if not incomplete_tasks:
        return

    plan_today = DailyPlan.query.filter_by(user_id=user_id, date=today_str).first()
    if not plan_today:
        plan_today = DailyPlan(user_id=user_id, date=today_str, status="PLANNED")
        db.session.add(plan_today)
        db.session.commit()

    for t in incomplete_tasks:
        new_task = DailyTask(
            plan_id=plan_today.id,
            task_name=t.task_name,
            status="PLANNED"
        )
        db.session.add(new_task)
    db.session.commit()

    send_message_to_bitrix(
        user_id,
        "Есть незавершённые задачи со вчера. Они перенесены в план на сегодня."
    )


def fetch_todays_bitrix_tasks(user_id: int):
    """Получаем из Bitrix24 список задач на сегодня. Фильтр настройте по своей логике."""
    if not BITRIX_TASK_LIST_URL:
        return []
    payload = {
        "filter": {
            "RESPONSIBLE_ID": user_id,
            ">=CREATED_DATE": datetime.date.today().isoformat()
        },
        "select": ["ID", "TITLE", "STATUS"]
    }
    try:
        resp = requests.post(BITRIX_TASK_LIST_URL, json=payload, timeout=5)
        data = resp.json()
        if "result" in data and "tasks" in data["result"]:
            return data["result"]["tasks"]
    except Exception as e:
        print(f"Ошибка запрос задач Bitrix: {e}")
    return []


def handle_start_work_day(user_id: int):
    """
    /start_day — если плана нет, создаём. Если PLANNED, переводим в STARTED.
    Вызываем get_motivational_greeting, который похвалит за успехи вчера
    и отчитает за невыполненные задачи.
    """
    today_str = datetime.date.today().isoformat()
    plan = DailyPlan.query.filter_by(user_id=user_id, date=today_str).first()

    if not plan:
        plan = DailyPlan(user_id=user_id, date=today_str, status="PLANNED")
        db.session.add(plan)
        db.session.commit()

    if plan.status == "STARTED":
        send_message_to_bitrix(user_id, "План уже в статусе STARTED. Можно добавлять задачи или начинать выполнение.")
        return "План уже стартовал."
    if plan.status == "FINISHED":
        send_message_to_bitrix(user_id, "План уже завершён на сегодня. Можно создать новый день завтра.")
        return "План уже завершён."

    # Если план был PLANNED (или только что создан),
    plan.status = "STARTED"
    plan.start_time = datetime.datetime.now().strftime("%H:%M")
    db.session.commit()

    # Смотрим, какие вчера были завершены, а какие остались незавершёнными
    yesterdays_completed = get_yesterdays_completed_tasks(user_id)
    yesterdays_incomplete = get_yesterdays_incomplete_tasks(user_id)

    # Мотивационное приветствие (с похвалой и «отчиткой»)
    motivation_msg = get_motivational_greeting(
        user_id=user_id,
        date_str=today_str,
        yesterdays_completed=yesterdays_completed,
        yesterdays_incomplete=yesterdays_incomplete
    )

    tasks = DailyTask.query.filter_by(plan_id=plan.id).all()
    if not tasks:
        msg = (
            f"{motivation_msg}\n\n"
            f"Рабочий день начат в {plan.start_time}.\n"
            f"Пока нет задач. Добавьте с помощью /add_tasks Задача1, Задача2.\n"
        )
        send_message_to_bitrix(user_id, msg)
        return "Рабочий день начат (нет задач)."

    # Есть задачи — общий совет
    overview = get_gpt_plan_overview_advice(user_id, plan.id)

    msg = (
        f"{motivation_msg}\n\n"
        f"Рабочий день начат в {plan.start_time}.\n"
        f"Текущий список задач:\n"
    )
    for t in tasks:
        msg += f"- [{t.id}] {t.task_name} (статус={t.status})\n"

    msg += f"\nGPT рекомендации:\n{overview}"
    send_message_to_bitrix(user_id, msg)
    return f"Рабочий день начат (задач={len(tasks)})."


def handle_add_tasks(user_id: int, task_names: list):
    today_str = datetime.date.today().isoformat()
    plan = DailyPlan.query.filter_by(user_id=user_id, date=today_str, status="STARTED").first()
    if not plan:
        send_message_to_bitrix(user_id, "Сначала начните рабочий день командой /start_day.")
        return

    for name in task_names:
        new_task = DailyTask(plan_id=plan.id, task_name=name, status="PLANNED")
        db.session.add(new_task)
    db.session.commit()

    send_message_to_bitrix(user_id, f"Задачи добавлены: {', '.join(task_names)}.")


def handle_start_task(user_id: int, task_id: int):
    today_str = datetime.date.today().isoformat()
    plan = DailyPlan.query.filter_by(user_id=user_id, date=today_str, status="STARTED").first()
    if not plan:
        send_message_to_bitrix(user_id, "Нет активного плана (STARTED).")
        return

    task = DailyTask.query.filter_by(id=task_id, plan_id=plan.id, status="PLANNED").first()
    if not task:
        send_message_to_bitrix(user_id, f"Задача {task_id} не найдена или не в статусе PLANNED.")
        return

    task.status = "IN_PROGRESS"
    task.start_time = datetime.datetime.now().strftime("%H:%M")
    db.session.commit()

    advice = get_gpt_task_advice(task.task_name)
    msg = (
        f"Задача [{task.id}] '{task.task_name}' → IN_PROGRESS.\n"
        f"GPT совет:\n{advice}"
    )
    send_message_to_bitrix(user_id, msg)


def handle_complete_task(user_id: int, task_id: int):
    today_str = datetime.date.today().isoformat()
    plan = DailyPlan.query.filter_by(user_id=user_id, date=today_str, status="STARTED").first()
    if not plan:
        send_message_to_bitrix(user_id, "Нет активного плана дня (STARTED).")
        return

    task = DailyTask.query.filter_by(id=task_id, plan_id=plan.id, status="IN_PROGRESS").first()
    if not task:
        send_message_to_bitrix(user_id, f"Задача {task_id} не найдена или не в статусе IN_PROGRESS.")
        return

    task.status = "COMPLETED"
    task.end_time = datetime.datetime.now().strftime("%H:%M")
    db.session.commit()

    send_message_to_bitrix(user_id, f"Задача [{task.id}] '{task.task_name}' завершена!")


def handle_finish_work_day(user_id: int):
    today_str = datetime.date.today().isoformat()
    plan = DailyPlan.query.filter_by(user_id=user_id, date=today_str, status="STARTED").first()
    if not plan:
        send_message_to_bitrix(user_id, "Не найден план со статусом STARTED. Возможно, день уже завершён.")
        return

    plan.status = "FINISHED"
    plan.end_time = datetime.datetime.now().strftime("%H:%M")

    tasks = DailyTask.query.filter_by(plan_id=plan.id).all()
    total = len(tasks)
    completed = len([t for t in tasks if t.status == "COMPLETED"])
    efficiency = round((completed / total * 100), 2) if total else 0
    plan.efficiency_score = efficiency

    db.session.commit()

    final_advice = get_gpt_final_summary(tasks, efficiency)

    msg = (
        f"Рабочий день завершён в {plan.end_time}.\n"
        f"Всего задач: {total}, выполнено: {completed}.\n"
        f"Эффективность: {efficiency}%.\n\n"
        f"Итоговые рекомендации:\n{final_advice}\n\n"
        f"Спасибо за работу!"
    )
    send_message_to_bitrix(user_id, msg)


# -------------------------------------------------------
#  Дополнительные функции
# -------------------------------------------------------
def get_yesterdays_completed_tasks(user_id: int):
    """
    Возвращает список названий задач, которые вчера были COMPLETED.
    """
    yesterday_str = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    plan_yesterday = DailyPlan.query.filter_by(user_id=user_id, date=yesterday_str).first()
    if not plan_yesterday:
        return []
    completed_tasks = DailyTask.query.filter_by(plan_id=plan_yesterday.id, status="COMPLETED").all()
    return [t.task_name for t in completed_tasks]


def get_yesterdays_incomplete_tasks(user_id: int):
    """
    Возвращает список названий задач, которые вчера остались незавершёнными (PLANNED или IN_PROGRESS).
    """
    yesterday_str = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    plan_yesterday = DailyPlan.query.filter_by(user_id=user_id, date=yesterday_str).first()
    if not plan_yesterday:
        return []
    incomplete_tasks = DailyTask.query.filter(
        DailyTask.plan_id == plan_yesterday.id,
        DailyTask.status.in_(["PLANNED", "IN_PROGRESS"])
    ).all()
    return [t.task_name for t in incomplete_tasks]


# -------------------------------------------------------
# Мотивационное приветствие (с похвалой и "отчиткой")
# -------------------------------------------------------
def get_motivational_greeting(user_id: int, date_str: str, yesterdays_completed: list, yesterdays_incomplete: list):
    """
    Генерирует 'мотивационную речь' от лица 'AI планировщика дня'.
    - Если есть завершённые задачи, похвалим
    - Если есть незавершённые задачи, мягко отругаем/подстегнём
    """
    completed_str = ""
    if yesterdays_completed:
        completed_str = "Вчера вы успешно завершили: " + ", ".join(yesterdays_completed) + ".\n"
    else:
        completed_str = "Вчера не было завершённых задач.\n"

    incomplete_str = ""
    if yesterdays_incomplete:
        incomplete_str = (
            "Однако остались незавершённые задачи: " +
            ", ".join(yesterdays_incomplete) +
            ". Надо их довести до ума!\n"
        )
    else:
        incomplete_str = "Все задачи вчера были закрыты вовремя, молодец!\n"

    prompt = (
        f"Ты — AI планировщик, незаменимый инструмент эффективности сотрудника. "
        f"Сегодня {date_str}. Поздоровайся, похвали за успехи (если есть), "
        f"и, если есть незавершённые задачи, мягко отчитывай и подстёгивай к их завершению. "
        f"Обращайся на «ты», будь дружелюбен и мотивирующ.\n\n"
        f"{completed_str}{incomplete_str}"
        f"В конце дай короткую воодушевляющую фразу."
    )

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.9
        )
        text = response.choices[0].message.content.strip()
        return text
    except Exception as e:
        print(f"GPT motivational greeting error: {e}")
        return (
            f"Сегодня {date_str} — новый день! "
            f"Посмотрим, что было вчера: {completed_str} {incomplete_str} "
            f"Надеюсь, сегодня всё сделаем!"
        )

# -------------------------------------------------------
# GPT вспомогательные (как раньше)
# -------------------------------------------------------
def get_gpt_plan_overview_advice(user_id: int, plan_id: int):
    tasks = DailyTask.query.filter_by(plan_id=plan_id).all()
    if not tasks:
        return "На сегодня задач нет — составьте список или добавьте."

    task_lines = "\n".join([f"- {t.task_name}" for t in tasks])
    prompt = (
        f"Ниже список задач на сегодня:\n{task_lines}\n\n"
        f"Дай общий совет, как эффективно спланировать день?"
    )
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"GPT overview error: {e}")
        return "Не удалось получить общий совет на день."


def get_gpt_task_advice(task_name: str):
    prompt = f"Дай совет, как выполнить задачу '{task_name}' максимально эффективно."
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"GPT task advice error: {e}")
        return "Не удалось получить совет от GPT."


def get_gpt_final_summary(tasks, efficiency):
    task_info = ""
    for t in tasks:
        status = t.status
        task_info += f"\n- {t.task_name} [{status}]"

    prompt = (
        f"Сегодняшние задачи:{task_info}\n"
        f"Эффективность {efficiency}%. "
        f"Дай небольшой итог работы и совет на завтра."
    )
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"GPT final summary error: {e}")
        return "Не удалось получить финальные рекомендации."


def send_message_to_bitrix(user_id: int, message: str):
    if not BITRIX_MESSAGE_ADD_URL:
        print("BITRIX_MESSAGE_ADD_URL не настроен.")
        return
    payload = {
        "DIALOG_ID": user_id,
        "MESSAGE": message
    }
    try:
        resp = requests.post(BITRIX_MESSAGE_ADD_URL, json=payload, timeout=5)
        if resp.status_code != 200:
            print("Ошибка при отправке в Bitrix:", resp.text)
    except Exception as e:
        print(f"Ошибка при запросе к Bitrix24: {e}")
