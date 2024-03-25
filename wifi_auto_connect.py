import subprocess, re

def info_process(info_raw):
    info = {}
    for i in info_raw:
        if "SSID" in i:
            info["SSID"] = i.split('"')[1]
        if "Quality" in i:
            info["quality"] = re.split(r'[=/\s]', i)[1]
            info["signal_level"] = re.split(r'[=/\s]', i)[6]
    return info

def edit_network_interface(interface_name, new_config):
    file_path = '/etc/network/interfaces'
    
    # Read the content of the interfaces file
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Find the index range for the specific interface section
    start_index = None
    end_index = None
    for i, line in enumerate(lines):
        if line.strip().startswith(f'auto {interface_name}'):
            start_index = i
        elif start_index is not None and line.strip() == '':
            end_index = i
            break

    if start_index is None or end_index is None:
        print(f"Interface '{interface_name}' not found in '{file_path}'")
        return

    # Modify the specific interface section
    lines[start_index:end_index] = new_config.splitlines(True)

    # Write the modified content back to the interfaces file
    with open(file_path, 'w') as file:
        file.writelines(lines)

class WiFi:
    def __init__(self, SSID, password):
        self.SSID = SSID
        self.pw = password
        self.signal_level = None
        self.quality = None
        
    def set_signal_level(self, signal_level):
        self.signal_level = signal_level
        
    def set_quality(self, quality):
        self.quality = quality
        
    def connect(self, interface, ip_prefix, ip_end=2):
        ip = ip_prefix + "." + str(ip_end)
        output = ""
        subprocess.check_output(['ifdown', interface])
        edit_network_interface(interface, f'''auto {interface}
iface {interface} inet static
    address {ip}
    network 255.255.255.0
    broadcast {ip_prefix}.255
    gateway {ip_prefix}.1
    dns-nameservers 8.8.8.8 1.1.1.1
    wpa-ssid "{self.SSID}"
    wpa-psk "{self.pw}"\n''')
        subprocess.check_output(['ifup', interface])
        print("\033[92mConnected WiFi", self.SSID, "on", interface, "\033[00m")
            
    def __repr__(self):
        return {
            "SSID": self.SSID,
            "Quality": self.quality,
            "signal_level":self.signal_level
        }
    
    def __str__(self):
        return f"SSID: {self.SSID}, Quality: {self.quality}, signal_level: {self.signal_level}"

class WiFi_Scanner:
    def __init__(self, interface="wlan1"):
        self.interface=interface
        self.info = []
        self.last_ssid = ""
        
    def get_wifi_info(self, prefix="NCLAB_HUB"):
        try:
            subprocess.check_output(['ifup', self.interface])
        except:
            pass
        self.info = []
        wifi_list = []
        wifi_list_raw = subprocess.check_output(['iwlist', self.interface, 'scanning']).decode()
        wifi_list_raw = wifi_list_raw.split("Cell")
        for wifi in wifi_list_raw:
            info_raw = wifi.split("\n")
            info_raw = [i.lstrip() for i in info_raw]
            if len(info_raw) > 4:
                info = info_process(info_raw)
                if prefix in info["SSID"]:
                    self.info.append(WiFi(info["SSID"], "12345678"))
                    self.info[-1].set_signal_level(info["signal_level"])
                    self.info[-1].set_quality(info["quality"])
        return self.info

    def get_best_wifi_info(self, prefix="NCLAB_HUB"):
        self.get_wifi_info(prefix)
        if len(self.info) > 0:
            best_info = self.info[0]
            for wifi in self.info:
                if best_info.signal_level < wifi.signal_level:
                    best_info = wifi
            return best_info
        else:
            return None
        
    def get_best_wifi_info_maxid(self, max_id=2, prefix="NCLAB_HUB"):
        self.get_wifi_info(prefix)
        if len(self.info) > 0:
            best_info = self.info[0]
            for wifi in self.info:
                if int(wifi.SSID[-1])+1 == int(max_id):
                    return wifi
                elif best_info.signal_level < wifi.signal_level and int(wifi.SSID[-1]) < int(max_id):
                    best_info = wifi
            return best_info
        else:
            return None
   
    def connect(self, wifi, ip_end_num):
        if self.last_ssid == wifi.SSID:
            print("\033[92mWiFi already Connected", wifi.SSID, "on", self.interface, "\033[00m")
            pass
        else:
            wifi.connect(self.interface, "192.168.10"+wifi.SSID[-1], ip_end_num)
            self.last_ssid = wifi.SSID
