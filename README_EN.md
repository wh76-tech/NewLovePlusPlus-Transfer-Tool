# New LovePlus+ Save Transfer Tool (NEWラブプラス＋ 存档引继助手)

[ [English](README_EN.md) | [中文说明](README.md) ]

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%203DS%20%7C%20Citra%20%7C%20Azahar-green.svg)]()
[![Python](https://img.shields.io/badge/Python-3.9%2B-orange.svg)]()

A dedicated NDS save transfer tool and LayeredFS code patch for **Nintendo 3DS《NEW LovePlus+》（NEWラブプラス＋, Title ID: `00040000000F4E00`）**.

Seamlessly transfer your *LovePlus+* (Title ID: `BOXJ`) save files from **DraStic emulator (`.dsv`)** or **standard NDS flashcarts/emulators (`.sav`)** directly into 3DS emulators (Azahar, Citra, Lime3DS, etc.) or real 3DS hardware—**without requiring a physical Slot-1 NDS cartridge**!

---

## 📖 Background & Reverse Engineering Breakdown

### 1. The Hardware Barrier on 3DS Emulators
The official Konami transfer utility 《NEWラブプラス＋セーブデータ引継ぎツール》（*NEW LovePlus+ Save Data Transfer Tool*, Title ID: `0004000000120D00`）was designed to read the physical NDS cartridge inserted into the 3DS Slot-1 via `fs:USER` SPI commands.

Because 3DS emulators (Azahar, Citra, Lime3DS, Mandarine, etc.) do not emulate the Slot-1 physical hardware SPI interface, running the transfer utility triggers a hardware check failure:
> **「ラブプラスのDSゲームカードを確認できませんでした。引継ぎを行うには、『ラブプラス』か『ラブプラス+』のDSゲームカードを挿してください。」**  
> *(Could not detect LovePlus DS game card. Please insert LovePlus or LovePlus+ card.)*

### 2. Reverse Engineering & Code Cave Hot Patch
By disassembling and reverse-engineering the ARM11 executable (`exefs/code.bin`) of the official transfer tool, we designed a lightweight 333-byte LayeredFS IPS patch (`code.ips`):

1. **Card Insertion Patch (`0x002d315c`)**:
   Forces `CardSlotIsInserted` to unconditionally return `1`.
2. **Card Type Detection Patch (`0x0036d0e8`)**:
   Hooks the async card detection thread callback to populate the detector struct as *LovePlus+* (`GameType: 4`, Title ID: `BOXJ`, Save Size: `0x40000` = 256KB).
3. **State Machine Bypass Patch (`0x0036ed54`)**:
   Bypasses the physical hardware poll loop in Title Substate 1, jumping directly to Substate 4 (data preparation).
4. **SDMC Code Cave Loader (`0x0037022c` -> `0x003d61b0`)**:
   Hooks `ReadSaveDataFromCard` (which originally called the SPI driver `0x002fcf44`) to jump into our custom code cave. The cave uses the 3DS filesystem service (`FSUSER_OpenFileDirectly`) to open `sdmc:/lpp.sav` from the virtual SD card, and calls `FSFILE_Read` to load the 256KB save directly into the game's allocated memory buffer (`[r4, #0x78]`).

**Why this is the best solution**:
The official Konami transfer tool executes its native girlfriend data LZ77 decompression, boyfriend statistics calculation, and ExtData checksum generation inside the 3DS environment. The generated 3DS ExtData (`00000F4E`) is **100% native, legitimate, and will never corrupt or trigger integrity checks**.

---

## ✨ Features

- 🌐 **Full Bilingual Support (English & Chinese)**: Real-time one-click language switching.
- 🖥️ **Standalone GUI Desktop Application**: No Python installation required—run `NEW_LovePlus+_Transfer_Tool.exe` directly on Windows.
- 🔍 **Smart Format Detection & Calibration**:
  - Automatically identifies DraStic `.dsv` files and strips the 122-byte DeSmuME footer.
  - Calibrates any flashcart save to the standard 256KB (`0x40000`) EEPROM format.
- 🚀 **One-Click Emulator Auto-Injection**:
  - Automatically locates **Azahar**, **Citra**, **Lime3DS**, and **Mandarine** user data directories.
  - Automatically deploys the LayeredFS patch (`load/mods/0004000000120D00/exefs/code.ips`) and SDMC save file (`sdmc/lpp.sav`).
- 🎮 **Real 3DS & Multi-Platform Support**:
  - Automatically formats and writes Luma3DS LayeredFS patches to real 3DS SD cards.
  - Exports an all-in-one portable `.zip` package for Android Citra / Lime3DS users.

---

## 🚀 Quick Start Guide

### Method 1: Using the GUI Desktop Tool (Recommended)

1. Download and run [`NEW_LovePlus+_Transfer_Tool.exe`](NEW_LovePlus+_Transfer_Tool.exe).
2. **Step 1**: Click **Browse...** to select your *LovePlus+* save file (supports DraStic `lpp.dsv` or any `.sav`).
3. **Step 2**: Choose your deployment target (automatically detects your installed Azahar / Citra emulator).
4. Click **【🚀 Deploy / Export Now】**.
5. Launch your 3DS emulator and open **《NEWラブプラス＋セーブデータ引継ぎツール》** (*Transfer Tool*).
6. The on-screen prompt will confirm:
   > **『ラブプラス＋』のDSゲームカードを確認しました。引継ぎを行いますか？**  
   > *(LovePlus+ DS game card confirmed. Proceed with transfer?)*
7. Tap **【はい】** (Yes) on the touchscreen to copy data.
8. Once complete, launch 《NEWラブプラス＋》（*NEW LovePlus+*）—your girlfriend's data, affection, anniversary dates, and memories are seamlessly carried over!

---

### Method 2: Manual Installation (Emulator / Real 3DS)

If you prefer placing files manually:

#### 1. PC Emulators (Azahar / Citra / Lime3DS)
- **Save file**: Rename your 256KB save to `lpp.sav` and place it in `<Emulator_Data_Dir>/sdmc/lpp.sav`.
- **Patch file**: Copy `code.ips` to:
  ```text
  <Emulator_Data_Dir>/load/mods/0004000000120D00/exefs/code.ips
  ```

#### 2. Real 3DS Hardware (Luma3DS Custom Firmware)
- **Save file**: Place the 256KB save at the **root of your 3DS SD card** as `SD:/lpp.sav`.
- **Patch file**: Copy `code.ips` to:
  ```text
  SD:/luma/titles/0004000000120D00/code.ips
  ```
- Hold `Select` while powering on your 3DS and ensure **"Enable game patching"** is enabled in Luma3DS configuration.

#### 3. Android Emulators (Citra / Lime3DS Mobile)
- **Save path**: `/citra-emu/sdmc/lpp.sav`
- **Patch path**: `/citra-emu/load/mods/0004000000120D00/exefs/code.ips`

---

## 🛠️ Building from Source

To build or modify the project from source:

```bash
# 1. Clone this repository
git clone https://github.com/wh76-tech/NewLovePlusPlus-Transfer-Tool.git
cd NewLovePlusPlus-Transfer-Tool

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Run the GUI application
python app.py

# 4. Rebuild the LayeredFS code.ips patch using Keystone/Capstone
python build_ips.py

# 5. Compile into a standalone Windows executable with PyInstaller
pyinstaller --onefile --noconsole --name "NEW_LovePlus+_Transfer_Tool" --icon="app_icon.ico" --add-data "app_icon.ico;." app.py
```

---

## ⚠️ Disclaimer

1. This project only provides reverse-engineered assembly patch algorithms and deployment utilities. **No copyrighted Nintendo 3DS or Konami game ROMs/binaries are included**.
2. This tool is intended for personal research, educational reverse engineering, and legitimate data backup purposes only.
3. *NEW LovePlus+* and *LovePlus+* are registered trademarks of Konami Digital Entertainment.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
