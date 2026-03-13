#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
import time
import random
import os
from datetime import datetime

def get_hls_link(identifier):
    id_clean = identifier.strip()
    # URL veya ID ayıklama
    if 'v=' in id_clean:
        id_clean = id_clean.split('v=')[1].split('&')[0]
    elif 'youtu.be/' in id_clean:
        id_clean = id_clean.split('youtu.be/')[1].split('?')[0]
    elif 'channel/' in id_clean:
        id_clean = id_clean.split('channel/')[1].split('/')[0]

    # Hedef URL
    if id_clean.startswith('UC'):
        target_url = f'https://www.youtube.com/channel/{id_clean}/live'
    else:
        target_url = f'https://www.youtube.com/watch?v={id_clean}'

    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--no-cache-dir",
        "--no-warnings",
        "--nocheckcertificate",
        "-f", "best",
        "-g"
    ]

    # Çerez dosyası varsa ekle
    if os.path.exists("cookies.txt"):
        cmd.extend(["--cookies", "cookies.txt"])
    
    cmd.append(target_url)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            stdout = result.stdout.strip().split('\n')
            for line in stdout:
                if '.m3u8' in line or 'googlevideo' in line:
                    return line.strip()
            return stdout[0]
        else:
            err = result.stderr.lower()
            if "sign in" in err: return "BOT_BLOCK"
            return None
    except:
        return None

def generate_m3u():
    print(f"\n🚀 MeTube Jeneratör | {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 50)
    
    if not os.path.exists("cookies.txt"):
        print("❌ KRİTİK HATA: cookies.txt bulunamadı! İşlem büyük ihtimalle başarısız olacak.")

    input_file, output_file = 'ids.txt', 'metube.m3u'
    if not os.path.exists(input_file): return False
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]
    
    m3u = ['#EXTM3U']
    success = 0
    
    for idx, line in enumerate(lines, 1):
        name, ident = line.split('|')[:2]
        print(f"📺 [{idx}/{len(lines)}] {name.strip()}", end=" ", flush=True)
        
        hls = get_hls_link(ident)
        if hls == "BOT_BLOCK":
            print("-> ❌ BOT ENGELİ")
        elif hls:
            m3u.append(f'#EXTINF:-1 group-title="Canlı",{name.strip()}\n{hls}')
            print("-> ✅ OK")
            success += 1
        else:
            print("-> ❌ HATA")
        
        time.sleep(random.randint(5, 8))
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(m3u))
    
    print(f"\n📊 Sonuç: {success}/{len(lines)} kanal güncellendi.")
    return success > 0

if __name__ == '__main__':
    sys.exit(0 if generate_m3u() else 1)
