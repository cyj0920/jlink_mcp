# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-03-09

### Added

#### Core Features
- 🎯 **J-Link Device Connection**
  - Support for SWD and JTAG interfaces
  - Automatic chip detection and name matching
  - Connection status monitoring
  - Target device information retrieval

- 💾 **Memory Operations**
  - Read memory with configurable access widths (8/16/32-bit)
  - Write memory operations
  - Memory dump capabilities

- 🔥 **Flash Programming**
  - Flash erase (range and chip erase)
  - Flash programming with data verification
  - Flash content verification

- 🎯 **Debug Control**
  - CPU halt and resume
  - Single-step instruction execution
  - CPU state monitoring
  - Target reset (normal, halt, core modes)
  - Breakpoint management (set/clear)

- 📊 **Register Access**
  - Read CPU registers
  - Write to CPU registers
  - Bulk register read operations

- 📡 **RTT (Real-Time Transfer)**
  - RTT buffer management
  - Real-time data read/write
  - RTT status monitoring

- 🔧 **SVD Integration**
  - System View Description file support
  - Peripheral register access with field parsing
  - SVD file scanning and device detection
  - Register value parsing with bit field interpretation

- 🧩 **Plugin Architecture**
  - Device patch interface for vendor-specific support
  - Device patch manager for multiple patch plugins
  - Extensible plugin system for new devices
  - External patch directory support via environment variables

- 🌐 **GDB Server**
  - Integrated GDB server support
  - GDB server configuration and management

#### Documentation
- 📚 **Comprehensive README**
  - Bilingual documentation (English and Chinese)
  - Feature overview with detailed descriptions
  - Installation guide (PyPI, source, UV)
  - Configuration instructions
  - Usage examples for all features
  - API reference documentation
  - Troubleshooting guide
  - Plugin development guide

- 📖 **API Documentation**
  - Complete function reference
  - Parameter descriptions
  - Usage examples
  - Architecture diagrams

#### Development Tools
- 🧪 **Testing Framework**
  - Unit tests for core functionality
  - Performance testing suite
  - Mock testing infrastructure

- 🔨 **Build System**
  - Hatchling-based build configuration
  - Python 3.10+ support
  - PyPI package distribution

#### Configuration
- ⚙️ **Environment Variables**
  - `JLINK_SVD_DIR` - External SVD directory
  - `JLINK_PATCH_DIR` - External device patch directory
  - `JLINK_DEFAULT_INTERFACE` - Default interface type

### Architecture

```
JLink MCP Server
├── Server Manager
├── Tool Layer
│   ├── Connection
│   ├── Debug
│   ├── Memory
│   ├── Flash
│   ├── Registers
│   ├── SVD
│   └── RTT
├── Manager Layer
│   ├── JLink Manager
│   ├── SVD Manager
│   └── Patch Manager
├── Plugin Layer
│   └── Device Patch Interface
└── Hardware Layer
    ├── pylink-square
    └── J-Link SDK
```

### Technical Details

- **Python Version**: 3.10+
- **Dependencies**:
  - pylink-square >= 2.0.0
  - mcp >= 1.26.0
  - pydantic >= 2.12.0
  - pydantic-settings >= 2.12.0

- **License**: MIT
- **Author**: cyj0920
- **Email**: cyjie0920@gmail.com

### Platforms Supported

- Windows
- Linux
- macOS

### Debuggers Supported

- All J-Link debuggers
- J-Trace debuggers

### Device Support

- Extensible plugin system for vendor-specific devices
- SVD-based register access for supported devices
- Custom device patches via plugin architecture

### Installation

```bash
pip install jlink-mcp
```

### Quick Start

```python
from jlink_mcp import connect_device, read_memory

# Connect to device
connect_device(chip_name="auto", interface="JTAG")

# Read memory
data = read_memory(address=0x20000000, size=64, width=32)
```

### PyPI Publication

- Package Name: `jlink-mcp`
- Version: `0.1.0`
- PyPI URL: https://pypi.org/project/jlink-mcp/

### GitHub Repository

- Repository: https://github.com/cyj0920/jlink_mcp
- Issues: https://github.com/cyj0920/jlink_mcp/issues

---

## Future Enhancements

### Planned Features

- [ ] Enhanced RTT performance optimization
- [ ] Support for more device vendors
- [ ] Advanced breakpoint management
- [ ] Memory watchpoints
- [ ] Trace support (ETM/ITM)
- [ ] Performance profiling integration
- [ ] Automated testing improvements
- [ ] Additional documentation and tutorials

### Community Contributions

Contributions are welcome! Please see the [README](README.md#contributing) for guidelines.

---

## Version History

### [0.1.0] - 2026-03-09
- Initial public release
- Core J-Link functionality
- Plugin architecture implementation
- Comprehensive documentation
- PyPI publication

---

## Links

- [Project Homepage](https://github.com/cyj0920/jlink_mcp)
- [PyPI Package](https://pypi.org/project/jlink-mcp/)
- [Documentation](https://github.com/cyj0920/jlink_mcp#readme)
- [Issue Tracker](https://github.com/cyj0920/jlink_mcp/issues)
- [License](LICENSE)

---

**Made with ❤️ for the embedded development community**

**为嵌入式开发社区用❤️打造**