import os
import sys
import shutil
import zipfile
import locale
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Embedded code.ips data (333 bytes) - Dedicated LovePlus+ Patch
EMBEDDED_CODE_IPS = bytes.fromhex(
    '5041544348'
    '1d315c00080100a0e31eff2fe1'
    '26d0e80038000051e30100a0031eff2f010400a0e30000c1e50100a0e30d00c1e50e00c1e5'
    '0000a0e3100081e50107a0e3140081e50100a0e31eff2fe1'
    '26ed5400140400a0e3700084e53f0000ea00f020e300f020e3'
    '27022c0004df9701ea'
    '2d61b000d470402de930d04de20040a0e10400a0e35000c4e50100a0e35d00c4e55e00c4e5'
    '0000a0e3600084e50107a0e3640084e5785094e50100a0e300008de50000a0e304008de5'
    '08008de50300a0e30c008de570008fe210008de50900a0e314008de50100a0e318008de5'
    '0000a0e31c008de54c009fe520108de20020a0e30930a0e3938cfbeb000050e30b00001a'
    '20008de224108de20020a0e30030a0e300508de50167a0e304608de59c2afaeb0040a0e1'
    '20009de5230000ef0400a0e130d08de27080bde8c0a746002f6c70702e73617600000000'
    '454f46'
)

TITLE_ID = "0004000000120D00"

