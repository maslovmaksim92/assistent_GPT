Ваш запрос предполагает разработку полноценного веб-приложения, который включает в себя frontend и backend разработку. Это не может быть выполнено в рамках одного скрипта Python, потому что вам потребуются различные технологии, такие как HTML, CSS, JavaScript для frontend и, возможно, Python с использованием фреймворка Django или Flask для backend.

Однако, я могу предложить вам базовый пример того, как вы можете создать простое веб-приложение на Flask, которое будет позволять вам управлять параметрами бота.

```python
from flask import Flask, render_template, request
app = Flask(__name__)

# Предположим, что у вас есть класс Bot
class Bot:
    def __init__(self, name, param1, param2):
        self.name = name
        self.param1 = param1
        self.param2 = param2

# Создаем список ботов
bots = [Bot('Bot1', 'param1', 'param2'), Bot('Bot2', 'param1', 'param2')]

@app.route('/')
def index():
    return render_template('index.html', bots=bots)

@app.route('/update_bot', methods=['POST'])
def update_bot():
    bot_name = request.form.get('bot_name')
    param1 = request.form.get('param1')
    param2 = request.form.get('param2')
    for bot in bots:
        if bot.name == bot_name:
            bot.param1 = param1
            bot.param2 = param2
            break
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
```

В этом примере мы создаем простое веб-приложение с двумя маршрутами. Один для отображения списка ботов и один для обновления параметров бота. Мы используем метод POST для отправки данных из веб-формы на сервер.

Пожалуйста, обратите внимание, что это очень простой пример и в реальном приложении вам потребуется добавить обработку ошибок, аутентификацию пользователей и другие важные функции.