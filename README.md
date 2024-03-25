# self-organizing-hop-network 
## Installation and Deployment Guide
### Step 1 - Install package needed and Get appcation code
Install package
* net-tools ifupdown: check network setting and network control
* nginx-light libnginx-mod-rtmp: RTMP server
* hostapd: Access point host
* git: Get appcation code From GitHub
* python3-opencv: Appcation used package
```bash
sudo apt-get update
sudo apt-get install -y net-tools ifupdown
sudo apt-get install -y nginx-light libnginx-mod-rtmp
sudo apt-get install -y hostapd
sudo apt-get install -y git
sudo apt-get install -y python3-opencv ffmpeg
```
Get code from GitHub
```bash
git clone https://github.com/NCU-NCLab/self-organizing-hop-network.git
```

### Step 2 - Setup RTMP
Switch into root shell
```bash
sudo -i
```
Setup RTMP config
Which host on port 1935
```bash
echo "rtmp {
  server {
    listen 1935;
    chunk_size 4096;
    application live {
      live on;
      record off;
    }
  }
}" > /etc/nginx/rtmp.conf
echo "include /etc/nginx/rtmp.conf;" >> /etc/nginx/nginx.conf
```
Restart nginx server
```bash
systemctl restart nginx.service
```
Check RTMP server status
```bash
netstat -an | grep 1935
```
### Step 3 - Setup AP and default network

#### Step 3.1 - Check Dongle
Check the dongle install or not.
```sbash
ifconfig -a
```
If 2 wireless devices shown, you can skip to step 3.2. 
The following is the sample of 2 wireless devices. If not, you need to install the dongle driver.
```bash
wlan0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.x.x  netmask 255.255.255.0  broadcast 192.168.x.255
        inet6 xxx  prefixlen 64  scopeid 0x20<link>
        ether xx:xx:xx:xx:xx:xx  txqueuelen 1000  (Ethernet)
        RX packets 19596  bytes 27653812 (27.6 MB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 6119  bytes 476613 (476.6 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

wlxxxxxxxxxx123: flags=4099<UP,BROADCAST,MULTICAST>  mtu 1500
        ether xx:xx:xx:xx:xx:xx  txqueuelen 1000  (Ethernet)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 0  bytes 0 (0.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```
##### Step 3.1.1 - Install Dongle Driver

#### Step 3.2 - Setup AP
Turn off interface
```bash
ifconfig wlan0 down
```
Set IP address(Gateway IP) for AP
```bash
echo "auto wlan0
iface wlan0 inet static
    address 192.168.151.1
    netmask 255.255.255.0" > /etc/network/interfaces
```
Set AP setting
```bash
echo "ctrl_interface=/var/run/hostapd
ctrl_interface_group=0
interface=wlan0
driver=nl80211
ssid=Hop_01
hw_mode=g
channel=1
macaddr_acl=0
auth_algs=3
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=12345678
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP" > /etc/hostapd/hostapd.conf
echo "DAEMON_CONF=\"/etc/hostapd/hostapd.conf\"" > /etc/default/hostapd
```
Start AP
```bash
ifup wlan0
systemctl unmask hostapd
systemctl enable hostapd
systemctl start hostapd
```
#### 3.3 Setup default network(Not necessarily for 1st device)
For all "wlxxxxxxxxxx123", replace "wlxxxxxxxxxx123" as your second interface id from Step 3.1
Turn off wpa_supplicant service
```bash
systemctl stop wpa_supplicant
systemctl disable wpa_supplicant
```
Turn off interface
```bash
ifconfig wlxxxxxxxxxx123 down
```
Set IP address(Gateway IP) for default network
Replace ip("192.168.xxx.xxx"), gateway ip("192.168.xxx.1"), ssid("xxxHop_02xxx") and password("xxx12345678xxx") to your wifi setting
```bash
echo "
auto wlxxxxxxxxxx123
iface wlxxxxxxxxxx123 inet static
    address 192.168.xxx.xxx
    network 255.255.255.0
    broadcast 192.168.152.255
    gateway 192.168.xxx.1
    dns-nameservers 8.8.8.8 1.1.1.1
    wpa-ssid \"xxxHop_02xxx\"
    wpa-psk \"xxx12345678xxx\"" >> /etc/network/interfaces
```
Turn on the interface
```bash
ifup wlxxxxxxxxxx123 
```
### Step 4 - Run Video Relay
#### Step 4.1 Run code on 1st Device
exit sudo mode and check camera
```bash=
exit
ls /dev/video*
```
Run relay code
```bash=
cd ~/self-organizing-hop-network
python3 video_push.py
```
#### Step 4.2 Run code on other Device
exit sudo mode
```bash=
exit
```
Run relay code and replace <id> as device id(Example: 2) and interface id "wlxxxxxxxxxx123"
```bash=
cd ~/self-organizing-hop-network
sudo python3 video_relay.py <id> wlxxxxxxxxxx123
```
#### Debug
If the following show
```bash
RTNETLINK answers: File exists
Failed to bring up 
```
Fix by this command
```bash
sudo ip addr flush dev <interface_id>
```