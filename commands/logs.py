import typer
from rich.console import Console
from rich.table import Table
import re
from collections import Counter, defaultdict

app = typer.Typer(help="Анализ access.log/error.log: топ-статусы, пути, IP, User-Agent, ошибки.")
console = Console()

log_line_re = re.compile(r'(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] "(?P<method>\S+) (?P<path>\S+) [^\"]+" (?P<status>\d{3})')

def logs(
    log_path: str = typer.Argument(..., help="Путь к access.log или error.log"),
    top: int = typer.Option(10, help="Сколько топ-значений выводить")
):
    """
    Анализирует access.log/error.log.

    Показывает:
      - Топ HTTP-статусов (404, 500 и др.)
      - Топ путей
      - Топ IP-адресов
      - Топ User-Agent
      - Топ путей с ошибками 404/500

    Пример:
        nginx-lens logs /var/log/nginx/access.log --top 20
    """
    try:
        with open(log_path) as f:
            lines = list(f)
    except FileNotFoundError:
        console.print(f"[red]Файл {log_path} не найден. Проверьте путь к логу.[/red]")
        return
    except Exception as e:
        console.print(f"[red]Ошибка при чтении {log_path}: {e}[/red]")
        return
    status_counter = Counter()
    path_counter = Counter()
    ip_counter = Counter()
    user_agent_counter = Counter()
    errors = defaultdict(list)
    for line in lines:
        m = log_line_re.search(line)
        if m:
            ip = m.group('ip')
            path = m.group('path')
            status = m.group('status')
            status_counter[status] += 1
            path_counter[path] += 1
            ip_counter[ip] += 1
            if status.startswith('4') or status.startswith('5'):
                errors[status].append(path)
        # user-agent (если есть)
        if '" "' in line:
            ua = line.rsplit('" "', 1)[-1].strip().strip('"')
            if ua:
                user_agent_counter[ua] += 1
    # Топ статусов
    table = Table(title="Top HTTP Status Codes", show_header=True, header_style="bold blue")
    table.add_column("Status")
    table.add_column("Count")
    for status, count in status_counter.most_common(top):
        table.add_row(status, str(count))
    console.print(table)
    # Топ путей
    table = Table(title="Top Paths", show_header=True, header_style="bold blue")
    table.add_column("Path")
    table.add_column("Count")
    for path, count in path_counter.most_common(top):
        table.add_row(path, str(count))
    console.print(table)
    # Топ IP
    table = Table(title="Top IPs", show_header=True, header_style="bold blue")
    table.add_column("IP")
    table.add_column("Count")
    for ip, count in ip_counter.most_common(top):
        table.add_row(ip, str(count))
    console.print(table)
    # Топ User-Agent
    if user_agent_counter:
        table = Table(title="Top User-Agents", show_header=True, header_style="bold blue")
        table.add_column("User-Agent")
        table.add_column("Count")
        for ua, count in user_agent_counter.most_common(top):
            table.add_row(ua, str(count))
        console.print(table)
    # Топ 404/500
    for err in ('404', '500'):
        if errors[err]:
            table = Table(title=f"Top {err} Paths", show_header=True, header_style="bold blue")
            table.add_column("Path")
            table.add_column("Count")
            c = Counter(errors[err])
            for path, count in c.most_common(top):
                table.add_row(path, str(count))
            console.print(table) 