import psutil
import cpuinfo
from rich.columns import Columns
from rich.console import Group
from rich.panel import Panel
from rich.console import Console
from rich.text import Text
from textwrap import dedent
from rich.table import Table
import platform
from rich.live import Live
from time import sleep, time

console = Console()
system_table = Table(expand=True)


logo = dedent("""
███████╗███████╗███╗   ██╗████████╗██╗███╗   ██╗███████╗██╗
██╔════╝██╔════╝████╗  ██║╚══██╔══╝██║████╗  ██║██╔════╝██║
███████╗█████╗  ██╔██╗ ██║   ██║   ██║██╔██╗ ██║█████╗  ██║
╚════██║██╔══╝  ██║╚██╗██║   ██║   ██║██║╚██╗██║██╔══╝  ██║
███████║███████╗██║ ╚████║   ██║   ██║██║ ╚████║███████╗███████╗
╚══════╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝
""")

def get_cpu_details():
    cpu_dict = cpuinfo.get_cpu_info()
    return cpu_dict["brand_raw"], cpu_dict["arch"], cpu_dict["count"]

cpu, arch, count = get_cpu_details()

def get_ram_usage():
    return psutil.virtual_memory().percent
def get_disk_usage():
    return psutil.disk_usage('/').percent

def get_resource_status(usage):
    if (usage >= 90):
        return "CRITICAL"
    elif (usage >= 70):
        return "WARNING"
    else:
        return "NORMAL"

def get_status_style(status):
    if status == "NORMAL":
        return "bold green"
    elif status == "WARNING":
        return "bold yellow"
    else:
        return "bold red"

def get_resource_table():
    resource_table = Table(expand=True)

    resource_table.add_column("METRIC", style="bold cyan")
    resource_table.add_column("USAGE", style="white")
    resource_table.add_column("STATUS")

    cpu_usage = psutil.cpu_percent(interval=None)
    ram_usage = get_ram_usage()
    disk_usage = get_disk_usage()

    for name, usage in [
        ("CPU", cpu_usage),
        ("RAM USAGE", ram_usage),
        ("DISK USAGE", disk_usage)
    ]:
        status = get_resource_status(usage)

        resource_table.add_row(
            name,
            f"{usage:.1f}%",
            Text(status, style=get_status_style(status))
        )

    return resource_table

def build_layout(download_speed, upload_speed, current_stats):
    left_column = Group(
        Panel(system_table, title="SYSTEM"),
        Panel(get_resource_table(), title="RESOURCE MONITOR"),
        Panel(
            get_network_table(download_speed, upload_speed, current_stats),
            title="NETWORK"
            )
    )

    right_column = Group(
        Panel("System Health", title="SYSTEM HEALTH"),
        Panel("Top Processes", title="TOP PROCESSES")
    )

    if console.size.width >= 120:
        main_content = Columns(
            [left_column, right_column],
            expand=True,
            equal=False
        )
    else:
        main_content = Group(
            left_column,
            right_column
        )

    return Group(
        Panel(Text(logo, style="bold cyan"), border_style="cyan"),
        main_content,
        Panel(
            "[bold green]● ONLINE[/bold green]  Monitoring Active     [dim]Q: Quit  |  R: Refresh[/dim]",
            border_style="cyan"
        )
    )

def get_network_table(download_speed, upload_speed, current_stats):
    network_table = Table(expand=True)

    network_table.add_column(
        "DIRECTION",
        style="bold cyan",
        width=18,
        no_wrap=True
    )

    network_table.add_column(
        "SPEED",
        style="white",
        width=18,
        justify="right",
        no_wrap=True
    )

    network_table.add_row(
        "DOWNLOAD",
        Text(f"{download_speed / 1024:.2f} KB/s", style="bold green")
    )

    network_table.add_row(
        "UPLOAD",
        Text(f"{upload_speed / 1024:.2f} KB/s", style="bold yellow")
    )

    return network_table

def get_network_speed(previous_stats, previous_time):
    current_stats = psutil.net_io_counters()
    current_time = time()

    elapsed = current_time - previous_time

    if elapsed <= 0:
        return 0, 0, current_stats, current_time
    
    else:
        download_speed = (current_stats.bytes_recv - previous_stats.bytes_recv) / elapsed
        upload_speed = (current_stats.bytes_sent - previous_stats.bytes_sent) / elapsed
        return download_speed, upload_speed, current_stats, current_time

def format_bytes(bytes_value):
    units = ["B", "KB", "MB", "GB", "TB"]
    for unit in units:
        if bytes_value < 1024:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024

    return f"{bytes_value:.2f} PB"


# SYSTEM

system_table.add_column("PROPERTY", style="bold cyan")
system_table.add_column("VALUE", style="white")

system_table.add_row("HOSTNAME", platform.node())
system_table.add_row("OPERATING SYSTEM", platform.system())
system_table.add_row("PROCESSOR", cpu)
system_table.add_row("ARCHITECTURE", arch)
system_table.add_row("LOGICAL PROCESSORS", str(count))

psutil.cpu_percent(interval=None)

previous_stats = psutil.net_io_counters()
previous_time = time()
download_speed = 0
upload_speed = 0

current_stats = previous_stats

try:
    with Live(
        build_layout(download_speed, upload_speed, current_stats),
        console=console,
        refresh_per_second=4,
        screen=True,
        vertical_overflow="ellipsis"
             ) as live:
        while True:
            download_speed, upload_speed, previous_stats, previous_time = get_network_speed(
            previous_stats, previous_time)
            live.update(build_layout(download_speed, upload_speed, current_stats))
            sleep(0.25)

except KeyboardInterrupt:
    pass