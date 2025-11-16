"""
Módulo para coletar métricas de sistema e infraestrutura.
"""
import psutil
import time
from typing import Dict, Any
from datetime import datetime


def get_cpu_metrics() -> Dict[str, Any]:
    """
    Coleta métricas de CPU.
    """
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count(logical=True)
    cpu_count_physical = psutil.cpu_count(logical=False)
    cpu_freq = psutil.cpu_freq()

    metrics = {
        "usage_percent": round(cpu_percent, 2),
        "cores_logical": cpu_count,
        "cores_physical": cpu_count_physical,
        "frequency": {
            "current": round(cpu_freq.current, 2) if cpu_freq else None,
            "min": round(cpu_freq.min, 2) if cpu_freq else None,
            "max": round(cpu_freq.max, 2) if cpu_freq else None,
        } if cpu_freq else None
    }

    return metrics


def get_memory_metrics() -> Dict[str, Any]:
    """
    Coleta métricas de memória RAM.
    """
    virtual_mem = psutil.virtual_memory()
    swap_mem = psutil.swap_memory()

    metrics = {
        "total": virtual_mem.total,
        "available": virtual_mem.available,
        "used": virtual_mem.used,
        "free": virtual_mem.free,
        "percent": round(virtual_mem.percent, 2),
        "total_gb": round(virtual_mem.total / (1024**3), 2),
        "available_gb": round(virtual_mem.available / (1024**3), 2),
        "used_gb": round(virtual_mem.used / (1024**3), 2),
        "swap": {
            "total": swap_mem.total,
            "used": swap_mem.used,
            "free": swap_mem.free,
            "percent": round(swap_mem.percent, 2),
            "total_gb": round(swap_mem.total / (1024**3), 2),
            "used_gb": round(swap_mem.used / (1024**3), 2),
        }
    }

    return metrics


def get_disk_metrics() -> Dict[str, Any]:
    """
    Coleta métricas de disco.
    """
    partitions = psutil.disk_partitions()
    disk_info = []

    for partition in partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disk_info.append({
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "fstype": partition.fstype,
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
                "percent": round(usage.percent, 2),
                "total_gb": round(usage.total / (1024**3), 2),
                "used_gb": round(usage.used / (1024**3), 2),
                "free_gb": round(usage.free / (1024**3), 2),
            })
        except (PermissionError, OSError):
            # Ignorar partições sem permissão ou problemas de acesso
            continue

    # IO Statistics
    disk_io = psutil.disk_io_counters()
    io_stats = None
    if disk_io:
        io_stats = {
            "read_count": disk_io.read_count,
            "write_count": disk_io.write_count,
            "read_bytes": disk_io.read_bytes,
            "write_bytes": disk_io.write_bytes,
            "read_mb": round(disk_io.read_bytes / (1024**2), 2),
            "write_mb": round(disk_io.write_bytes / (1024**2), 2),
        }

    return {
        "partitions": disk_info,
        "io_counters": io_stats
    }


def get_network_metrics() -> Dict[str, Any]:
    """
    Coleta métricas de rede.
    """
    net_io = psutil.net_io_counters()

    metrics = {
        "bytes_sent": net_io.bytes_sent,
        "bytes_recv": net_io.bytes_recv,
        "packets_sent": net_io.packets_sent,
        "packets_recv": net_io.packets_recv,
        "errin": net_io.errin,
        "errout": net_io.errout,
        "dropin": net_io.dropin,
        "dropout": net_io.dropout,
        "bytes_sent_mb": round(net_io.bytes_sent / (1024**2), 2),
        "bytes_recv_mb": round(net_io.bytes_recv / (1024**2), 2),
    }

    return metrics


def get_process_metrics() -> Dict[str, Any]:
    """
    Coleta métricas do processo atual da aplicação.
    """
    process = psutil.Process()

    with process.oneshot():
        memory_info = process.memory_info()
        cpu_percent = process.cpu_percent(interval=0.1)

        metrics = {
            "pid": process.pid,
            "cpu_percent": round(cpu_percent, 2),
            "memory_rss": memory_info.rss,
            "memory_vms": memory_info.vms,
            "memory_rss_mb": round(memory_info.rss / (1024**2), 2),
            "memory_vms_mb": round(memory_info.vms / (1024**2), 2),
            "threads": process.num_threads(),
            "create_time": datetime.fromtimestamp(process.create_time()).isoformat(),
        }

    return metrics


def get_system_info() -> Dict[str, Any]:
    """
    Coleta informações gerais do sistema.
    """
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime_seconds = time.time() - psutil.boot_time()

    metrics = {
        "boot_time": boot_time.isoformat(),
        "uptime_seconds": round(uptime_seconds, 2),
        "uptime_hours": round(uptime_seconds / 3600, 2),
        "uptime_days": round(uptime_seconds / 86400, 2),
    }

    return metrics


def get_all_metrics() -> Dict[str, Any]:
    """
    Coleta todas as métricas do sistema.
    """
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "system": get_system_info(),
        "cpu": get_cpu_metrics(),
        "memory": get_memory_metrics(),
        "disk": get_disk_metrics(),
        "network": get_network_metrics(),
        "process": get_process_metrics(),
    }
