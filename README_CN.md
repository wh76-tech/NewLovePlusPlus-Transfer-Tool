# New LovePlus+ Save Transfer Tool (NEWラブプラス＋ 存档引继助手)

[ [English](README.md) | [中文说明](README_CN.md) ]

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%203DS%20%7C%20Citra%20%7C%20Azahar-green.svg)]()
[![Python](https://img.shields.io/badge/Python-3.9%2B-orange.svg)]()

专为 **3DS《NEWラブプラス＋》（NEW LovePlus+，Title ID: `00040000000F4E00`）** 打造的 NDS 存档免卡带引继工具与 LayeredFS 补丁。

支持将从 **DraStic 模拟器（`.dsv`）** 或 **NDS 烧录卡 / 模拟器（`.sav`）** 导出的《LovePlus+》（Title ID: `BOXJ`）存档，完美无缝继承至电脑模拟器（Azahar / Citra / Lime3DS）或 3DS 真实主机中！

---

## 📖 项目背景与原理

### 1. 模拟器无法直接继承的原因
官方 3DS 工具《NEWラブプラス＋セーブデータ引継ぎツール》（Title ID: `0004000000120D00`）依赖 3DS 底层硬件读取插入 Slot-1 卡槽的 NDS 实体卡带（通过 `fs:USER` 的 SPI 接口）。

在 Citra / Azahar 等 3DS 模拟器中，由于不支持 NDS 卡槽硬件模拟，启动引继工具时会卡在检测卡带界面，并弹出提示：
> **「ラブプラスのDSゲームカードを確認できませんでした。引継ぎを行うには、『ラブプラス』か『ラブプラス+』のDSゲームカードを挿してください。」**

### 2. 逆向工程与代码洞（Code Cave）补丁实现
本项目通过对引继工具 ARM11 核心程序 `exefs/code.bin` 进行反编译和逆向分析，实现了以下四项底层热补丁（LayeredFS IPS 补丁，仅 333 字节）：

1. **卡槽插入检测 Patch (`0x002d315c`)**：
   强制函数始终返回 `1`，向系统报告 NDS 卡槽已插入卡带。
2. **卡带型号识别 Patch (`0x0036d0e8`)**：
   Hook 异步检测线程回调，向卡带信息结构体写入《LovePlus+》（GameType: 4, Title ID: `BOXJ`, 存档大小: 256KB）。
3. **状态机轮询旁路 Patch (`0x0036ed54`)**：
   绕过 Substate 1 的硬件等待循环，直接跃迁至 Substate 4（数据读取与转换准备）。
4. **SDMC 重定向代码洞 Patch (`0x0037022c` -> `0x003d61b0`)**：
   将原本通过 SPI 读取 Slot-1 卡带物理扇区的函数重定向至我们注入的代码洞中。代码洞调用 3DS 系统的 `FSUSER_OpenFileDirectly` 接口直接打开虚拟 SD 卡中的 `sdmc:/lpp.sav`，并调用 `FSFILE_Read` 将 256KB 存档读入内存缓冲区。

**核心优势**：直接由 Konami 官方引继工具的核心算法在 3DS 环境下执行女朋友数据解压、好感度/交往天数/纪念日转换以及 ExtData 校验和计算，保证生成的 3DS 存档（`00000F4E`）100% 原生合法，永不损坏。

---

## ✨ 主要功能

- 🌐 **完整中英双语支持**：界面右上角一键实时切换语言。
- 🖥️ **一键式图形界面应用程序**：无需配置 Python 环境，双击 `NEW_LovePlus+_Transfer_Tool.exe` 即可使用。
- 🔍 **智能格式识别与校准**：
  - 自动识别 DraStic 导出的 `.dsv` 存档并剔除末尾 122 字节 DeSmuME 标识。
  - 自动将各类烧录卡导出的存档校准为标准的 256KB（`0x40000`）格式。
- 🚀 **一键部署到模拟器**：
  - 自动探测本机已安装的 **Azahar**、**Citra**、**Lime3DS**、**Mandarine** 模拟器数据路径。
  - 自动创建 LayeredFS 补丁目录（`load/mods/0004000000120D00/code.ips`）与 SDMC 存档文件。
- 🎮 **实机与多端支持**：
  - 支持直接将补丁与存档一键写入真实 3DS 的 SD 卡（兼容 Luma3DS LayeredFS）。
  - 支持导出免安装独立 `.zip` 压缩包，方便发送给手机 Citra / Lime3DS 用户。

---

## 🚀 使用方法

### 方式一：使用 GUI 桌面助手（推荐）

1. 下载并运行 [`NEW_LovePlus+_Transfer_Tool.exe`](NEW_LovePlus+_Transfer_Tool.exe)。
2. **第一步**：点击“浏览文件”选择您的《LovePlus+》存档文件（支持 DraStic 的 `lpp.dsv` 或任意 `.sav`）。
3. **第二步**：选择目标环境（默认会自动选中已检测到的 Azahar / Citra 模拟器）。
4. 点击 **【🚀 一键部署 / 导出】** 按钮。
   > 💡 **程序自动执行**：工具会自动将 `code.ips` 免卡带补丁写入模拟器的 mods 目录（`load/mods/0004000000120D00/code.ips`），并将校准后的存档写入 `sdmc/lpp.sav`，无需手动复制文件或新建文件夹！
5. 打开模拟器运行《NEWラブプラス＋セーブデータ引継ぎツール》（引继工具）。
6. 屏幕将显示：
   > **『ラブプラス＋』のDSゲームカードを確認しました。引継ぎを行いますか？**
7. 触摸下屏点击 **【はい】** 确认复制数据。
8. 提示引继完成后，启动《NEW LovePlus+》（新爱相随+）游戏本体，在标题菜单点击 **「继承《爱相随》《爱相随+》的存档」（『ラブプラス』『ラブプラス＋』のデータを引き継ぐ）**，等待进度条读取跑完，女友数据即完美继承！

---

### 方式二：手动配置（模拟器 / 3DS 实机）

如果您希望手动放置文件，请按如下路径配置：

#### 1. 电脑模拟器（Azahar / Citra / Lime3DS）
- **存档路径**：将提取出的 256KB 存档重命名为 `lpp.sav`，放置在模拟器数据目录下的 `sdmc/lpp.sav`。
- **补丁路径**：将 `code.ips` 直接放入游戏 Title ID 文件夹即可（无需新建 `exefs` 子文件夹，与真实 3DS 实机保持统一；放入 `exefs/` 亦兼容）：
  ```text
  <模拟器数据目录>/load/mods/0004000000120D00/code.ips
  ```
  *(或 `<模拟器数据目录>/load/mods/0004000000120D00/exefs/code.ips`)*

#### 2. 真实 3DS 主机（Luma3DS）
- **存档路径**：将 256KB 存档命名为 `lpp.sav`，放置在 3DS 的 **SD 卡根目录**（`SD:/lpp.sav`）。
- **补丁路径**：将 `code.ips` 放到：
  ```text
  SD:/luma/titles/0004000000120D00/code.ips
  ```
- 开机时长按 `Select` 确保勾选了 **"Enable game patching"**。

#### 3. 手机模拟器（Android Citra / Lime3DS）
- **存档路径**：`/citra-emu/sdmc/lpp.sav`
- **补丁路径**：`/citra-emu/load/mods/0004000000120D00/code.ips` (或 `/citra-emu/load/mods/0004000000120D00/exefs/code.ips`)

---

## 🛠️ 从源码构建

如果您希望自行从源码修改或打包：

```bash
# 1. 克隆本仓库
git clone https://github.com/wh76-tech/NewLovePlusPlus-Transfer-Tool.git
cd NewLovePlusPlus-Transfer-Tool

# 2. 安装 Python 依赖
pip install -r requirements.txt

# 3. 运行桌面程序
python app.py

# 4. 重新构建 LayeredFS code.ips 补丁
python build_ips.py

# 5. 使用 PyInstaller 打包为单文件 .exe
pyinstaller --onefile --noconsole --name "NEW_LovePlus+_Transfer_Tool" --icon="app_icon.ico" --add-data "app_icon.ico;." app.py
```

---

## ⚠️ 免责声明 (Disclaimer)

1. 本项目仅包含逆向补丁算法代码与部署脚本，**不包含任何任天堂（Nintendo）或科乐美（Konami）的受版权保护的原版 ROM 二进制文件**。
2. 本工具仅供个人学习研究逆向工程及合法数据备份之用，请在支持正版游戏的前提下使用。
3. 《NEWラブプラス＋》及《ラブプラス＋》的商标与版权归属 Konami Digital Entertainment。

---

## 💖 鸣谢与致谢 (Credits)

- **[wh76-tech](https://github.com/wh76-tech)** - 项目发起者、测试与维护。
- **[Google Antigravity](https://deepmind.google/)** - 协助完成 ARM11 逆向工程分析、代码洞（Code Cave）底层补丁编写与桌面工具开发。
- **[Konami Digital Entertainment](https://www.konami.com/)** - 《LovePlus+》与《NEW LovePlus+》原作制作方。
- **3DS 模拟器与自制系统社区**（Citra、Azahar、Lime3DS 及 Luma3DS 团队）- 提供出色的运行与补丁平台。

---

## 📄 开源许可证

本项目基于 [MIT License](LICENSE) 开源。
