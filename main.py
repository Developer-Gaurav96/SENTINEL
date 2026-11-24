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
from time import sleep

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

def build_layout():
    left_column = Group(
        Panel(system_table, title="SYSTEM"),
        Panel(get_resource_table(), title="RESOURCE MONITOR"),
        Panel("Network Statistics", title="NETWORK")
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


# SYSTEM

system_table.add_column("PROPERTY", style="bold cyan")
system_table.add_column("VALUE", style="white")

system_table.add_row("HOSTNAME", platform.node())
system_table.add_row("OPERATING SYSTEM", platform.system())
system_table.add_row("PROCESSOR", cpu)
system_table.add_row("ARCHITECTURE", arch)
system_table.add_row("LOGICAL PROCESSORS", str(count))

psutil.cpu_percent(interval=None)
try:
    with Live(
        build_layout(),
        console=console,
        refresh_per_second=4,
        screen=True,
        vertical_overflow="ellipsis"
    ) as live:
        while True:
            live.update(build_layout())
            sleep(0.25)

except KeyboardInterrupt:
    pass