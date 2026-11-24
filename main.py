import psutil
import cpuinfo
from rich.layout import Layout
from rich.panel import Panel
from rich.console import Console
from rich.text import Text
from rich.align import Align
from textwrap import dedent

console = Console()

layout = Layout()
layout.split_column(
    Layout(name="header", size=9),
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

console.print(layout["header"])