import psutil
import cpuinfo
from rich.layout import Layout
from rich.panel import Panel
from rich.console import Console
from rich.text import Text
from rich.align import Align
from textwrap import dedent
from rich.table import Table
import platform

console = Console()
system_table = Table()
resource_table = Table()

layout = Layout()
layout.split_column(
    Layout(name="header", size=10),
    Layout(name="main"),
    Layout(name="footer", size=3)
)


def get_cpu_details():
    cpu_dict = cpuinfo.get_cpu_info()
    return cpu_dict["brand_raw"], cpu_dict["arch"], cpu_dict["count"]

cpu, arch, count = get_cpu_details()

def get_ram_usage():
    return psutil.virtual_memory().percent
def get_disk_usage():
    return psutil.disk_usage('/').percent

logo = dedent("""
███████╗███████╗███╗   ██╗████████╗██╗███╗   ██╗███████╗██╗
██╔════╝██╔════╝████╗  ██║╚══██╔══╝██║████╗  ██║██╔════╝██║
███████╗█████╗  ██╔██╗ ██║   ██║   ██║██╔██╗ ██║█████╗  ██║
╚════██║██╔══╝  ██║╚██╗██║   ██║   ██║██║╚██╗██║██╔══╝  ██║
███████║███████╗██║ ╚████║   ██║   ██║██║ ╚████║███████╗███████╗
╚══════╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝
""")

header_content = Text(logo, justify="left", style="bold cyan")
header_panel = Panel(header_content, border_style="cyan", width=110, expand=False)
layout["header"].update(Align.center(header_panel, vertical="top"))
layout["main"].split_row(
    Layout(name="left", ratio=3),
    Layout(name="right", ratio=2)
)

layout["left"].split_column(
    Layout(name="system_info", ratio=2),
    Layout(name="resource_monitor", ratio=3),
    Layout(name="network", ratio=2)
)

# SYSTEM

system_table.add_column("PROPERTY", style="bold cyan")
system_table.add_column("VALUE", style="white")

system_table.add_row("HOSTNAME", platform.node())
system_table.add_row("OPERATING SYSTEM", platform.system())
system_table.add_row("PROCESSOR", cpu)
system_table.add_row("ARCHITECTURE", arch)
system_table.add_row("LOGICAL PROCESSORS", str(count))

# RESOURCE MONITOR

resource_table.add_column("METRIC", style="bold cyan")
resource_table.add_column("USAGE", style="white")
resource_table.add_column("STATUS", style="bold green")

resource_table.add_row(
    "CPU",
    f"{psutil.cpu_percent(interval=0.5):.1f}%",
    "NORMAL"
)

resource_table.add_row(
    "RAM USAGE",
    f"{get_ram_usage():.1f}%",
    "NORMAL"
)

resource_table.add_row(
    "DISK USAGE",
    f"{get_disk_usage():.1f}%",
    "NORMAL"
)

layout["system_info"].update(
    Panel(system_table, title="SYSTEM")
)

layout["resource_monitor"].update(
    Panel(resource_table, title="RESOURCE MONITOR")
)

layout["network"].update(
    Panel("Network Statistics", title="NETWORK")
)

layout["right"].split_column(
    Layout(name="system_health", ratio=2),
    Layout(name="top_processes", ratio=3)
)

layout["system_health"].update(
    Panel("System Health", title="SYSTEM HEALTH")
)

layout["top_processes"].update(
    Panel("Top Processes", title="TOP PROCESSES")
)

layout["footer"].update(
    Panel(
        "[bold green]● ONLINE[/bold green]  Monitoring Active     [dim]Q: Quit  |  R: Refresh[/dim]",
        border_style="cyan"
    )
)



console.print(layout)