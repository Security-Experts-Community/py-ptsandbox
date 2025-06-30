# PTSandbox Python Client

![PTSandbox Logo](https://raw.githubusercontent.com/Security-Experts-Community/py-ptsandbox/refs/heads/main/docs/assets/logo_with_text.svg)

<p align="center">
    <em>Full-featured async Python client for PT Sandbox instances</em>
</p>

<p align="center">
    <a href="https://pypi.org/project/ptsandbox"><img src="https://badgen.net/pypi/v/ptsandbox" alt="PyPI Version"></a>
    <a href="https://pypi.org/project/ptsandbox"><img src="https://badgen.net/pypi/python/ptsandbox" alt="Python Versions"></a>
    <a href="https://github.com/Security-Experts-Community/py-ptsandbox/blob/main/LICENSE"><img src="https://badgen.net/github/license/Security-Experts-Community/py-ptsandbox" alt="License"></a>
</p>

---

**Documentation**: <a href="https://security-experts-community.github.io/py-ptsandbox" target="_blank">https://security-experts-community.github.io/py-ptsandbox</a>

**Source Code**: <a href="https://github.com/Security-Experts-Community/py-ptsandbox" target="_blank">https://github.com/Security-Experts-Community/py-ptsandbox</a>

---

## 📖 Overview

PTSandbox Python Client is a modern async library for interacting with PT Sandbox through API. The library provides a convenient interface for submitting files and URLs for analysis, retrieving scan results, system management, and much more.

### ✨ Key Features

- **Fully Asynchronous** — all operations are performed in a non-blocking manner
- **Fully Typed** — complete type hints support for better development experience
- **Dual API Support** — both Public API and UI API for administrative tasks
- **Flexible File Upload** — support for various input data formats
- **High Performance** — optimized HTTP requests with connection pooling
- **Error Resilience** — built-in error handling and retry logic
- **Modern Python** — requires Python 3.11+

## 📦 Installation

### PyPI

```bash
python3 -m pip install ptsandbox
```

### uv (recommended)

```bash
uv add ptsandbox
```

### Nix

```bash
# Coming soon
```

## 🔧 Requirements

- Python 3.11+
- aiohttp 3.11.15+
- pydantic 2.11.1+
- loguru 0.7.3+

## 🚀 Quick Start

### Basic File Scanning

```python
import asyncio
from pathlib import Path
from ptsandbox import Sandbox, SandboxKey

async def main():
    # Create connection key
    key = SandboxKey(
        name="test-key-1",
        key="<TOKEN_FROM_SANDBOX>",
        host="10.10.10.10",
    )
    
    # Initialize client
    sandbox = Sandbox(key)
    
    # Submit file for analysis
    task = await sandbox.create_scan(Path("suspicious_file.exe"))
    
    # Wait for analysis completion
    result = await sandbox.wait_for_report(task)
    
    if (report := result.get_long_report()) is not None:
        print(report.result.verdict)

asyncio.run(main())
```

### URL Scanning

```python
import asyncio
from ptsandbox import Sandbox, SandboxKey

async def main():
    key = SandboxKey(
        name="test-key-1", 
        key="<TOKEN_FROM_SANDBOX>",
        host="10.10.10.10"
    )
    
    sandbox = Sandbox(key)
    
    # Scan suspicious URL
    task = await sandbox.create_url_scan("http://malware.com/malicious-file")
    result = await sandbox.wait_for_report(task)
    
    if (report := result.get_long_report()) is not None:
        print(report.result.verdict)

asyncio.run(main())
```

### Working with UI API (Administrative Functions)

```python
import asyncio
from ptsandbox import Sandbox, SandboxKey

async def main():
    key = SandboxKey(
        name="test-key-1",
        key="<TOKEN_FROM_SANDBOX>", 
        host="10.10.10.10",
        ui=SandboxKey.UI(
            login="login",
            password="password"
        )
    )
    
    sandbox = Sandbox(key)
    
    # Authorize in UI API
    await sandbox.ui.authorize()
    
    # Get system information
    system_info = await sandbox.ui.get_system_settings()
    print(f"System version: {system_info.data}")
    
    # Get tasks status
    tasks = await sandbox.ui.get_tasks()
    print(f"Active tasks: {len(tasks.tasks)}")

asyncio.run(main())
```

## 🛠️ Core Features

### Public API

- **[File Scanning](https://security-experts-community.github.io/py-ptsandbox/usage/public-api/scanning/default-scan/)** — submit files of any type for analysis
- **[URL Scanning](https://security-experts-community.github.io/py-ptsandbox/usage/public-api/scanning/scan/#url)** — check web links for threats  
- **[Advanced Scanning](https://security-experts-community.github.io/py-ptsandbox/usage/public-api/scanning/scan/#advanced-scan)** — configure analysis parameters (VM image, duration, commands)
- **[Rescan Analysis](https://security-experts-community.github.io/py-ptsandbox/usage/public-api/scanning/rescan/)** — analyze saved traces without re-execution
- **[File Downloads](https://security-experts-community.github.io/py-ptsandbox/usage/public-api/download-files/)** — retrieve original files and artifacts by hash
- **[System Information](https://security-experts-community.github.io/py-ptsandbox/usage/public-api/system/)** — get version and health status
- **[Email Analysis](https://security-experts-community.github.io/py-ptsandbox/usage/public-api/email/)** — extract and analyze email headers
- **[Source Checking](https://security-experts-community.github.io/py-ptsandbox/usage/public-api/scanning/source/)** — specialized source file analysis

### UI API (Administrative)

- **[Token Management](https://security-experts-community.github.io/py-ptsandbox/usage/ui-api/api-tokens/)** — create and manage API keys
- **[Entry Points](https://security-experts-community.github.io/py-ptsandbox/usage/ui-api/entry-points/)** — configure automatic processing rules
- **[Task Management](https://security-experts-community.github.io/py-ptsandbox/usage/ui-api/tasks/)** — view and manage scan queue
- **[System Settings](https://security-experts-community.github.io/py-ptsandbox/usage/ui-api/system/)** — configure sandbox parameters
- **[License Management](https://security-experts-community.github.io/py-ptsandbox/usage/ui-api/license/)** — manage licenses and restrictions
- **[Cluster Monitoring](https://security-experts-community.github.io/py-ptsandbox/usage/ui-api/cluster/)** — monitor cluster node status
- **[Component Management](https://security-experts-community.github.io/py-ptsandbox/usage/ui-api/components/)** — manage system modules
- **[Download Files](https://security-experts-community.github.io/py-ptsandbox/usage/ui-api/download-files/)** — download files and artifacts via UI API
- **[Artifacts](https://security-experts-community.github.io/py-ptsandbox/usage/ui-api/artifacts/)** — work with scan results and artifacts
- **[Antivirus Engines](https://security-experts-community.github.io/py-ptsandbox/usage/ui-api/antiviruses/)** — manage AV engine integrations
- **[Queue Management](https://security-experts-community.github.io/py-ptsandbox/usage/ui-api/baqueue/)** — monitor and manage scan queues
- **[Authorization](https://security-experts-community.github.io/py-ptsandbox/usage/ui-api/authorization/)** — handle UI API authentication

## 🔄 Advanced Usage

### Batch Scanning

```python
import asyncio
from pathlib import Path
from ptsandbox import Sandbox, SandboxKey

async def scan_multiple_files(files: list[Path]):
    sandbox = Sandbox(SandboxKey(...))
    
    # Submit all files in parallel
    tasks = []
    for file in files:
        task = await sandbox.create_scan(file, async_result=True)
        tasks.append(task)
    
    # Wait for all tasks to complete
    results = []
    for task in tasks:
        result = await sandbox.wait_for_report(task)
        results.append(result)
    
    return results
```

### Custom Scan Configuration

```python
from ptsandbox.models import SandboxBaseScanTaskRequest, SandboxOptions

# Configure scan options
options = SandboxBaseScanTaskRequest.Options(
    sandbox=SandboxOptions(
        image_id="ubuntu-jammy-x64",     # VM image selection
        analysis_duration=300,           # Analysis time in seconds
        custom_command="python3 {file}", # Custom execution command
        save_video=True,                 # Save process video
    )
)

task = await sandbox.create_scan(file, options=options)
```

### Advanced File Analysis

```python
from ptsandbox.models import SandboxOptionsAdvanced

# Advanced scanning with custom rules and extra files
task = await sandbox.create_advanced_scan(
    Path("malware.exe"),
    extra_files=[Path("config.ini"), Path("data.txt")],  # Additional files
    sandbox=SandboxOptionsAdvanced(
        image_id="win10-x64",
        analysis_duration=600,
        custom_command="python3 {file}",  # Custom execution command
        save_video=True,                  # Save process video
        mitm_enabled=True,                # Enable traffic decryption
        bootkitmon=False                  # Disable bootkitmon analysis
    )
)
```

### Error Handling

```python
from ptsandbox.models import (
    SandboxUploadException, 
    SandboxWaitTimeoutException,
    SandboxTooManyErrorsException
)

try:
    task = await sandbox.create_scan(large_file, upload_timeout=600)
    result = await sandbox.wait_for_report(task, wait_time=300)
except SandboxUploadException as e:
    print(f"Upload error: {e}")
except SandboxWaitTimeoutException as e:
    print(f"Timeout waiting for result: {e}")
except SandboxTooManyErrorsException as e:
    print(f"Too many errors occurred: {e}")
```

### Stream File Downloads

```python
# Download large files as stream
async for chunk in sandbox.get_file_stream("sha256_hash"):
    # Process chunk by chunk
    process_chunk(chunk)

# Get email headers
async for header_chunk in sandbox.get_email_headers(email_file):
    print(header_chunk.decode())
```

## 🔧 Configuration

### Proxy Support

```python
sandbox = Sandbox(
    key, 
    proxy="http://proxy.company.com:8080"
)
```

### Custom Timeouts

```python
from aiohttp import ClientTimeout

sandbox = Sandbox(
    key,
    default_timeout=ClientTimeout(
        total=600,
        connect=60,
        sock_read=300
    )
)
```

### Upload Semaphore Control

```python
# Limit concurrent uploads
sandbox = Sandbox(
    key,
    upload_semaphore_size=3  # Max 3 concurrent uploads
)
```

## 🤝 Contributing

We welcome contributions to the project! Whether you're fixing bugs, adding features, improving documentation, or helping other users, every contribution is valuable.

Please read our [Contributing Guide](CONTRIBUTING.md) for detailed information.

## 📋 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Documentation**: [https://security-experts-community.github.io/py-ptsandbox](https://security-experts-community.github.io/py-ptsandbox)
- **Issues**: [GitHub Issues](https://github.com/Security-Experts-Community/py-ptsandbox/issues)

## 🙏 Acknowledgments

- **PT ESC Malware Detection** — PT Sandbox development team
- **Security Experts Community** — information security experts community
- All project contributors

---

<p align="center">
    <img width="60%" src="https://raw.githubusercontent.com/Security-Experts-Community/py-ptsandbox/refs/heads/main/docs/assets/pic_right.svg">
</p>