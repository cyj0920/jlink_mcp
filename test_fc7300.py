"""针对 FC7300F4MDSXXXXXT1C 芯片的实际硬件测试脚本."""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from jlink_mcp.tools import (
    list_jlink_devices,
    connect_device,
    disconnect_device,
    get_connection_status,
    get_target_info,
    get_target_voltage,
    scan_target_devices,
    list_flagchip_devices,
    read_memory,
    write_memory,
    read_registers,
    write_register,
    reset_target,
    halt_cpu,
    run_cpu,
    get_cpu_state
)
from jlink_mcp.utils import logger


def print_section(title):
    """打印章节标题."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_fc7300_hardware():
    """测试 FC7300F4MDSXXXXXT1C 硬件."""

    print_section("FC7300F4MDSXXXXXT1C 硬件测试")

    # 1. 列出所有 JLink 设备
    print("\n[1] 列出所有 JLink 设备:")
    devices = list_jlink_devices()
    if isinstance(devices, list) and len(devices) > 0:
        for dev in devices:
            print(f"   - 序列号: {dev['serial_number']}")
            print(f"     产品: {dev['product_name']}")
            print(f"     连接类型: {dev['connection_type']}")
    else:
        print(f"   ❌ 未找到 JLink 设备")
        return

    # 2. 列出 Flagchip 设备
    print("\n[2] 列出支持的 Flagchip 设备:")
    flagchip = list_flagchip_devices()
    if flagchip.get("success"):
        print(f"   找到 {flagchip['device_count']} 个 Flagchip 设备")
        # 检查 FC7300F4MDSXXXXXT1C 是否在列表中
        if "FC7300F4MDSxXxxxT1C" in flagchip["device_names"]:
            print("   ✅ FC7300F4MDSxXxxxT1C 在支持列表中")
        else:
            print("   ❌ FC7300F4MDSxXxxxT1C 不在支持列表中")
            print("   尝试使用 FC7300F4MDDxXxxxT1C（兼容型号）")
    else:
        print(f"   ❌ {flagchip.get('error', {}).get('description', '未知错误')}")

# 3. 连接到设备（使用 JTAG 接口，自动检测芯片）
    print("\n[3] 连接到设备 (JTAG + 自动检测):")
    # 不指定芯片名称，让 JLink 自动检测
    result = connect_device(
        serial_number="941000024",
        interface="JTAG",
        chip_name=None
    )
    if result.get("success"):
        print(f"   ✅ {result['message']}")
    else:
        print(f"   ❌ {result.get('error', {}).get('description', '连接失败')}")
        print(f"   建议: {result.get('error', {}).get('suggestion', '')}")
        return

    # 4. 获取连接状态
    print("\n[4] 获取连接状态:")
    status = get_connection_status()
    if status.get("success"):
        data = status["data"]
        print(f"   已连接: {data['connected']}")
        print(f"   设备序列号: {data['device_serial']}")
        print(f"   目标接口: {data['target_interface']}")
        print(f"   目标已连接: {data['target_connected']}")
        print(f"   目标电压: {data['target_voltage']}V")
        print(f"   固件版本: {data['firmware_version']}")
    else:
        print(f"   ❌ {status.get('error', {}).get('description', '未知错误')}")

    # 5. 获取设备信息
    print("\n[5] 获取设备信息:")
    info = get_target_info()
    if info.get("success"):
        data = info["data"]
        print(f"   设备名称: {data['device_name']}")
        print(f"   内核类型: {data['core_type']}")
        print(f"   内核 ID: {hex(data['core_id']) if data['core_id'] else 'N/A'}")
        print(f"   设备 ID: {hex(data['device_id']) if data['device_id'] else 'N/A'}")
        print(f"   Flash 大小: {data['flash_size']} 字节" if data['flash_size'] else '   Flash 大小: N/A')
        print(f"   RAM 大小: {data['ram_size']} 字节" if data['ram_size'] else '   RAM 大小: N/A')
    else:
        print(f"   ❌ {info.get('error', {}).get('description', '未知错误')}")

    # 6. 获取电压
    print("\n[6] 获取目标电压:")
    voltage = get_target_voltage()
    if voltage.get("success"):
        data = voltage["data"]
        print(f"   电压: {data['voltage_v']}V")
        print(f"   状态: {data['status']}")
    else:
        print(f"   ❌ {voltage.get('error', {}).get('description', '未知错误')}")

    # 7. 扫描目标设备
    print("\n[7] 扫描目标总线上的设备:")
    scan = scan_target_devices()
    if scan.get("success"):
        print(f"   找到 {scan['device_count']} 个设备")
        for i, dev_id in enumerate(scan["devices"], 1):
            print(f"   设备 {i}: ID = {hex(dev_id)}")
    else:
        print(f"   ❌ {scan.get('error', {}).get('description', '未知错误')}")

    # 8. 复位设备
    print("\n[8] 复位设备:")
    reset = reset_target(reset_type="normal")
    if reset.get("success"):
        print(f"   ✅ {reset['message']}")
    else:
        print(f"   ❌ {reset.get('error', {}).get('description', '未知错误')}")

    # 9. 暂停 CPU
    print("\n[9] 暂停 CPU:")
    halt = halt_cpu()
    if halt.get("success"):
        print(f"   ✅ {halt['message']}")
    else:
        print(f"   ❌ {halt.get('error', {}).get('description', '未知错误')}")

    # 10. 读取寄存器
    print("\n[10] 读取寄存器:")
    regs = read_registers(register_names=["R0", "R15 (PC)", "R13 (SP)"])
    if regs.get("success"):
        registers = regs["registers"]
        for reg in registers:
            print(f"   {reg['name']} = {hex(reg['value'])}")
    else:
        print(f"   ❌ {regs.get('error', {}).get('description', '未知错误')}")

    # 11. 暂停 CPU（确保 CPU 处于暂停状态，以便读取内存）
    print("\n[11] 暂停 CPU:")
    halt = halt_cpu()
    if halt.get("success"):
        print(f"   ✅ {halt['message']}")
    else:
        print(f"   ❌ {halt.get('error', {}).get('description', '未知错误')}")

    # 12. 运行 CPU
    print("\n[12] 运行 CPU:")
    run = run_cpu()
    if run.get("success"):
        print(f"   ✅ {run['message']}")
    else:
        print(f"   ❌ {run.get('error', {}).get('description', '未知错误')}")

    # 13. 获取 CPU 状态
    print("\n[13] 获取 CPU 状态:")
    state = get_cpu_state()
    if state.get("success"):
        state_data = state.get("state", {})
        print(f"   是否暂停: {state_data.get('is_halted', 'N/A')}")
        pc = state_data.get('pc')
        if pc is not None:
            print(f"   PC: {hex(pc)}")
        else:
            print(f"   PC: N/A")
    else:
        print(f"   ❌ {state.get('error', {}).get('description', '未知错误')}")

    # 14. 断开连接
    print("\n[14] 断开连接:")
    disconnect = disconnect_device()
    if disconnect.get("success"):
        print(f"   ✅ {disconnect['message']}")
    else:
        print(f"   ❌ {disconnect.get('error', {}).get('description', '未知错误')}")

    print("\n" + "=" * 60)
    print("  测试完成！")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    try:
        test_fc7300_hardware()
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()