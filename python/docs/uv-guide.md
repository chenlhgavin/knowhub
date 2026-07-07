# uv 完全指南 — 安装、使用与 conda 对比

uv 是 Astral 团队（ruff 的作者）用 Rust 开发的 Python 包管理工具，替代 pip + venv + pyenv + pip-tools 的全家桶。速度快一个数量级，且与 PyPI 生态完全兼容。

---

## uv vs conda 对比

### 定位

| | uv | conda |
|---|---|---|
| 出品 | Astral（ruff 团队） | Anaconda / conda-forge |
| 实现语言 | Rust | Python |
| 定位 | Python 包管理器 + 虚拟环境 | 跨语言包管理器 + 环境管理 |
| 替代 | pip + pip-tools + venv + pyenv | pip + venv + 系统级 C 库管理 |

### 速度

uv 用 Rust 实现，依赖解析和安装速度比 conda 快一个数量级：

```bash
# uv 创建环境 + 安装依赖，通常秒级完成
uv venv .venv && uv pip install flask  # ~1-2s

# conda 同样操作，解析依赖就要几十秒
conda create -n myenv flask            # ~30-120s
```

conda 慢主要因为它的 SAT 求解器要处理跨语言依赖（C/C++/Fortran 库），复杂度更高。

### 包源

| | uv | conda |
|---|---|---|
| 默认源 | PyPI（wheel/sdist） | conda channels（conda 包格式） |
| 包数量 | PyPI 50万+ | conda-forge ~3万 |
| 非 Python 依赖 | 不管，依赖系统 | 自带（CUDA、MKL、libssl 等） |

这是 conda 的核心优势——它能管理 Python 生态之外的二进制依赖：

```bash
# conda 可以直接装特定版本的 CUDA toolkit
conda install cuda-toolkit=12.1

# uv 做不到这个，需要自行安装系统级依赖
```

### 环境隔离方式

uv 的 venv 就是软链接 + site-packages，几 MB。conda 环境是完整的目录树，包含 bin/lib/include，几百 MB 起步。

### 适用场景

**选 uv：**
- 纯 Python 项目（Web、CLI、SDK 开发）
- CI/CD 流水线（速度快）
- 需要和 pip/PyPI 生态完全兼容
- 追求轻量和速度

**选 conda：**
- 数据科学 / 机器学习（numpy、scipy、pytorch 等依赖大量 C 库）
- 需要管理 CUDA、MKL、OpenSSL 等系统级依赖
- 跨平台一致性要求高（conda 包是预编译的）
- 团队已有 conda 工作流

### 混用

可以在 conda 环境里用 uv 装 PyPI 包：

```bash
conda activate myenv
uv pip install some-pypi-only-package
```

反过来不行——uv 环境里没法用 conda install。混用时 conda 管系统级依赖，uv 管纯 Python 包，各司其职。

### 总结

uv 是更快更现代的 pip 替代品，conda 是带系统级依赖管理的重型方案。对于纯 Python 项目（如 Claude Agent SDK），uv 完全够用且体验更好；涉及科学计算和 GPU 依赖时，conda 的优势不可替代。

---

## uv 常用命令速查

### 1. 安装 uv

```bash
# Linux / macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# pip 安装
pip install uv

# Homebrew
brew install uv

# 查看版本
uv --version
```

### 2. Python 版本管理（替代 pyenv）

```bash
# 查看可安装的 Python 版本
uv python list

# 安装指定版本
uv python install 3.12
uv python install 3.11 3.13    # 同时装多个

# 查看已安装的版本
uv python list --only-installed

# 固定项目 Python 版本（写入 .python-version）
uv python pin 3.12
```

### 3. 虚拟环境管理（替代 venv）

```bash
# 创建虚拟环境（默认 .venv 目录）
uv venv

# 指定目录和 Python 版本
uv venv .venv --python 3.12

# 激活环境
source .venv/bin/activate      # Linux/macOS
.venv\Scripts\activate         # Windows

# 不激活也能用，uv 命令会自动检测 .venv
uv pip install flask           # 自动装到 .venv 里
```

### 4. 包管理 — pip 兼容模式（替代 pip）

