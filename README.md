# nginx-lens

**nginx-lens** — современный CLI-инструмент для анализа, диагностики и визуализации конфигураций Nginx.

## Зачем нужен nginx-lens?

- Быстро находит ошибки и потенциальные проблемы в ваших nginx-конфигах.
- Визуализирует маршруты и структуру — легко понять, как устроен ваш nginx.
- Показывает, какой location/server обслуживает конкретный URL.
- Анализирует логи и помогает выявить аномалии.
- Упрощает аудит, миграцию и поддержку сложных инфраструктур.

## Примеры работы

### Справочник утилиты

![nginx-lens --help](docs/main-help.jpeg)

### Справочник для команд

![nginx-lens <команда> --help](docs/command-help.jpeg)

### Доступность upstream-серверов

![nginx-lens health <путь_к_конфигу>](docs/example-health.jpeg)

### Древовидная визуализация структуры конфига

![nginx-lens tree <путь_к_конфигу>](docs/example-tree.jpeg)

### Древовидная визуализация include'ов

![nginx-lens include-tree <путь_к_конфигу>](docs/example-include-tree.jpeg)

### Удобный анализатор логов

![nginx-lens logs <путь_к_файлу_лога>](docs/example-logs.jpeg)

### Аудит конфигурации

![nginx-lens analyze <путь_к_конфигу>](docs/example-analyze.jpeg)

### Визуализация маршрутов

![nginx-lens graph <путь_к_конфигу>](docs/example-graph.jpeg)

### Поиск маршрута для URL

![nginx-lens route <URL>](docs/example-route.png)

### Сравнение конфигов

![nginx-lens diff <путь_к_первому_конфигу> <путь_к_второму_конфигу>](docs/example-diff.jpeg)

### Удобная проверка синтаксиса конфига

![nginx-lens syntax](docs/example-syntax.jpeg)


## Установка и системные требования

- **Python 3.8+**
- Linux/macOS (работает и под Windows WSL)

### Установка с помощью bash-скрипта (Рекомендуется)

```bash
wget https://raw.githubusercontent.com/shelovesuastra/nginx-lens/install-nginx-lens.sh
# или
curl https://raw.githubusercontent.com/shelovesuastra/nginx-lens/install-nginx-lens.sh

chmod +x install-nginx-lens.sh

./install-nginx-lens.sh
# или
sh ./install-nginx-lens.sh
# или
bash ./install-nginx-lens.sh
```

### Установка через PyPI

```bash
pipx install nginx-lens
```
или
```bash
pip install nginx-lens
```

## Автор

[Daniil Astrouski](https://github.com/shelovesuastra)

## Лицензия

MIT