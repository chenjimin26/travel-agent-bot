"""
美团旅行 CLI 工具
"""
import subprocess


def call_meituan(city: str, query: str, timeout: int = 120) -> str:
    """调用 mttravel CLI，返回查询结果"""
    proc = subprocess.Popen(
        ["mttravel", city, query],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True
    )
    try:
        stdout, _ = proc.communicate(timeout=timeout)
        return stdout.strip()
    except subprocess.TimeoutExpired:
        proc.kill()
        return "查询超时，请稍后重试"
    finally:
        proc.terminate()
