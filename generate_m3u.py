#!/usr/bin/env python3
import subprocess, sys, os, time, random

def get_hls(ident):
    # ID'den URL oluşturma
    url = f"https://www.youtube.com/channel/{ident}/live" if ident.startswith('UC') else f"https://www.youtube.com/watch?v={ident}"
    
    cmd = [sys.executable, "-m", "yt_dlp", "--no-warnings", "-f", "best", "-g"]
    
    # cookies.txt varsa otomatik kullanır
    if os.path.exists("cookies.txt"):
        cmd.extend(["--cookies", "cookies.txt"])
    
    cmd.append(url)
    
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=40)
        if res.returncode == 0:
            output = res.stdout.strip().split('\n')
            return next((line for line in output if '.m3u8' in line or 'googlevideo' in line), output[0])
    except:
        return None
    return None

def run():
    if not os.path.exists("ids.txt"): return
    with open("ids.txt", "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]

    m3u = ["#EXTM3U"]
    for line in lines:
        name, ident = line.split('|')[:2]
        print(f"🔄 {name} aranıyor...")
        link = get_hls(ident)
        if link:
            m3u.append(f'#EXTINF:-1 group-title="YouTube",{name}\n{link}')
            print(f"✅ {name} eklendi.")
        else:
            print(f"❌ {name} başarısız.")
        time.sleep(random.randint(5, 10))

    with open("metube.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(m3u))

if __name__ == "__main__":
    run()
