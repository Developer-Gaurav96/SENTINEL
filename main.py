
import os
import psutil
import cpuinfo
import platform

from rich.columns import Columns
from rich.console import Group, Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.live import Live

from textwrap import dedent
from time import sleep, time


console = Console()
system_table = Table(expand=True)
process_cpu = {}


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
    return (
        cpu_dict.get("brand_raw", "Unknown"),
        cpu_dict.get("arch", "Unknown"),
        cpu_dict.get("count") or psutil.cpu_count() or 0
    )


cpu, arch, count = get_cpu_details()


def get_ram_usage():
    return psutil.virtual_memory().percent


def get_disk_usage():
    if platform.system() == "Windows":
        disk_path = os.environ.get("SystemDrive", "C:")
    else:
        disk_path = "/"

    return psutil.disk_usage(disk_path).percent


def get_resource_status(usage):
    if usage >= 90:
        return "CRITICAL"
    elif usage >= 70:
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

    resource_table.add_column(
        "METRIC", style="bold cyan",
        width=26, no_wrap=True, ratio=0
    )
    resource_table.add_column(
        "USAGE", style="white",
        width=10, justify="right", no_wrap=True, ratio=0
    )
    resource_table.add_column(
        "STATUS", width=12,
        no_wrap=True, ratio=1
    )

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


def build_layout(download_speed, upload_speed):
    left_column = Group(
        Panel(system_table, title="SYSTEM"),
        Panel(get_resource_table(), title="RESOURCE MONITOR"),
        Panel(
            get_network_table(download_speed, upload_speed),
            title="NETWORK"
        )
    )

    right_column = Group(
        Panel(get_system_health_table(), title="SYSTEM HEALTH"),
        Panel(get_process_table(), title="TOP PROCESSES")
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
        Panel(
            Text(logo, style="bold cyan"),
            border_style="cyan"
        ),
        main_content,
        Panel(
            "[bold green]● ONLINE[/bold green]  Monitoring Active     [dim]Ctrl+C: Quit[/dim]",
            border_style="cyan"
        )
    )


def get_network_table(download_speed, upload_speed):
    network_table = Table(expand=True)

    network_table.add_column(
        "DIRECTION",
        style="bold cyan",
        width=26,
        no_wrap=True,
        ratio=0
    )

    network_table.add_column(
        "SPEED",
        style="white",
        width=18,
        justify="right",
        no_wrap=True,
        ratio=1
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

    downloaded = current_stats.bytes_recv - previous_stats.bytes_recv
    uploaded = current_stats.bytes_sent - previous_stats.bytes_sent

    download_speed = max(0, downloaded / elapsed)
    upload_speed = max(0, uploaded / elapsed)

    return download_speed, upload_speed, current_stats, current_time


def format_bytes(bytes_value):
    units = ["B", "KB", "MB", "GB", "TB"]

    for unit in units:
        if bytes_value < 1024:
            return f"{bytes_value:.2f} {unit}"

        bytes_value /= 1024

    return f"{bytes_value:.2f} PB"


def get_process_table():
    process_table = Table(expand=True)

    process_table.add_column(
        "PID", style="dim white",
        width=8, no_wrap=True, ratio=0
    )
    process_table.add_column(
        "PROCESS", style="bold cyan",
        width=25, no_wrap=True, overflow="ellipsis", ratio=0
    )
    process_table.add_column(
        "RAM %", style="bold green",
        width=10, justify="right", no_wrap=True, ratio=0
    )
    process_table.add_column(
        "CPU %", style="purple",
        width=10, justify="right", no_wrap=True, ratio=1
    )

    processes = []
    active_processes = set()

    for process in psutil.process_iter(
        ["pid", "name", "memory_percent"]
    ):
        try:
            pid = process.info["pid"]
            create_time = process.create_time()
            process_id = (pid, create_time)

            active_processes.add(process_id)

            if process_id not in process_cpu:
                process_cpu[process_id] = process

            cpu_usage = process_cpu[process_id].cpu_percent()

            processes.append((
                pid,
                process.info["name"] or "Unknown",
                process.info["memory_percent"] or 0.0,
                cpu_usage
            ))

        except (psutil.Error, TypeError, KeyError):
            continue

    for process_id in list(process_cpu):
        if process_id not in active_processes:
            del process_cpu[process_id]

    top_processes = sorted(
        processes,
        key=lambda process: process[3],
        reverse=True
    )[:12]

    for pid, name, memory_usage, cpu_usage in top_processes:
        process_table.add_row(
            str(pid),
            name,
            f"{memory_usage:.2f}%",
            f"{cpu_usage:.1f}%"
        )

    return process_table


def get_system_uptime():
    uptime = time() - psutil.boot_time()

    days, remainder = divmod(uptime, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    return (
        f"{int(days)}d {int(hours)}h "
        f"{int(minutes)}m {int(seconds)}s"
    )


def get_system_health_table():
    health_table = Table(expand=True)

    health_table.add_column(
        "METRIC", style="bold cyan",
        width=36, no_wrap=True, ratio=0
    )
    health_table.add_column(
        "VALUE", style="white", ratio=1
    )

    health_table.add_row("UPTIME", get_system_uptime())
    health_table.add_row("TOTAL PROCESSES", str(len(psutil.pids())))
    health_table.add_row(
        "AVAILABLE RAM",
        format_bytes(psutil.virtual_memory().available)
    )

    physical_cores = psutil.cpu_count(logical=False)

    health_table.add_row(
        "CPU CORES",
        str(physical_cores or "Unknown")
    )

    return health_table


# SYSTEM TABLE

system_table.add_column(
    "PROPERTY", style="bold cyan",
    width=26, no_wrap=True, ratio=0
)
system_table.add_column(
    "VALUE", style="white", ratio=1
)

system_table.add_row("HOSTNAME", platform.node())
system_table.add_row("OPERATING SYSTEM", platform.system())
system_table.add_row("PROCESSOR", cpu)
system_table.add_row("ARCHITECTURE", arch)
system_table.add_row("LOGICAL PROCESSORS", str(count))


# MONITORING INITIALIZATION

psutil.cpu_percent(interval=None)

previous_stats = psutil.net_io_counters()
previous_time = time()

download_speed = 0
upload_speed = 0


# MAIN LOOP

try:
    with Live(
        build_layout(download_speed, upload_speed),
        console=console,
        refresh_per_second=4,
        screen=False,
        vertical_overflow="ellipsis"
    ) as live:

        while True:
            (
                download_speed,
                upload_speed,
                previous_stats,
                previous_time
            ) = get_network_speed(previous_stats, previous_time)

            live.update(
                build_layout(download_speed, upload_speed)
            )

            sleep(0.25)

except KeyboardInterrupt:
    pass