I18N = {
    'zh': {
        'app_title': "NEW LovePlus+ 存档引继与转换助手 v1.1",
        'header_title': "NEW LovePlus+ 存档引继助手",
        'header_sub': "专为 NDS《LovePlus+》打造，支持 DraStic (.dsv) 与标准 (.sav) 存档一键引继",
        'lang_label': "🌐 语言 / Language:",
        'step1_title': " 第一步：选择 NDS 存档文件 (.dsv / .sav) ",
        'browse': "浏览文件...",
        'tip_default': "提示：可直接选择 DraStic 导出的 lpp.dsv，程序将自动剔除 122 字节尾部并校准为标准 256KB 存档。",
        'step2_title': " 第二步：选择目标部署环境 ",
        'mode_emu': "本机 3DS 模拟器 (自动探测与注入)",
        'mode_sd': "真实 3DS 主机 SD 卡 (自动创建 Luma 补丁目录与 sdmc 存档)",
        'mode_zip': "导出为独立分享包 (.zip) (方便发送给手机模拟器或其他玩家)",
        'no_emu': "未自动检测到常见模拟器，请选择自定义目录",
        'target_path': "目标路径:",
        'sd_root_label': "3DS SD卡根目录:",
        'zip_path_label': "保存压缩包路径:",
        'btn_deploy': "🚀 一键部署 / 导出",
        'grp_log': " 执行日志与操作指引 ",
        'welcome_1': "欢迎使用《NEW LovePlus+ 存档引继助手》！ (by wh76-tech & Google Antigravity)",
        'welcome_2': "请先选择您的 DraStic (.dsv) 或 NDS (.sav) 存档，然后点击【一键部署】。",
        'footer': "Crafted with ❤️ by wh76-tech & Google Antigravity | MIT License",
        'sel_file_title': "选择 LovePlus+ 存档文件",
        'all_files': "所有文件",
        'dsv_recognized': "识别结果: DraStic DSV 存档 ({sz:,} 字节，含 122 字节尾部，部署时将自动截取前 256KB)",
        'std_recognized': "识别结果: 标准《LovePlus+》存档 (256KB / 0x40000 字节，完美就绪)",
        'other_recognized': "已载入存档: {name} ({sz:,} 字节，部署时将校准为标准 256KB)",
        'parse_err': "无法解析文件: {err}",
        'err_title': "错误",
        'select_save_err': "请先选择有效的存档文件！",
        'select_sd_err': "请选择有效的 3DS SD 卡根目录！",
        'no_emu_err': "未检测到已安装的模拟器，请选择【导出独立免安装分享包】或【真实3DS】。",
        'deploy_start': "\n================ 开始部署 [{mode}] ================",
        'target_emu_log': "[*] 目标模拟器: {name}",
        'dsv_stripped_log': "[*] 检测到 DraStic 尾部标记，已自动剥离末尾 122 字节。",
        'save_256_log': "[*] 截取标准 256KB (0x40000)《LovePlus+》存档数据。",
        'save_pad_log': "[*] 存档不足 256KB，已自动填充至 256KB 标准大小。",
        'save_written_log': "[✓] 存档已写入: {path} ({sz:,} 字节)",
        'ips_written_log': "[✓] IPS 补丁已写入: {path}",
        'bin_written_log': "[✓] 完整 code.bin 补丁已写入: {path}",
        'deploy_success_header': "\n================ 部署成功！ ================",
        'deploy_steps': (
            "【接下来只需 3 步】：\n"
            "1. 打开模拟器，运行《NEWラブプラス＋セーブデータ引継ぎツール》（引继工具）。\n"
            "2. 屏幕将显示：『ラブプラス＋』のDSゲームカードを確認しました。\n"
            "   点击【はい】确认复制数据，等待提示引继成功。\n"
            "3. 打开《NEW LovePlus+》（新爱相随+）本体，在标题菜单点击「继承《爱相随》《爱相随+》的存档」（『ラブプラス』『ラブプラス＋』のデータを引き継ぐ），等待进度条跑完，女友数据即完美继承！"
        ),
        'deploy_msg': "《LovePlus+》存档与补丁已成功注入模拟器！\n\n1. 运行《引继工具》，点击【はい】完成数据复制。\n2. 打开《NEW LovePlus+》本体，在标题菜单点击「继承《爱相随》《爱相随+》的存档」并等待进度条跑完即可！",
        'deploy_msg_title': "部署完成",
        'sd_success_header': "\n================ 实机配置完成！ ================",
        'sd_steps': (
            "【实机操作指引】：\n"
            "1. 将 SD 卡插回 3DS 主机，开机长按 Select 确保 Luma 菜单启用了 'Enable game patching'。\n"
            "2. 运行《NEWラブプラス＋セーブデータ引継ぎツール》，确认复制数据。\n"
            "3. 打开《NEW LovePlus+》本体，在标题菜单点击「继承《爱相随》《爱相随+》的存档」（『ラブプラス』『ラブプラス＋』のデータを引き継ぐ），等待进度条跑完即可！"
        ),
        'sd_msg': "SD 卡补丁与存档已就绪！\n\n插回 3DS 运行引继工具完成复制后，在《NEW LovePlus+》本体标题菜单点击「继承《爱相随》《爱相随+》的存档」并等待进度条跑完即可。",
        'sd_msg_title': "实机配置完成",
        'zip_created_log': "[✓] 独立分享包已生成: {path}",
        'zip_desc_log': "压缩包内已包含纯净 256KB 存档、免卡带补丁及全平台使用教程，可直接分享给好友！",
        'zip_msg': "整合压缩包已生成至:\n{path}\n\n可直接分享给其他玩家！",
        'zip_msg_title': "打包成功",
        'save_zip_title': "选择保存位置",
        'op_err_log': "[!] 发生错误: {err}",
        'op_fail_title': "执行失败",
        'op_fail_msg': "部署过程中发生错误:\n{err}",
    },
    'en': {
        'app_title': "NEW LovePlus+ Save Transfer Tool v1.1",
        'header_title': "NEW LovePlus+ Save Transfer Tool",
        'header_sub': "Dedicated tool for NDS LovePlus+, supporting DraStic (.dsv) & standard (.sav) saves",
        'lang_label': "🌐 Language / 语言:",
        'step1_title': " Step 1: Select NDS Save File (.dsv / .sav) ",
        'browse': "Browse...",
        'tip_default': "Note: You can directly select lpp.dsv from DraStic. The tool automatically removes the 122-byte footer and calibrates to standard 256KB.",
        'step2_title': " Step 2: Select Deployment Target ",
        'mode_emu': "Local 3DS Emulator (Auto-detect & Inject)",
        'mode_sd': "Real 3DS SD Card (Auto-create Luma patch directory & sdmc save)",
        'mode_zip': "Export Standalone Share Pack (.zip) (For mobile Citra or sharing with friends)",
        'no_emu': "No supported emulator detected automatically. Please select a custom path.",
        'target_path': "Target Path:",
        'sd_root_label': "3DS SD Card Root:",
        'zip_path_label': "Save Zip File Path:",
        'btn_deploy': "🚀 Deploy / Export Now",
        'grp_log': " Execution Log & Step-by-Step Guide ",
        'welcome_1': "Welcome to NEW LovePlus+ Save Transfer Tool! (by wh76-tech & Google Antigravity)",
        'welcome_2': "Please select your DraStic (.dsv) or NDS (.sav) save, then click [Deploy / Export Now].",
        'footer': "Crafted with ❤️ by wh76-tech & Google Antigravity | MIT License",
        'sel_file_title': "Select LovePlus+ Save File",
        'all_files': "All Files",
        'dsv_recognized': "Recognized: DraStic DSV Save ({sz:,} bytes, 122-byte DeSmuME footer will be stripped on deploy)",
        'std_recognized': "Recognized: Standard LovePlus+ Save (256KB / 0x40000 bytes, ready to use)",
        'other_recognized': "Loaded Save: {name} ({sz:,} bytes, will be calibrated to 256KB)",
        'parse_err': "Cannot parse file: {err}",
        'err_title': "Error",
        'select_save_err': "Please select a valid save file first!",
        'select_sd_err': "Please select a valid 3DS SD card root directory!",
        'no_emu_err': "No installed emulator detected. Please select [Export Standalone Share Pack] or [Real 3DS SD Card].",
        'deploy_start': "\n================ Starting Deployment [{mode}] ================",
        'target_emu_log': "[*] Target Emulator: {name}",
        'dsv_stripped_log': "[*] DraStic footer detected. Automatically stripped trailing 122 bytes.",
        'save_256_log': "[*] Extracted standard 256KB (0x40000) LovePlus+ save data.",
        'save_pad_log': "[*] Save size is under 256KB. Padded to standard 256KB size.",
        'save_written_log': "[✓] Save written to: {path} ({sz:,} bytes)",
        'ips_written_log': "[✓] IPS patch written to: {path}",
        'bin_written_log': "[✓] Patched code.bin written to: {path}",
        'deploy_success_header': "\n================ Deployment Successful! ================",
        'deploy_steps': (
            "[Follow these 3 easy steps]:\n"
            "1. Launch your emulator and open 'NEW LovePlus+ Save Data Transfer Tool'.\n"
            "2. The screen will display: 『ラブプラス＋』のDSゲームカードを確認しました。\n"
            "   Click [はい] (Yes) to confirm copying data.\n"
            "3. Launch 'NEW LovePlus+' game, select 'Inherit save from LovePlus / LovePlus+' (『ラブプラス』『ラブプラス＋』のデータを引き継ぐ) on the title menu, and wait for the progress bar to finish. Your girlfriend data is now seamlessly carried over!"
        ),
        'deploy_msg': "LovePlus+ save and bypass patch successfully injected into the emulator!\n\n1. Run the Transfer Tool and tap [はい] to copy data.\n2. Open 'NEW LovePlus+', select 'Inherit save from LovePlus / LovePlus+' on the title menu, and wait for the progress bar to finish!",
        'deploy_msg_title': "Deployment Complete",
        'sd_success_header': "\n================ SD Card Setup Complete! ================",
        'sd_steps': (
            "[Real 3DS Console Guide]:\n"
            "1. Insert the SD card back into your 3DS. Hold Select on boot to ensure 'Enable game patching' is checked in Luma3DS.\n"
            "2. Launch 'NEW LovePlus+ Save Data Transfer Tool' on your 3DS and confirm copying data.\n"
            "3. Launch 'NEW LovePlus+' game, select 'Inherit save from LovePlus / LovePlus+' (『ラブプラス』『ラブプラス＋』のデータを引き継ぐ) on the title menu, and wait for the progress bar to finish!"
        ),
        'sd_msg': "SD card patch and save are ready!\n\nInsert back into 3DS, run Transfer Tool to copy, then select 'Inherit save from LovePlus / LovePlus+' on the main game title menu and wait for the progress bar to finish.",
        'sd_msg_title': "Setup Complete",
        'zip_created_log': "[✓] Standalone share pack generated: {path}",
        'zip_desc_log': "Zip archive contains calibrated 256KB save, Slot-1 bypass patch, and multi-platform tutorials!",
        'zip_msg': "All-in-one pack generated at:\n{path}\n\nYou can directly share this with other players!",
        'zip_msg_title': "Export Successful",
        'save_zip_title': "Select Zip Destination",
        'op_err_log': "[!] Error occurred: {err}",
        'op_fail_title': "Execution Failed",
        'op_fail_msg': "An error occurred during deployment:\n{err}",
    }
}

