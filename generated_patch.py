Реализация этой задачи зависит от множества вещей: вашего стека технологий, сколько кода вы готовы предоставить и т.д. Но в общих чертах решение может выглядеть примерно так:

Для веб-интерфейса можно использовать flask:

```python
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')  # предполагается, что вы имеете готовую веб-страницу с аккардеонами блоками

@app.route('/create_bot', methods=['POST'])
def create_bot():
    bot_params = None  # берем данные из POST-запроса
    bot = Bot(**bot_params)  # создаем бота с параметрами

    # сохраняем бота (например, в базу данных)
    
    return redirect(url_for('home'))
```

Для каждого бота вы можете создать класс с методами, которые можно вызывать из веб-страницы:

```python
class Bot:
    def __init__(self, **params):
        self.params = params

    def start(self):
        # запускаем бота

    def stop(self):
        # останавливаем бота

    def update_params(self, **new_params):
        self.params.update(new_params)
```

Форму для создания бота и кнопки управления каждым ботом вы можете добавить на веб-страницу:

```html
<form action="{{ url_for('create_bot') }}" method="post">
  <!-- поля формы для каждого параметра бота -->
  <button type="submit">Создать бота</button>
</form>

<div class="accordion">
  <!-- для каждого бота -->
  <div class="card">
    <div class="card-header">
      <h2 class="mb-0">
        <!-- дисплей параметров бота --> 
      </h2>
    </div>
    <div id="collapseOne" class="collapse" aria-labelledby="headingOne" data-parent="#accordionExample">
      <div class="card-body">
        <!-- форма или кнопка для обновления параметров бота -->
        <!-- кнопка для запуска/остановки бота -->
      </div>
    </div>
  </div>
</div>
```

Этот код — очень общая идея, и его следует адаптировать в соответствии с вашим конкретным сценарием.