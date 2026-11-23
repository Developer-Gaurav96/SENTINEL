import psutil

def get_cpu_cores():
    return psutil.cpu_count()
def get_ram_usage():
    return psutil.virtual_memory().percent
def get_disk_usage():
    return psutil.disk_usage('/').percent

print("=" * 32)
print("              SENTINEL")
print("         SYSTEM INFORMATION")

print(f"Cpu cores:               {get_cpu_cores()}")
print(f"RAM Usage:               {get_ram_usage()}%")
print(f"Disk Usage:              {get_disk_usage()}%")

print("=" * 32)
