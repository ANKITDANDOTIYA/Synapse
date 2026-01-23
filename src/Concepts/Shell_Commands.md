# ??? Raspberry Pi Initial Setup Commands

Ye guide **Project Synapse** ke initial system configuration ke liye hai. In commands ko terminal (SSH) ke through run karna hai.

---

## 1. System Refresh & Update

### `sudo apt update`
- **Function:** Ye command Raspberry Pi ke software repositories (online servers) se latest package lists download karta hai.
- **Why:** Isse system ko pata chalta hai ki kaunse softwares ke naye versions available hain. Ye install nahi karta, sirf "check" karta hai.

### `sudo apt upgrade -y`
- **Function:** Ye asliyat mein purane softwares ko download karke naye version se replace (upgrade) karta hai.
- **Flag `-y`:** Iska matlab hai "Auto-Yes". Ye install karte waqt aapse baar-baar permission nahi maangega.

---

## 2. Power & Identification

### `sudo reboot`
- **Function:** System ko restart karta hai. 
- **Note:** SSH connection cut jayega. 1-2 minute baad wapas login karna hoga.

### `sudo shutdown -h now`
- **Function:** Raspberry Pi ko turant surakshit tarike se band karta hai. 
- **Importance:** Bina shutdown kiye power cable nikalne se SD Card corrupt ho sakta hai.

### `hostname -I`
- **Function:** Raspberry Pi ka current Local IP Address dikhata hai.

---

## 3. Hardware Monitoring

### `vcgencmd measure_temp`
- **Function:** Raspberry Pi ke processor (CPU) ka temperature dikhata hai. 
- **Why:** Project Synapse mein jab AI model chalega, toh humein check karna hoga ki Pi overheat toh nahi ho raha.

### `df -h`
- **Function:** Disk usage check karta hai. 
- **Note:** Isse aap dekh sakte hain ki 128GB card mein se kitni space bachi hai.

---

## 4. SSH & Networking

### `ping raspberrypi.local`
- **Function:** Laptop se check karta hai ki Pi network par accessible hai ya nahi.

### `ssh [username]@[hostname].local`
- **Function:** Secure Shell tunnel banata hai taaki laptop se Pi ka terminal control kiya ja sake.