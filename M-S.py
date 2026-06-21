import sys
import subprocess
import os
import time
import threading
from scapy.all import sniff, Dot11Deauth, Dot11Beacon, Dot11, Dot11Elt, wrpcap
import customtkinter as ctk
import datetime

# ----------------- التثبيت التلقائي الذكي -----------------
def check_and_install_requirements():
    required_packages = {
        'scapy': 'scapy', 
        'customtkinter': 'customtkinter', 
        'arabic_reshaper': 'arabic-reshaper', 
        'bidi': 'python-bidi'
    }
    for module_name, pip_name in required_packages.items():
        try: 
            __import__(module_name)
        except ImportError:
            try: 
                subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name, "--break-system-packages"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception: pass

check_and_install_requirements()

import arabic_reshaper
from bidi.algorithm import get_display

# ----------------- إعدادات الواجهة والمظهر -----------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def ar_fix(text):
    """إصلاح النصوص العربية للواجهة الرسومية فقط"""
    return get_display(arabic_reshaper.reshape(text))

# ----------------- محرك اللغات الشامل -----------------
LANGUAGES = {
    'en': 'English', 'ar': 'العربية', 'fr': 'Français', 'es': 'Español',
    'de': 'Deutsch', 'ru': 'Русский', 'zh': '中文 (Chinese)', 'ja': '日本語 (Japanese)'
}

TRANSLATIONS = {
    'en': {
        'title': 'M-S Wi-Fi Forensics & IDS', 'select_iface': 'Select Interface:',
        'btn_monitor': '1. Enable Monitor Mode', 'btn_scan': '2. Scan Radar', 'btn_protect': '3. Enable Shield',
        'btn_report': 'Security Report & Map', 'btn_pcap': 'Save PCAP',
        'status_wait': 'Status: Waiting for interface...', 'log_ready': 'M-S System loaded successfully.',
        'dropdown_default': 'Detected networks will appear here...',
        'rep_title': 'Security Intelligence Report', 'rep_net': 'Network (SSID)', 'rep_chan': 'Channel',
        'rep_mac': 'BSSID', 'rep_vendor': 'Vendor', 'rep_enc': 'Encryption', 'rep_wps': 'WPS Status',
        'rep_clients': 'Connected Clients Map', 'rep_threats': 'Threat Analysis', 'btn_save_rep': 'Save Report to File',
        'no_clients': 'No connected clients detected yet.', 'safe': 'Network is stable. No active attacks.',
        'wps_danger': 'Enabled (Danger!)', 'wps_safe': 'Disabled (Safe)', 'rep_saved': 'Report saved successfully as'
    },
    'ar': {
        'title': 'نظام M-S للعمليات الأمنية والأدلة الجنائية', 'select_iface': 'اختر الكرت:',
        'btn_monitor': '1. تفعيل وضع المراقبة', 'btn_scan': '2. فحص الرادار', 'btn_protect': '3. تفعيل درع الحماية',
        'btn_report': 'إصدار تقرير الأمان', 'btn_pcap': 'حفظ الأدلة (PCAP)',
        'status_wait': 'الحالة: في انتظار تفعيل الكرت...', 'log_ready': 'تم تحميل نظام M-S والأدلة الجنائية بنجاح.',
        'dropdown_default': 'الشبكات المكتشفة ستظهر هنا...',
        'rep_title': 'تقرير الاستخبارات الأمنية لشبكة', 'rep_net': 'الشبكة المستهدفة', 'rep_chan': 'القناة اللاسلكية',
        'rep_mac': 'عنوان الماك', 'rep_vendor': 'الشركة المصنعة', 'rep_enc': 'نوع التشفير', 'rep_wps': 'حالة ثغرة WPS',
        'rep_clients': 'خريطة الأجهزة المتصلة (Clients)', 'rep_threats': 'تحليل التهديدات والهجمات', 'btn_save_rep': 'حفظ التقرير في ملف نصي',
        'no_clients': 'لم يتم رصد أجهزة متصلة بعد (استمر في المراقبة).', 'safe': 'الشبكة مستقرة ولا توجد هجمات نشطة حالياً.',
        'wps_danger': 'مفعل (خطر أمني!)', 'wps_safe': 'معطل (آمن)', 'rep_saved': 'تم حفظ التقرير بنجاح باسم'
    },
    'fr': {
        'title': 'M-S - Forensique Wi-Fi et IDS', 'select_iface': 'Sélectionner l\'interface:',
        'btn_monitor': '1. Activer le mode moniteur', 'btn_scan': '2. Scanner le radar', 'btn_protect': '3. Activer le bouclier',
        'btn_report': 'Rapport de sécurité', 'btn_pcap': 'Sauvegarder PCAP',
        'status_wait': 'Statut: En attente d\'interface...', 'log_ready': 'Système M-S chargé avec succès.',
        'dropdown_default': 'Les réseaux détectés apparaîtront ici...',
        'rep_title': 'Rapport d\'Intelligence de Sécurité', 'rep_net': 'Réseau (SSID)', 'rep_chan': 'Canal',
        'rep_mac': 'BSSID', 'rep_vendor': 'Fournisseur', 'rep_enc': 'Chiffrement', 'rep_wps': 'Statut WPS',
        'rep_clients': 'Carte des clients connectés', 'rep_threats': 'Analyse des menaces', 'btn_save_rep': 'Enregistrer le rapport',
        'no_clients': 'Aucun client connecté détecté.', 'safe': 'Le réseau est stable. Aucune attaque.',
        'wps_danger': 'Activé (Danger!)', 'wps_safe': 'Désactivé (Sûr)', 'rep_saved': 'Rapport enregistré sous'
    },
    # (تم اختصار اللغات الأخرى هنا في القاموس للحفاظ على الأداء، وسيتم تطبيق الإنجليزية كبديل آلي لأي لغة لم تُكتب بالكامل)
}

