"""测试设备名称智能匹配功能."""

import sys
sys.path.insert(0, "src")

from jlink_mcp.flagchip_patch import flagchip_patch


def test_match_device_name():
    """测试设备名称匹配功能."""
    print("=" * 60)
    print("测试设备名称智能匹配")
    print("=" * 60)

    test_cases = [
        # (输入, 期望的完整名称)
        ("FC7300F4MDD", ["FC7300F4MDDxXxxxT1B", "FC7300F4MDDxXxxxT1C"]),
        ("FC7300F4MDS", ["FC7300F4MDSxXxxxT1B", "FC7300F4MDSxXxxxT1C"]),
        ("FC7300F8MDQ", ["FC7300F8MDQxXxxxT1B"]),
        ("FC7300F8MDT", ["FC7300F8MDTxXxxxT1B"]),
        ("FC7240F2M", ["FC7240F2MDSxXxxxT1A"]),
        ("FC4150F2M", ["FC4150F2MBSxXxxxT1A"]),
        ("FC4150F1M", ["FC4150F1MBSxXxxxT1A", "FC4150F1MBSxXxxxT1B", "FC4150F1MSxXxxxT2B"]),
        ("FC4150F512", ["FC4150F512BSxXxxxT1A"]),
        # 完整名称应该直接返回
        ("FC7300F4MDDxXxxxT1C", ["FC7300F4MDDxXxxxT1C"]),
        # 不存在的名称
        ("UNKNOWN_CHIP", []),
    ]

    all_passed = True
    for input_name, expected_options in test_cases:
        result = flagchip_patch.match_device_name(input_name)

        if expected_options:
            # 检查结果是否在预期选项中
            if result in expected_options:
                status = "✅ 通过"
            else:
                status = "❌ 失败"
                all_passed = False
            print(f"{status}: '{input_name}' -> '{result}' (期望: {expected_options})")
        else:
            # 期望返回 None
            if result is None:
                status = "✅ 通过"
            else:
                status = "❌ 失败"
                all_passed = False
            print(f"{status}: '{input_name}' -> {result} (期望: None)")

    print()
    return all_passed


def test_find_similar_devices():
    """测试查找相似设备功能."""
    print("=" * 60)
    print("测试查找相似设备")
    print("=" * 60)

    test_cases = [
        ("FC7300F4MDD", 3),
        ("FC4150", 5),
        ("FC7240", 3),
    ]

    for partial_name, limit in test_cases:
        results = flagchip_patch.find_similar_devices(partial_name, limit)
        print(f"\n查找 '{partial_name}' (最多 {limit} 个):")
        for name in results:
            print(f"  - {name}")

    print()
    return True


def test_get_suggestions():
    """测试获取设备建议功能."""
    print("=" * 60)
    print("测试获取设备名称建议")
    print("=" * 60)

    test_names = ["FC7300F4MDD", "FC4150F1M", "UNKNOWN"]

    for name in test_names:
        suggestion = flagchip_patch.get_device_name_suggestions(name)
        print(f"\n输入: '{name}'")
        print(suggestion)

    print()
    return True


def list_all_devices():
    """列出所有支持的设备."""
    print("=" * 60)
    print("支持的 Flagchip 设备列表")
    print("=" * 60)

    # 过滤掉解锁/工厂模式的设备，只显示普通设备
    normal_devices = [
        name for name in flagchip_patch.device_names
        if not any(keyword in name for keyword in ["Unlock", "Factory", "FromRom", "Core", "_64", "ETM"])
    ]

    print(f"\n共 {len(normal_devices)} 个设备:\n")

    # 按系列分组
    series = {}
    for name in normal_devices:
        # 提取系列名称 (如 FC7300F4MDD)
        if name.startswith("FC7300"):
            key = name[:11]  # FC7300F4MDD
        elif name.startswith("FC7240"):
            key = name[:10]  # FC7240F2M
        elif name.startswith("FC4150"):
            key = name[:10]  # FC4150F2M
        else:
            key = name[:6]

        if key not in series:
            series[key] = []
        series[key].append(name)

    for key, devices in sorted(series.items()):
        print(f"{key} 系列:")
        for dev in sorted(devices):
            print(f"  - {dev}")
        print()


def main():
    """主函数."""
    print("\n" + "=" * 60)
    print("Flagchip 设备名称智能匹配测试")
    print("=" * 60 + "\n")

    if not flagchip_patch.is_available():
        print("❌ Flagchip 补丁不可用，请检查 JLinkDevices.xml 文件")
        return 1

    print(f"✅ 已加载 {len(flagchip_patch.device_names)} 个设备\n")

    # 运行测试
    results = []
    results.append(("设备名称匹配", test_match_device_name()))
    results.append(("查找相似设备", test_find_similar_devices()))
    results.append(("获取设备建议", test_get_suggestions()))

    # 列出所有设备
    list_all_devices()

    # 汇总结果
    print("=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    for test_name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{status}: {test_name}")

    print("\n" + "=" * 60)
    if all(r[1] for r in results):
        print("✅ 所有测试通过!")
        return 0
    else:
        print("❌ 部分测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
