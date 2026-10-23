import os
import sys
import shutil
import zipfile
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
        ("Azahar 模拟器 (推荐)", os.path.join(appdata, 'Azahar')),
        ("Citra 模拟器", os.path.join(appdata, 'Citra')),
        ("Lime3DS 模拟器", os.path.join(appdata, 'Lime3DS')),
        ("Mandarine 模拟器", os.path.join(appdata, 'Mandarine')),
    ]
    detected = []
    for name, path in candidates:
        if os.path.exists(path):
            detected.append((name, path))
    return detected

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NEW LovePlus+ 存档引继与转换助手 v1.0")
        self.geometry("680x620")
        self.minsize(620, 560)

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

    def create_widgets(self):
        # 1. Header Frame
        header = ttk.Frame(self, padding=(15, 12))
        header.pack(fill='x')

        title_lbl = ttk.Label(header, text="NEW LovePlus+ 存档引继助手", font=("Microsoft YaHei UI", 14, "bold"))
        title_lbl.pack(anchor='w')
        sub_lbl = ttk.Label(header, text="专为 NDS《LovePlus+》打造，支持 DraStic (.dsv) 与标准 (.sav) 存档一键引继", font=("Microsoft YaHei UI", 9), foreground="#666666")
        sub_lbl.pack(anchor='w', pady=(2, 0))

        sep = ttk.Separator(self, orient='horizontal')
        sep.pack(fill='x', padx=10, pady=(0, 10))

        # Main content container
        container = ttk.Frame(self, padding=(15, 0))
        container.pack(fill='both', expand=True)

        # 2. Step 1: Save File Selection
        grp_save = ttk.LabelFrame(container, text=" 第一步：选择 NDS 存档文件 (.dsv / .sav) ", padding=(12, 10))
        grp_save.pack(fill='x', pady=(0, 10))

        save_box = ttk.Frame(grp_save)
        save_box.pack(fill='x')

        self.txt_save = ttk.Entry(save_box, textvariable=self.save_file_path, font=("Microsoft YaHei UI", 9))
        self.txt_save.pack(side='left', fill='x', expand=True, padx=(0, 8))

        btn_browse_save = ttk.Button(save_box, text="浏览文件...", command=self.browse_save_file)
        btn_browse_save.pack(side='right')

        self.lbl_save_info = ttk.Label(grp_save, text="提示：可直接选择 DraStic 导出的 lpp.dsv，程序将自动剔除 122 字节尾部并校准为标准 256KB 存档。", font=("Microsoft YaHei UI", 8), foreground="#555555")
        self.lbl_save_info.pack(anchor='w', pady=(6, 0))

        # 3. Step 2: Target Selection
        grp_target = ttk.LabelFrame(container, text=" 第二步：选择目标部署环境 ", padding=(12, 10))
        grp_target.pack(fill='x', pady=(0, 10))

        # Radio 1: Local Emulator
        r1 = ttk.Radiobutton(grp_target, text="本机 3DS 模拟器 (自动探测与注入)", variable=self.target_mode, value="emulator", command=self.on_mode_change)
        r1.pack(anchor='w')

        emu_frame = ttk.Frame(grp_target, padding=(20, 2))
        emu_frame.pack(fill='x')
        self.emu_combo = ttk.Combobox(emu_frame, state='readonly', font=("Microsoft YaHei UI", 9))
        if self.detected_emus:
            self.emu_combo['values'] = [f"{name} ({path})" for name, path in self.detected_emus]
            self.emu_combo.current(0)
        else:
            self.emu_combo['values'] = ["未自动检测到常见模拟器，请选择自定义目录"]
            self.emu_combo.current(0)
        self.emu_combo.pack(fill='x')

        # Radio 2: Real 3DS SD Card
        r2 = ttk.Radiobutton(grp_target, text="真实 3DS 主机 SD 卡 (自动创建 Luma 补丁目录与 sdmc 存档)", variable=self.target_mode, value="sdcard", command=self.on_mode_change)
        r2.pack(anchor='w', pady=(6, 0))

        # Radio 3: Export Zip / Folder for sharing
        r3 = ttk.Radiobutton(grp_target, text="导出为独立分享包 (.zip) (方便发送给手机模拟器或其他玩家)", variable=self.target_mode, value="zip", command=self.on_mode_change)
        r3.pack(anchor='w', pady=(6, 0))

        # Custom path entry
        self.custom_frame = ttk.Frame(grp_target, padding=(20, 6))
        self.custom_frame.pack(fill='x')
        self.lbl_custom = ttk.Label(self.custom_frame, text="目标路径:", font=("Microsoft YaHei UI", 9))
        self.lbl_custom.pack(side='left', padx=(0, 6))
        self.txt_custom = ttk.Entry(self.custom_frame, textvariable=self.custom_path, font=("Microsoft YaHei UI", 9))
        self.txt_custom.pack(side='left', fill='x', expand=True, padx=(0, 6))
        self.btn_browse_custom = ttk.Button(self.custom_frame, text="浏览...", command=self.browse_custom_path)
        self.btn_browse_custom.pack(side='right')

        self.on_mode_change()

        # 4. Action Button
        btn_frame = ttk.Frame(container, padding=(0, 4))
        btn_frame.pack(fill='x', pady=(0, 8))

        self.btn_run = ttk.Button(btn_frame, text="🚀 一键部署 / 导出", style='Accent.TButton', command=self.execute_deploy)
        self.btn_run.pack(fill='x', ipady=6)

        # 5. Log & Guidance Console
        grp_log = ttk.LabelFrame(container, text=" 执行日志与操作指引 ", padding=(10, 8))
        grp_log.pack(fill='both', expand=True, pady=(0, 10))

        self.log_txt = tk.Text(grp_log, wrap='word', height=8, font=("Consolas", 9), relief='flat', background="#f7f7f7")
        self.log_txt.pack(fill='both', expand=True, side='left')
        scroll = ttk.Scrollbar(grp_log, command=self.log_txt.yview)
        scroll.pack(side='right', fill='y')
        self.log_txt.config(yscrollcommand=scroll.set)

        self.log("欢迎使用《NEW LovePlus+ 存档引继助手》！")
        self.log("请先选择您的 DraStic (.dsv) 或 NDS (.sav) 存档，然后点击【一键部署】。")
        self.log("------------------------------------------------------------------")

        # Auto-detect default save file if present in current dir
        cur_dsv = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lpp.dsv')
        cur_sav = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lpp.sav')
        if os.path.exists(cur_dsv):
            self.set_save_file(cur_dsv)
        elif os.path.exists(cur_sav):
            self.set_save_file(cur_sav)

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
            self.lbl_custom.config(text="3DS SD卡根目录:")
            self.custom_frame.pack(fill='x')
        elif mode == 'zip':
            self.emu_combo.config(state='disabled')
            self.lbl_custom.config(text="保存压缩包路径:")
            self.custom_frame.pack(fill='x')

    def browse_save_file(self):
        path = filedialog.askopenfilename(
            title="选择 LovePlus+ 存档文件",
            filetypes=[("NDS 存档 (*.dsv, *.sav)", "*.dsv;*.sav"), ("所有文件 (*.*)", "*.*")]
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
                info = f"识别结果: DraStic DSV 存档 ({sz:,} 字节，含 122 字节尾部，部署时将自动截取前 256KB)"
            elif sz == 262144:
                info = f"识别结果: 标准《LovePlus+》存档 (256KB / 0x40000 字节，完美就绪)"
            else:
                info = f"已载入存档: {os.path.basename(path)} ({sz:,} 字节，部署时将校准为标准 256KB)"
            self.lbl_save_info.config(text=info, foreground="#007700")
        except Exception as e:
            self.lbl_save_info.config(text=f"无法解析文件: {e}", foreground="#cc0000")

    def browse_custom_path(self):
        mode = self.target_mode.get()
        if mode == 'sdcard':
            d = filedialog.askdirectory(title="选择 3DS SD 卡根目录")
            if d:
                self.custom_path.set(d)
        elif mode == 'zip':
            f = filedialog.asksaveasfilename(
                title="选择保存位置",
                defaultextension=".zip",
                filetypes=[("Zip 压缩包 (*.zip)", "*.zip")]
            )
            if f:
                self.custom_path.set(f)

    def process_save_data(self, src_path):
        with open(src_path, 'rb') as f:
            data = f.read()

        # Check for DeSmuME footer
        if len(data) > 122 and b'|-DESMUME SAVE-|' in data[-122:]:
            data = data[:-122]
            self.log(f"[*] 检测到 DraStic 尾部标记，已自动剥离末尾 122 字节。")

        # Standard LovePlus+ EEPROM is 256KB (262,144 bytes)
        if len(data) >= 262144:
            clean_data = data[:262144]
            self.log(f"[*] 截取标准 256KB (0x40000)《LovePlus+》存档数据。")
        else:
            clean_data = data.ljust(262144, b'\xff')
            self.log(f"[*] 存档不足 256KB，已自动填充至 256KB 标准大小。")
        return clean_data

    def execute_deploy(self):
        src = self.save_file_path.get().strip()
        if not src or not os.path.exists(src):
            messagebox.showerror("错误", "请先选择有效的存档文件！")
            return

        mode = self.target_mode.get()
        self.log(f"\n================ 开始部署 [{mode}] ================")

        try:
            save_bytes = self.process_save_data(src)
            patched_code_bin = get_patched_code_bin()

            if mode == 'emulator':
                if not self.detected_emus:
                    messagebox.showerror("错误", "未检测到已安装的模拟器，请选择【导出独立免安装分享包】或【真实3DS】。")
                    return
                idx = self.emu_combo.current()
                emu_name, emu_dir = self.detected_emus[idx]
                self.log(f"[*] 目标模拟器: {emu_name}")

                # 1. Write sdmc/lpp.sav
                sdmc_dir = os.path.join(emu_dir, 'sdmc')
                os.makedirs(sdmc_dir, exist_ok=True)
                target_sav = os.path.join(sdmc_dir, 'lpp.sav')
                with open(target_sav, 'wb') as f:
                    f.write(save_bytes)
                self.log(f"[✓] 存档已写入: {target_sav} ({len(save_bytes):,} 字节)")

                # 2. Write mods
                mod_dir = os.path.join(emu_dir, 'load', 'mods', TITLE_ID, 'exefs')
                os.makedirs(mod_dir, exist_ok=True)

                target_ips = os.path.join(mod_dir, 'code.ips')
                with open(target_ips, 'wb') as f:
                    f.write(EMBEDDED_CODE_IPS)
                self.log(f"[✓] IPS 补丁已写入: {target_ips}")

                if patched_code_bin:
                    target_bin = os.path.join(mod_dir, 'code.bin')
                    with open(target_bin, 'wb') as f:
                        f.write(patched_code_bin)
                    self.log(f"[✓] 完整 code.bin 补丁已写入: {target_bin}")

                self.log("\n================ 部署成功！ ================")
                self.log("【接下来只需 3 步】：")
                self.log("1. 打开模拟器，运行《NEWラブプラス＋セーブデータ引継ぎツール》（引继工具）。")
                self.log("2. 屏幕将显示：『ラブプラス＋』のDSゲームカードを確認しました。")
                self.log("   点击【はい】确认复制数据。")
                self.log("3. 提示引继完成后，打开《NEW LovePlus+》本体，女友数据已完美继承！")

                messagebox.showinfo("部署完成", "《LovePlus+》存档与补丁已成功注入模拟器！\n\n现在请打开模拟器运行《引继工具》，点击【はい】即可完成继承！")

            elif mode == 'sdcard':
                sd_root = self.custom_path.get().strip()
                if not sd_root or not os.path.exists(sd_root):
                    messagebox.showerror("错误", "请选择有效的 3DS SD 卡根目录！")
                    return

                # Write SD:/lpp.sav
                target_sav = os.path.join(sd_root, 'lpp.sav')
                with open(target_sav, 'wb') as f:
                    f.write(save_bytes)
                self.log(f"[✓] 存档已写入 SD 卡根目录: {target_sav}")

                # Write Luma3DS LayeredFS patch: SD:/luma/titles/0004000000120D00/code.ips
                luma_mod_dir = os.path.join(sd_root, 'luma', 'titles', TITLE_ID)
                os.makedirs(luma_mod_dir, exist_ok=True)
                target_ips = os.path.join(luma_mod_dir, 'code.ips')
                with open(target_ips, 'wb') as f:
                    f.write(EMBEDDED_CODE_IPS)
                self.log(f"[✓] Luma3DS 补丁已写入: {target_ips}")

                self.log("\n================ 实机配置完成！ ================")
                self.log("【实机操作指引】：")
                self.log("1. 将 SD 卡插回 3DS 主机，开机确保 Luma 菜单启用了 'Enable game patching'。")
                self.log("2. 运行《NEWラブプラス＋セーブデータ引継ぎツール》。")
                self.log("3. 确认复制数据，引继完成后打开《NEW LovePlus+》即可！")

                messagebox.showinfo("实机配置完成", "SD 卡补丁与存档已就绪！\n\n插回 3DS 运行引继工具即可完成转换。")

            elif mode == 'zip':
                zip_path = self.custom_path.get().strip()
                if not zip_path:
                    zip_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "NEW_LovePlus+_引继补丁包.zip")

                readme_content = (
                    "【NEW LovePlus+ 存档引继补丁包使用说明】\n\n"
                    "一、电脑模拟器（Azahar / Citra / Lime3DS）用户：\n"
                    "1. 将 lpp.sav 复制到模拟器数据目录下的 sdmc/ 文件夹内（即 sdmc/lpp.sav）。\n"
                    "2. 将 code.ips 和 code.bin 复制到 load/mods/0004000000120D00/exefs/ 文件夹下。\n"
                    "3. 运行《NEWラブプラス＋セーブデータ引継ぎツール》，提示识别到卡带后点击【はい】。\n"
                    "4. 打开《NEW LovePlus+》游戏本体即可继承！\n\n"
                    "二、真实 3DS（Luma3DS）实机用户：\n"
                    "1. 将 lpp.sav 放到 SD 卡根目录下。\n"
                    "2. 将 code.ips 放到 SD:/luma/titles/0004000000120D00/ 目录下。\n"
                    "3. 主机运行引继工具完成复制。\n\n"
                    "三、手机 Citra / Lime3DS 用户：\n"
                    "1. 存档放置在：/citra-emu/sdmc/lpp.sav\n"
                    "2. 补丁放置在：/citra-emu/load/mods/0004000000120D00/exefs/code.ips\n"
                )

                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                    zf.writestr('lpp.sav', save_bytes)
                    zf.writestr('code.ips', EMBEDDED_CODE_IPS)
                    if patched_code_bin:
                        zf.writestr('code.bin', patched_code_bin)
                    zf.writestr('使用说明.txt', readme_content.encode('utf-8'))

                self.log(f"[✓] 独立分享包已生成: {zip_path}")
                self.log("压缩包内已包含纯净 256KB 存档、免卡带补丁及全平台使用教程，可直接分享给好友！")
                messagebox.showinfo("打包成功", f"整合压缩包已生成至:\n{zip_path}\n\n可直接分享给其他玩家！")

        except Exception as e:
            self.log(f"[!] 发生错误: {e}")
            messagebox.showerror("执行失败", f"部署过程中发生错误:\n{e}")

if __name__ == '__main__':
    app = App()
    app.mainloop()