```bash
# 安装包
uv pip install flask
uv pip install "flask>=3.0"
uv pip install flask uvicorn gunicorn    # 多个包

# 从 requirements.txt 安装
uv pip install -r requirements.txt

# 安装本地包（开发模式）
uv pip install -e .
uv pip install -e ./vendors/claude-agent-sdk-python

# 卸载
uv pip uninstall flask

# 查看已安装的包
uv pip list
uv pip show flask

# 导出当前环境
uv pip freeze > requirements.txt
```

### 5. 项目管理（替代 pip-tools + 手动管理）

```bash
# 初始化新项目（生成 pyproject.toml）
uv init myproject
uv init --lib mylib            # 库项目
uv init --script myscript.py   # 脚本项目

# 添加依赖（自动写入 pyproject.toml + 更新 uv.lock）
uv add flask
uv add "sqlalchemy>=2.0"
uv add pytest --dev            # 开发依赖

# 移除依赖
uv remove flask

# 同步环境（根据 uv.lock 安装精确版本）
uv sync

# 更新锁文件
uv lock

# 查看依赖树
uv tree
```

### 6. 运行命令（替代手动激活环境）

```bash
# 在项目环境中运行命令，无需手动 activate
uv run python app.py
uv run pytest
uv run flask run

# 运行单文件脚本（自动处理依赖）
uv run script.py

# 脚本内联依赖（PEP 723）
# script.py 文件头部：
# /// script
# dependencies = ["requests"]
# ///
uv run script.py               # 自动安装 requests 并运行
```

### 7. 锁文件与可复现构建（替代 pip-tools）

```bash
# 从 requirements.in 生成精确锁文件
uv pip compile requirements.in -o requirements.lock

# 按锁文件精确安装（移除多余包）
uv pip sync requirements.lock

# 项目模式下自动管理
uv lock                        # 生成 uv.lock
uv sync                        # 按 uv.lock 同步环境
uv export > requirements.txt   # 导出为 requirements.txt 格式
```

### 8. 全局工具管理（替代 pipx）

```bash
# 安装全局 CLI 工具
uv tool install ruff
uv tool install black
uv tool install httpie

# 临时运行（不安装）
uv tool run ruff check .
uvx ruff check .               # uvx 是 uv tool run 的简写

# 查看已安装的工具
uv tool list

# 卸载
uv tool uninstall ruff
```

### 9. 缓存管理

```bash
# 查看缓存大小
uv cache dir
uv cache info

# 清理缓存
uv cache clean
uv cache clean flask           # 只清理特定包

# 临时禁用缓存
uv pip install flask --no-cache
```

### 10. 常用配置

通过 `uv.toml` 或 `pyproject.toml` 中的 `[tool.uv]` 配置：

```toml
# pyproject.toml
[tool.uv]
python-preference = "managed"  # 优先用 uv 管理的 Python

# 配置国内镜像源
[[tool.uv.index]]
url = "https://mirrors.aliyun.com/pypi/simple/"
default = true
```

环境变量方式：

```bash
# 设置镜像源
export UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/

# 设置缓存目录
export UV_CACHE_DIR=/tmp/uv-cache
```

---

## 典型工作流

### 新项目从零开始

```bash
uv init myproject && cd myproject
uv add flask sqlalchemy
uv add pytest --dev
uv run flask run
```

### 接手已有项目

```bash
git clone <repo> && cd <repo>
uv sync                        # 根据 uv.lock 还原环境
uv run pytest                  # 跑测试
```

### 快速实验

```bash
uv venv /tmp/experiment
uv pip install --python /tmp/experiment pandas matplotlib
/tmp/experiment/bin/python -c "import pandas; print(pandas.__version__)"
```

---

## uv 命令与传统工具对照

| 传统工具 | uv 等价命令 |
|---|---|
| `python -m venv .venv` | `uv venv` |
| `pip install flask` | `uv pip install flask` / `uv add flask` |
| `pip freeze` | `uv pip freeze` |
| `pip-compile` | `uv pip compile` / `uv lock` |
| `pip-sync` | `uv pip sync` / `uv sync` |
| `pyenv install 3.12` | `uv python install 3.12` |
| `pipx install ruff` | `uv tool install ruff` |
| `pipx run ruff` | `uvx ruff` |
