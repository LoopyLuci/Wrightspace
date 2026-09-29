"""webbuilder.hardware.detector — Hardware.Detector."""

from __future__ import annotations
import os
from dataclasses import dataclass, field


@dataclass
class CPUInfo:
    cores_logical: int = 1
    cores_physical: int = 1
    brand: str = ""


@dataclass
class MemoryInfo:
    total_gb: float = 0.0
    available_gb: float = 0.0


@dataclass
class GPUInfo:
    name: str = ""
    memory_mb: float = 0.0


@dataclass
class HardwareInfo:
    cpu: CPUInfo = field(default_factory=CPUInfo)
    memory: MemoryInfo = field(default_factory=MemoryInfo)
    gpus: list[GPUInfo] = field(default_factory=list)


class HardwareDetector:
    def detect(self, force: bool = False) -> HardwareInfo:
        try:
            import psutil
            cpu = CPUInfo(
                cores_logical=psutil.cpu_count(logical=True) or 1,
                cores_physical=psutil.cpu_count(logical=False) or 1,
                brand="",
            )
            mem = psutil.virtual_memory()
            memory = MemoryInfo(
                total_gb=round(mem.total / (1024**3), 2),
                available_gb=round(mem.available / (1024**3), 2),
            )
        except ImportError:
            cpu = CPUInfo(
                cores_logical=os.cpu_count() or 1,
                cores_physical=os.cpu_count() or 1,
                brand="",
            )
            memory = self._detect_memory_fallback()
        return HardwareInfo(cpu=cpu, memory=memory, gpus=[])

    def _detect_memory_fallback(self) -> MemoryInfo:
        try:
            import ctypes

            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ('dwLength', ctypes.c_ulong),
                    ('dwMemoryLoad', ctypes.c_ulong),
                    ('ullTotalPhys', ctypes.c_ulonglong),
                    ('ullAvailPhys', ctypes.c_ulonglong),
                    ('ullTotalPageFile', ctypes.c_ulonglong),
                    ('ullAvailPageFile', ctypes.c_ulonglong),
                    ('ullTotalVirtual', ctypes.c_ulonglong),
                    ('ullAvailVirtual', ctypes.c_ulonglong),
                    ('ullAvailExtendedVirtual', ctypes.c_ulonglong),
                ]

            kernel32 = ctypes.windll.kernel32
            mem_status = MEMORYSTATUSEX()
            mem_status.dwLength = ctypes.sizeof(mem_status)
            if kernel32.GlobalMemoryStatusEx(ctypes.byref(mem_status)):
                return MemoryInfo(
                    total_gb=round(mem_status.ullTotalPhys / (1024**3), 2),
                    available_gb=round(mem_status.ullAvailPhys / (1024**3), 2),
                )
        except Exception:
            pass
        return MemoryInfo(total_gb=0.0, available_gb=0.0)