# تعبئة باقي اللغات تلقائياً بالإنجليزية لتجنب الأخطاء
for lang in LANGUAGES:
    if lang not in TRANSLATIONS:
        TRANSLATIONS[lang] = TRANSLATIONS['en']

# ----------------- استخبارات الماك -----------------
MAC_VENDORS = {
    "00:C0:CA": "Alfa Network", "C8:3A:35": "Tenda", "CC:50:E3": "Espressif (Deauther)",
    "18:FE:34": "Espressif (Deauther)", "00:25:9C": "Cisco", "F4:F5:E8": "Apple",
    "00:14:22": "Dell", "B4:B6:76": "Intel", "FC:18:3C": "Samsung"
}

def get_vendor(mac):
    if not mac: return "Unknown"
    return MAC_VENDORS.get(mac[:8].upper(), "Unknown Device")

# ----------------- النافذة الرئيسية -----------------
class MSWiFiIDS(ctk.CTk):
    def __init__(self, lang_code):
        super().__init__()
        self.lang = lang_code
        self.t = TRANSLATIONS.get(self.lang, TRANSLATIONS['en'])
        
        self.title(self.tr('title'))
        self.geometry("1000x850")
        
        self.scanned_networks = {} 
        self.networks_history = {} 
        self.deauth_logs = []
        self.forensic_pcap = [] 
        self.connected_clients = set() 
        
        self.karma_tracker = {}
        self.beacon_count = 0
        self.last_flood_check = time.time()
        
        self.current_iface = ""
        self.is_scanning = False
        self.is_protecting = False
        
        self.setup_ui()

    def tr(self, key):
        text = self.t.get(key, key)
        return ar_fix(text) if self.lang == 'ar' else text

    def raw_tr(self, key):
        """إرجاع النص الأصلي بدون معالجة لحفظه في الملفات النصية"""
        return self.t.get(key, key)

    def get_interfaces(self):
        try: return [iface for iface in os.listdir('/sys/class/net/') if iface != 'lo']
        except Exception: return ["wlan0"]

    def setup_ui(self):
        self.title_label = ctk.CTkLabel(self, text=self.tr('title'), font=("Arial", 24, "bold"), text_color="#FF8C00")
        self.title_label.pack(pady=15)

        self.frame_top = ctk.CTkFrame(self)
        self.frame_top.pack(pady=5, padx=20, fill="x")
        
        available_ifaces = self.get_interfaces()
        self.iface_menu = ctk.CTkOptionMenu(self.frame_top, values=available_ifaces, width=150, fg_color="#333333", button_color="#FF8C00")
        if available_ifaces: self.iface_menu.set(available_ifaces[0])
        self.iface_menu.pack(side="right", padx=10, pady=10)
        
        self.iface_label = ctk.CTkLabel(self.frame_top, text=self.tr('select_iface'), font=("Arial", 14)).pack(side="right")
        self.btn_monitor = ctk.CTkButton(self.frame_top, text=self.tr('btn_monitor'), fg_color="#0055ff", command=self.enable_monitor_mode)
        self.btn_monitor.pack(side="left", padx=10)

        self.frame_mid = ctk.CTkFrame(self)
        self.frame_mid.pack(pady=5, padx=20, fill="x")

        self.network_menu = ctk.CTkOptionMenu(self.frame_mid, values=[self.tr('dropdown_default')], width=250, fg_color="#333333", button_color="#0055ff")
        self.network_menu.pack(side="right", padx=10, pady=10)
        self.btn_scan = ctk.CTkButton(self.frame_mid, text=self.tr('btn_scan'), fg_color="#8B008B", hover_color="#4B0082", command=self.toggle_scan, state="disabled")
        self.btn_scan.pack(side="right", padx=10)
        self.btn_protect = ctk.CTkButton(self.frame_mid, text=self.tr('btn_protect'), fg_color="#FF8C00", hover_color="#CC7000", text_color="black", font=("Arial", 14, "bold"), command=self.toggle_protection, state="disabled")
        self.btn_protect.pack(side="left", padx=10)
        
        self.frame_tools = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_tools.pack(pady=5, padx=20, fill="x")
        self.btn_report = ctk.CTkButton(self.frame_tools, text=self.tr('btn_report'), fg_color="#228B22", hover_color="#006400", command=self.generate_security_report, state="disabled")
        self.btn_report.pack(side="right", padx=10)
        self.btn_pcap = ctk.CTkButton(self.frame_tools, text=self.tr('btn_pcap'), fg_color="#8B0000", hover_color="#660000", text_color="white", command=self.export_pcap, state="disabled")
        self.btn_pcap.pack(side="left", padx=10)

        self.status_label = ctk.CTkLabel(self, text=self.tr('status_wait'), font=("Arial", 16, "bold"), text_color="yellow")
        self.status_label.pack(pady=5)

        self.log_box = ctk.CTkTextbox(self, width=950, height=400, font=("Consolas", 14), text_color="#00FF00", fg_color="#1a1a1a")
        self.log_box.pack(pady=10)
        self.log_message(self.tr('log_ready'))

    def log_message(self, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_box.insert("end", f"[{timestamp}] {message}\n")
        self.log_box.see("end")

    def enable_monitor_mode(self):
        iface = self.iface_menu.get()
        try:
            subprocess.run(["airmon-ng", "check", "kill"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["airmon-ng", "start", iface], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            new_interfaces = self.get_interfaces()
            self.iface_menu.configure(values=new_interfaces)
            self.current_iface = f"{iface}mon" if f"{iface}mon" in new_interfaces else iface
            self.btn_scan.configure(state="normal")
            self.btn_monitor.configure(state="disabled")
            self.log_message("[+] Monitor Mode Enabled.")
        except Exception:
            self.log_message("[-] Error! Run as root (sudo).")

    def update_network_list(self):
        networks = list(self.scanned_networks.keys())
        if networks:
            self.network_menu.configure(values=networks)
            if self.network_menu.get() == self.tr('dropdown_default'):
                self.network_menu.set(networks[-1])
            self.btn_protect.configure(state="normal")
            self.btn_report.configure(state="normal")

    def channel_hopper(self):
        channel = 1
        while self.is_scanning:
            try:
                os.system(f"iwconfig {self.current_iface} channel {channel}")
                channel = channel + 1 if channel < 13 else 1
                time.sleep(0.3)
            except Exception: pass

    def export_pcap(self):
        if not self.forensic_pcap: return
        filename = f"MS_Forensics_{datetime.datetime.now().strftime('%H%M%S')}.pcap"
        wrpcap(filename, self.forensic_pcap)
        self.log_message(f"[+] PCAP Saved: {filename}")

    def process_packet(self, packet):
        if packet.haslayer(Dot11Beacon):
            self.beacon_count += 1
            if time.time() - self.last_flood_check >= 1.0:
                if self.beacon_count > 500: 
                    self.log_message(f"[!!!] Jamming/Flood Detected! Packets: {self.beacon_count}/sec")
                    self.forensic_pcap.append(packet)
                    self.btn_pcap.configure(state="normal")
                self.beacon_count = 0
                self.last_flood_check = time.time()
                
        if self.is_scanning:
            if packet.haslayer(Dot11Beacon):
                try:
                    ssid = packet.info.decode('utf-8', 'ignore')
                    bssid = packet.addr2
                    if ssid and ssid.strip() and "\x00" not in ssid:
                        channel, crypto, wps = 1, "WPA/WPA2", False
                        try:
                            layer = packet.getlayer(Dot11Elt)
                            while layer:
                                if layer.ID == 3: channel = int(layer.info[0])
                                elif layer.ID == 221 and layer.info.startswith(b'\x00P\xf2\x04'): wps = True
                                layer = layer.payload.getlayer(Dot11Elt)
                        except: pass
                        self.scanned_networks[ssid] = {'bssid': bssid, 'channel': channel, 'crypto': crypto, 'wps': wps}
                        self.update_network_list()
                except: pass

        elif self.is_protecting:
            target_ssid = self.network_menu.get()
            target_data = self.scanned_networks.get(target_ssid, {})
            target_bssid = target_data.get('bssid')
            
            if packet.haslayer(Dot11):
                if packet.addr1 == target_bssid and packet.addr2: self.connected_clients.add(packet.addr2)
                elif packet.addr2 == target_bssid and packet.addr1 and packet.addr1 != "ff:ff:ff:ff:ff:ff": self.connected_clients.add(packet.addr1)

            if packet.haslayer(Dot11Beacon):
                try:
                    ssid = packet.info.decode('utf-8', 'ignore')
                    bssid = packet.addr2
                    if ssid == target_ssid and bssid != target_bssid:
                        if f"eviltwin_{bssid}" not in self.deauth_logs:
                            self.deauth_logs.append(f"eviltwin_{bssid}")
                            self.log_message(ar_fix(f"[!!!] Evil Twin Detected! MAC: {bssid} ({get_vendor(bssid)})"))
                            self.forensic_pcap.append(packet)
                            self.btn_pcap.configure(state="normal")
                except: pass

            elif packet.haslayer(Dot11) and packet.type == 0 and packet.subtype in [10, 12]:
                addr1, addr2, addr3 = packet.addr1, packet.addr2, packet.addr3
                if target_bssid in [addr1, addr2, addr3]:
                    if f"{addr2}-{addr1}" not in self.deauth_logs:
                        self.deauth_logs.append(f"{addr2}-{addr1}")
                        attacker = addr2 if addr2 != target_bssid else addr1 
                        self.log_message(ar_fix(f"[!!!] Deauth Attack! {addr2} ({get_vendor(attacker)}) -> {addr1}"))
                        self.forensic_pcap.append(packet)
                        self.btn_pcap.configure(state="normal")

    def generate_security_report(self):
        target_ssid = self.network_menu.get()
        if target_ssid not in self.scanned_networks: return
        data = self.scanned_networks[target_ssid]
        
        # تحضير النص الخام للملف (بدون معالجة)
        raw_rep = f"=== {self.raw_tr('rep_title')} : {target_ssid} ===\n\n"
        raw_rep += f"- {self.raw_tr('rep_net')}: {target_ssid}\n"
        raw_rep += f"- {self.raw_tr('rep_mac')}: {data['bssid']}\n"
        raw_rep += f"- {self.raw_tr('rep_vendor')}: {get_vendor(data['bssid'])}\n"
        raw_rep += f"- {self.raw_tr('rep_chan')}: {data['channel']}\n"
        raw_rep += "-"*40 + "\n"
        raw_rep += f"- {self.raw_tr('rep_enc')}: {data['crypto']}\n"
        wps_stat = self.raw_tr('wps_danger') if data['wps'] else self.raw_tr('wps_safe')
        raw_rep += f"- {self.raw_tr('rep_wps')}: {wps_stat}\n\n"
        
        raw_rep += f"=== {self.raw_tr('rep_clients')} ===\n"
        if not self.connected_clients:
            raw_rep += f"{self.raw_tr('no_clients')}\n"
        else:
            for idx, c in enumerate(self.connected_clients, 1): 
                raw_rep += f"{idx}. {c} -> ({get_vendor(c)})\n"
                
        raw_rep += f"\n=== {self.raw_tr('rep_threats')} ===\n"
        if len(self.forensic_pcap) > 0:
            raw_rep += f"[!] Warning: Detected ({len(self.forensic_pcap)}) malicious packets.\n"
        else:
            raw_rep += f"{self.raw_tr('safe')}\n"

        # تحضير النص المعالج للواجهة الرسومية
        ui_rep = ar_fix(raw_rep) if self.lang == 'ar' else raw_rep

        report_win = ctk.CTkToplevel(self)
        report_win.title(f"{self.tr('rep_title')} - {target_ssid}")
        report_win.geometry("650x700")
        
        title_lbl = ctk.CTkLabel(report_win, text=self.tr('rep_title'), font=("Arial", 20, "bold"), text_color="#FF8C00")
        title_lbl.pack(pady=10)
        
        txt = ctk.CTkTextbox(report_win, width=600, height=500, font=("Arial", 14), text_color="white", fg_color="#222222")
        txt.pack(pady=10)
        txt.insert("0.0", ui_rep)
        txt.configure(state="disabled")

        def save_to_file():
            filename = f"MS_Report_{datetime.datetime.now().strftime('%H%M%S')}.txt"
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(raw_rep)
                self.log_message(f"{self.tr('rep_saved')} {filename}")
            except Exception as e:
                self.log_message(f"Error saving report: {e}")

        btn_save = ctk.CTkButton(report_win, text=self.tr('btn_save_rep'), fg_color="#228B22", hover_color="#006400", command=save_to_file)
        btn_save.pack(pady=10)

    def sniff_loop(self):
        sniff(iface=self.current_iface, prn=self.process_packet, store=False, stop_filter=lambda x: not (self.is_scanning or self.is_protecting))

    def toggle_scan(self):
        if not self.is_scanning:
            if self.is_protecting: self.toggle_protection()
            self.is_scanning = True
            self.btn_scan.configure(text=self.tr('btn_scan').replace('2. ', ''), fg_color="red")
            self.hopper_thread = threading.Thread(target=self.channel_hopper, daemon=True)
            self.hopper_thread.start()
            self.main_thread = threading.Thread(target=self.sniff_loop, daemon=True)
            self.main_thread.start()
            self.log_message("[*] Scanning Radar Started...")
        else:
            self.is_scanning = False
            self.btn_scan.configure(text=self.tr('btn_scan'), fg_color="#8B008B")

    def toggle_protection(self):
        target_ssid = self.network_menu.get()
        if target_ssid not in self.scanned_networks: return
        if not self.is_protecting:
            if self.is_scanning: self.toggle_scan()
            target_channel = self.scanned_networks[target_ssid]['channel']
            self.is_protecting = True
            self.btn_protect.configure(text=self.tr('btn_protect').replace('3. ', ''), fg_color="red")
            self.btn_scan.configure(state="disabled")
            os.system(f"iwconfig {self.current_iface} channel {target_channel}")
            self.log_message(f"[*] Shield Activated on: '{target_ssid}' [CH {target_channel}]")
            self.deauth_logs.clear(); self.forensic_pcap.clear(); self.connected_clients.clear() 
            self.main_thread = threading.Thread(target=self.sniff_loop, daemon=True)
            self.main_thread.start()
        else:
            self.is_protecting = False
            self.btn_protect.configure(text=self.tr('btn_protect'), fg_color="#FF8C00")
            self.btn_scan.configure(state="normal")
            self.log_message("[*] Shield Deactivated.")

# ----------------- شاشة اختيار اللغة المصححة -----------------
class LanguageSelector(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("M-S Setup")
        self.geometry("400x300")
        self.eval('tk::PlaceWindow . center')
        
        # تطبيق معالجة اللغة العربية هنا لضمان عدم ظهور حروف متقطعة
        welcome_text = ar_fix("Select Language / اختر اللغة")
        label = ctk.CTkLabel(self, text=welcome_text, font=("Arial", 18, "bold"))
        label.pack(pady=30)
        
        self.lang_var = ctk.StringVar(value="en")
        options = [f"{v} ({k})" for k, v in LANGUAGES.items()]
        
        self.dropdown = ctk.CTkOptionMenu(self, values=options, width=200, fg_color="#333333", button_color="#FF8C00")
        self.dropdown.pack(pady=10)
        
        btn = ctk.CTkButton(self, text="Start M-S System", fg_color="#0055ff", command=self.start_app)
        btn.pack(pady=30)

    def start_app(self):
        selected = self.dropdown.get()
        lang_code = selected.split('(')[-1].strip(')')
        self.destroy() 
        app = MSWiFiIDS(lang_code) 
        app.mainloop()

if __name__ == "__main__":
    setup = LanguageSelector()
    setup.mainloop()