def get_bundle_dir():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

def get_patched_code_bin():
    bundle_dir = get_bundle_dir()
    p1 = os.path.join(bundle_dir, 'code_patched.bin')
    if os.path.exists(p1):
        with open(p1, 'rb') as f:
            return f.read()
    p2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'code_patched.bin')
    if os.path.exists(p2):
        with open(p2, 'rb') as f:
            return f.read()
    return None

def detect_emulators():
    appdata = os.environ.get('APPDATA', '')
    candidates = [
        ("Azahar Emulator", os.path.join(appdata, 'Azahar')),
        ("Citra Emulator", os.path.join(appdata, 'Citra')),
        ("Lime3DS Emulator", os.path.join(appdata, 'Lime3DS')),
        ("Mandarine Emulator", os.path.join(appdata, 'Mandarine')),
    ]
    detected = []
    for name, path in candidates:
        if os.path.exists(path):
            detected.append((name, path))
    return detected

def get_default_lang():
    try:
        loc = locale.getdefaultlocale()[0]
        if loc and loc.lower().startswith('zh'):
            return 'zh'
    except Exception:
        pass
    return 'en'

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.lang = get_default_lang()
        self.title(self.t('app_title'))
        self.geometry("690x630")
        self.minsize(640, 570)

        # Set icon if available
        bundle_dir = get_bundle_dir()
        icon_path = os.path.join(bundle_dir, 'app_icon.ico')
        if not os.path.exists(icon_path):
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app_icon.ico')
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

        self.style = ttk.Style(self)
        try:
            self.style.theme_use('vista')
        except Exception:
            pass

        self.save_file_path = tk.StringVar()
        self.target_mode = tk.StringVar(value="emulator")
        self.custom_path = tk.StringVar()
        self.selected_emu_idx = tk.IntVar(value=0)

        self.detected_emus = detect_emulators()
        self.create_widgets()

    def t(self, key, **kwargs):
        lang_dict = I18N.get(self.lang, I18N['en'])
        text = lang_dict.get(key, I18N['en'].get(key, key))
        if kwargs:
            text = text.format(**kwargs)
        return text

    def create_widgets(self):
        # 1. Header Frame
        header = ttk.Frame(self, padding=(15, 12))
        header.pack(fill='x')

        # Top title & Language selector bar
        top_bar = ttk.Frame(header)
        top_bar.pack(fill='x')

        self.title_lbl = ttk.Label(top_bar, text=self.t('header_title'), font=("Microsoft YaHei UI", 14, "bold"))
        self.title_lbl.pack(side='left', anchor='w')

        # Language dropdown on the right
        lang_box = ttk.Frame(top_bar)
        lang_box.pack(side='right', anchor='e')
        self.lbl_lang = ttk.Label(lang_box, text=self.t('lang_label'), font=("Microsoft YaHei UI", 9))
        self.lbl_lang.pack(side='left', padx=(0, 6))

        self.combo_lang = ttk.Combobox(lang_box, state='readonly', width=10, font=("Microsoft YaHei UI", 9))
        self.combo_lang['values'] = ["简体中文", "English"]
        self.combo_lang.current(0 if self.lang == 'zh' else 1)
        self.combo_lang.bind("<<ComboboxSelected>>", self.on_language_selected)
        self.combo_lang.pack(side='left')

        self.sub_lbl = ttk.Label(header, text=self.t('header_sub'), font=("Microsoft YaHei UI", 9), foreground="#666666")
        self.sub_lbl.pack(anchor='w', pady=(3, 0))

        sep = ttk.Separator(self, orient='horizontal')
        sep.pack(fill='x', padx=10, pady=(0, 10))

        # Main content container
        container = ttk.Frame(self, padding=(15, 0))
        container.pack(fill='both', expand=True)

        # 2. Step 1: Save File Selection
        self.grp_save = ttk.LabelFrame(container, text=self.t('step1_title'), padding=(12, 10))
        self.grp_save.pack(fill='x', pady=(0, 10))

        save_box = ttk.Frame(self.grp_save)
        save_box.pack(fill='x')

        self.txt_save = ttk.Entry(save_box, textvariable=self.save_file_path, font=("Microsoft YaHei UI", 9))
        self.txt_save.pack(side='left', fill='x', expand=True, padx=(0, 8))

        self.btn_browse_save = ttk.Button(save_box, text=self.t('browse'), command=self.browse_save_file)
        self.btn_browse_save.pack(side='right')

        self.lbl_save_info = ttk.Label(self.grp_save, text=self.t('tip_default'), font=("Microsoft YaHei UI", 8), foreground="#555555")
        self.lbl_save_info.pack(anchor='w', pady=(6, 0))

        # 3. Step 2: Target Selection
        self.grp_target = ttk.LabelFrame(container, text=self.t('step2_title'), padding=(12, 10))
        self.grp_target.pack(fill='x', pady=(0, 10))

        # Radio 1: Local Emulator
        self.r1 = ttk.Radiobutton(self.grp_target, text=self.t('mode_emu'), variable=self.target_mode, value="emulator", command=self.on_mode_change)
        self.r1.pack(anchor='w')

        emu_frame = ttk.Frame(self.grp_target, padding=(20, 2))
        emu_frame.pack(fill='x')
        self.emu_combo = ttk.Combobox(emu_frame, state='readonly', font=("Microsoft YaHei UI", 9))
        if self.detected_emus:
            self.emu_combo['values'] = [f"{name} ({path})" for name, path in self.detected_emus]
            self.emu_combo.current(0)
        else:
            self.emu_combo['values'] = [self.t('no_emu')]
            self.emu_combo.current(0)
        self.emu_combo.pack(fill='x')

        # Radio 2: Real 3DS SD Card
        self.r2 = ttk.Radiobutton(self.grp_target, text=self.t('mode_sd'), variable=self.target_mode, value="sdcard", command=self.on_mode_change)
        self.r2.pack(anchor='w', pady=(6, 0))

        # Radio 3: Export Zip / Folder for sharing
        self.r3 = ttk.Radiobutton(self.grp_target, text=self.t('mode_zip'), variable=self.target_mode, value="zip", command=self.on_mode_change)
        self.r3.pack(anchor='w', pady=(6, 0))

        # Custom path entry
        self.custom_frame = ttk.Frame(self.grp_target, padding=(20, 6))
        self.custom_frame.pack(fill='x')
        self.lbl_custom = ttk.Label(self.custom_frame, text=self.t('target_path'), font=("Microsoft YaHei UI", 9))
        self.lbl_custom.pack(side='left', padx=(0, 6))
        self.txt_custom = ttk.Entry(self.custom_frame, textvariable=self.custom_path, font=("Microsoft YaHei UI", 9))
        self.txt_custom.pack(side='left', fill='x', expand=True, padx=(0, 6))
        self.btn_browse_custom = ttk.Button(self.custom_frame, text=self.t('browse'), command=self.browse_custom_path)
        self.btn_browse_custom.pack(side='right')

        self.on_mode_change()

        # 4. Action Button
        btn_frame = ttk.Frame(container, padding=(0, 4))
        btn_frame.pack(fill='x', pady=(0, 8))

        self.btn_run = ttk.Button(btn_frame, text=self.t('btn_deploy'), style='Accent.TButton', command=self.execute_deploy)
        self.btn_run.pack(fill='x', ipady=6)

        # 5. Log & Guidance Console
        self.grp_log = ttk.LabelFrame(container, text=self.t('grp_log'), padding=(10, 8))
        self.grp_log.pack(fill='both', expand=True, pady=(0, 10))

        self.log_txt = tk.Text(self.grp_log, wrap='word', height=8, font=("Consolas", 9), relief='flat', background="#f7f7f7")
        self.log_txt.pack(fill='both', expand=True, side='left')
        scroll = ttk.Scrollbar(self.grp_log, command=self.log_txt.yview)
        scroll.pack(side='right', fill='y')
        self.log_txt.config(yscrollcommand=scroll.set)

        self.log(self.t('welcome_1'))
        self.log(self.t('welcome_2'))
        self.log("------------------------------------------------------------------")

        # Footer / Credits
        self.lbl_footer = ttk.Label(container, text=self.t('footer'), font=("Microsoft YaHei UI", 8), foreground="#888888")
        self.lbl_footer.pack(side='bottom', pady=(0, 4))

        # Auto-detect default save file if present in current dir
        cur_dsv = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lpp.dsv')
        cur_sav = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lpp.sav')
        if os.path.exists(cur_dsv):
            self.set_save_file(cur_dsv)
        elif os.path.exists(cur_sav):
            self.set_save_file(cur_sav)

    def on_language_selected(self, event=None):
        idx = self.combo_lang.current()
        self.lang = 'zh' if idx == 0 else 'en'
        self.update_ui_texts()

    def update_ui_texts(self):
        self.title(self.t('app_title'))
        self.title_lbl.config(text=self.t('header_title'))
        self.sub_lbl.config(text=self.t('header_sub'))
        self.lbl_lang.config(text=self.t('lang_label'))
        self.grp_save.config(text=self.t('step1_title'))
        self.btn_browse_save.config(text=self.t('browse'))
        self.grp_target.config(text=self.t('step2_title'))
        self.r1.config(text=self.t('mode_emu'))
        self.r2.config(text=self.t('mode_sd'))
        self.r3.config(text=self.t('mode_zip'))
        self.btn_browse_custom.config(text=self.t('browse'))
        self.btn_run.config(text=self.t('btn_deploy'))
        self.grp_log.config(text=self.t('grp_log'))
        self.lbl_footer.config(text=self.t('footer'))

        # Update mode label
        self.on_mode_change()

        # Update save info if a file is already loaded
        cur_file = self.save_file_path.get().strip()
        if cur_file and os.path.exists(cur_file):
            self.set_save_file(cur_file)
        else:
            self.lbl_save_info.config(text=self.t('tip_default'), foreground="#555555")

    def log(self, text):
        self.log_txt.insert('end', text + "\n")
        self.log_txt.see('end')

    def on_mode_change(self):
        mode = self.target_mode.get()
        if mode == 'emulator':
            self.emu_combo.config(state='readonly')
            self.custom_frame.pack_forget()
        elif mode == 'sdcard':
            self.emu_combo.config(state='disabled')
            self.lbl_custom.config(text=self.t('sd_root_label'))
            self.custom_frame.pack(fill='x')
        elif mode == 'zip':
            self.emu_combo.config(state='disabled')
            self.lbl_custom.config(text=self.t('zip_path_label'))
            self.custom_frame.pack(fill='x')

    def browse_save_file(self):
        path = filedialog.askopenfilename(
            title=self.t('sel_file_title'),
            filetypes=[("NDS Saves (*.dsv, *.sav)", "*.dsv;*.sav"), (self.t('all_files') + " (*.*)", "*.*")]
        )
        if path:
            self.set_save_file(path)

    def set_save_file(self, path):
        self.save_file_path.set(path)
        try:
            sz = os.path.getsize(path)
            with open(path, 'rb') as f:
                raw_bytes = f.read()

            is_dsv = False
            if len(raw_bytes) > 122 and b'|-DESMUME SAVE-|' in raw_bytes[-122:]:
                is_dsv = True

            if is_dsv:
                info = self.t('dsv_recognized', sz=sz)
            elif sz == 262144:
                info = self.t('std_recognized')
            else:
                info = self.t('other_recognized', name=os.path.basename(path), sz=sz)
            self.lbl_save_info.config(text=info, foreground="#007700")
        except Exception as e:
            self.lbl_save_info.config(text=self.t('parse_err', err=e), foreground="#cc0000")

    def browse_custom_path(self):
        mode = self.target_mode.get()
        if mode == 'sdcard':
            d = filedialog.askdirectory(title=self.t('sd_root_label'))
            if d:
                self.custom_path.set(d)
        elif mode == 'zip':
            f = filedialog.asksaveasfilename(
                title=self.t('save_zip_title'),
                defaultextension=".zip",
                filetypes=[("Zip Archive (*.zip)", "*.zip")]
            )
            if f:
                self.custom_path.set(f)

    def process_save_data(self, src_path):
        with open(src_path, 'rb') as f:
            data = f.read()

        # Check for DeSmuME footer
        if len(data) > 122 and b'|-DESMUME SAVE-|' in data[-122:]:
            data = data[:-122]
            self.log(self.t('dsv_stripped_log'))

        # Standard LovePlus+ EEPROM is 256KB (262,144 bytes)
        if len(data) >= 262144:
            clean_data = data[:262144]
            self.log(self.t('save_256_log'))
        else:
            clean_data = data.ljust(262144, b'\xff')
            self.log(self.t('save_pad_log'))
        return clean_data

    def execute_deploy(self):
        src = self.save_file_path.get().strip()
        if not src or not os.path.exists(src):
            messagebox.showerror(self.t('err_title'), self.t('select_save_err'))
            return

        mode = self.target_mode.get()
        self.log(self.t('deploy_start', mode=mode))

        try:
            save_bytes = self.process_save_data(src)
            patched_code_bin = get_patched_code_bin()

            if mode == 'emulator':
                if not self.detected_emus:
                    messagebox.showerror(self.t('err_title'), self.t('no_emu_err'))
                    return
                idx = self.emu_combo.current()
                emu_name, emu_dir = self.detected_emus[idx]
                self.log(self.t('target_emu_log', name=emu_name))

                # 1. Write sdmc/lpp.sav
                sdmc_dir = os.path.join(emu_dir, 'sdmc')
                os.makedirs(sdmc_dir, exist_ok=True)
                target_sav = os.path.join(sdmc_dir, 'lpp.sav')
                with open(target_sav, 'wb') as f:
                    f.write(save_bytes)
                self.log(self.t('save_written_log', path=target_sav, sz=len(save_bytes)))

                # 2. Write mods (write to both mod root and exefs subfolder for 100% fail-safe compatibility)
                mod_title_dir = os.path.join(emu_dir, 'load', 'mods', TITLE_ID)
                mod_exefs_dir = os.path.join(mod_title_dir, 'exefs')
                os.makedirs(mod_exefs_dir, exist_ok=True)

                target_ips_root = os.path.join(mod_title_dir, 'code.ips')
                target_ips_exefs = os.path.join(mod_exefs_dir, 'code.ips')
                with open(target_ips_root, 'wb') as f:
                    f.write(EMBEDDED_CODE_IPS)
                with open(target_ips_exefs, 'wb') as f:
                    f.write(EMBEDDED_CODE_IPS)
                self.log(self.t('ips_written_log', path=target_ips_root))

                if patched_code_bin:
                    target_bin_root = os.path.join(mod_title_dir, 'code.bin')
                    target_bin_exefs = os.path.join(mod_exefs_dir, 'code.bin')
                    with open(target_bin_root, 'wb') as f:
                        f.write(patched_code_bin)
                    with open(target_bin_exefs, 'wb') as f:
                        f.write(patched_code_bin)
                    self.log(self.t('bin_written_log', path=target_bin_root))

                self.log(self.t('deploy_success_header'))
                self.log(self.t('deploy_steps'))

                messagebox.showinfo(self.t('deploy_msg_title'), self.t('deploy_msg'))

            elif mode == 'sdcard':
                sd_root = self.custom_path.get().strip()
                if not sd_root or not os.path.exists(sd_root):
                    messagebox.showerror(self.t('err_title'), self.t('select_sd_err'))
                    return

                # Write SD:/lpp.sav
                target_sav = os.path.join(sd_root, 'lpp.sav')
                with open(target_sav, 'wb') as f:
                    f.write(save_bytes)
                self.log(self.t('save_written_log', path=target_sav, sz=len(save_bytes)))

                # Write Luma3DS LayeredFS patch: SD:/luma/titles/0004000000120D00/code.ips
                luma_mod_dir = os.path.join(sd_root, 'luma', 'titles', TITLE_ID)
                os.makedirs(luma_mod_dir, exist_ok=True)
                target_ips = os.path.join(luma_mod_dir, 'code.ips')
                with open(target_ips, 'wb') as f:
                    f.write(EMBEDDED_CODE_IPS)
                self.log(self.t('ips_written_log', path=target_ips))

                self.log(self.t('sd_success_header'))
                self.log(self.t('sd_steps'))

                messagebox.showinfo(self.t('sd_msg_title'), self.t('sd_msg'))

            elif mode == 'zip':
                zip_path = self.custom_path.get().strip()
                if not zip_path:
                    zip_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "NEW_LovePlus+_Transfer_Pack.zip")

                readme_content = (
                    "========================================================================\n"
                    "NEW LovePlus+ Save Transfer Pack (NEWラブプラス＋ 存档引继补丁包)\n"
                    "========================================================================\n\n"
                    "[1. PC Emulators (Azahar / Citra / Lime3DS)]:\n"
                    "1. Copy 'lpp.sav' to your emulator's 'sdmc/' directory (as sdmc/lpp.sav).\n"
                    "2. Copy 'code.ips' to 'load/mods/0004000000120D00/code.ips' (no exefs folder required, exefs/ is also supported).\n"
                    "3. Open the emulator and launch 'NEW LovePlus+ Save Data Transfer Tool'.\n"
                    "4. Tap [はい] (Yes) to confirm transfer.\n"
                    "5. Launch 'NEW LovePlus+' game, select 'Inherit save from LovePlus / LovePlus+' (『ラブプラス』『ラブプラス＋』のデータを引き継ぐ) on the title menu, and wait for the progress bar to finish!\n\n"
                    "[2. Real 3DS (Luma3DS)]:\n"
                    "1. Place 'lpp.sav' at the root of your SD card (SD:/lpp.sav).\n"
                    "2. Place 'code.ips' at 'SD:/luma/titles/0004000000120D00/code.ips'.\n"
                    "3. Launch the Transfer Tool on 3DS to copy data.\n"
                    "4. Launch 'NEW LovePlus+' game, select 'Inherit save from LovePlus / LovePlus+' on the title menu, and wait for the progress bar to finish!\n\n"
                    "[3. Android Mobile Citra / Lime3DS]:\n"
                    "1. Place save at: /citra-emu/sdmc/lpp.sav\n"
                    "2. Place patch at: /citra-emu/load/mods/0004000000120D00/code.ips\n"
                    "3. Run Transfer Tool -> then in 'NEW LovePlus+' select 'Inherit save' on title menu and wait for progress bar.\n"
                )

                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                    zf.writestr('lpp.sav', save_bytes)
                    zf.writestr('code.ips', EMBEDDED_CODE_IPS)
                    if patched_code_bin:
                        zf.writestr('code.bin', patched_code_bin)
                    zf.writestr('README_Instructions.txt', readme_content.encode('utf-8'))

                self.log(self.t('zip_created_log', path=zip_path))
                self.log(self.t('zip_desc_log'))
                messagebox.showinfo(self.t('zip_msg_title'), self.t('zip_msg', path=zip_path))

        except Exception as e:
            self.log(self.t('op_err_log', err=e))
            messagebox.showerror(self.t('op_fail_title'), self.t('op_fail_msg', err=e))

if __name__ == '__main__':
    app = App()
    app.mainloop()
