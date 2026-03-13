#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
import time
import random
import os
from datetime import datetime

def get_hls_link(identifier):
    # ID içindeki olası tam URL'leri temizle (Sadece ID kısmını al)
    id_clean = identifier.strip()
    if 'v=' in id_clean:
        id_clean = id_clean.split('v=')[1].split('&')[0]
    elif 'youtu.be/' in id_clean:
        id_clean = id_clean.split('youtu.be/')[1].split('?')[0]
    elif 'channel/' in id_clean:
        id_clean = id_clean.split('channel/')[1].split('/')[0]

    # Hedef URL Belirleme
    if id_clean.startswith('UC'):
        target_url = f'https://www.youtube.com/channel/{id_clean}/live'
    else:
        target_url = f'https://www.youtube.com/watch?v={id_clean}'

    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--no-cache-dir",
        "--no-warnings",
        "-f", "best",
        "-g"
    ]

    # GitHub Actions için Cookies kontrolü (KRİTİK)
    if os.path.exists("cookies.txt"):
        cmd.extend(["--cookies", "cookies.txt"])
    
    cmd.append(target_url)
    
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=60,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"}
        )
        
        if result.returncode == 0:
            stdout = result.stdout.strip()
            for line in stdout.split('\n'):
                if '.m3u8' in line or 'googlevideo.com' in line:
                    return line.strip()
            return stdout.split('\n')[0].strip() if stdout else None
        else:
            err = result.stderr.lower()
            if "sign in" in err: return "BOT_BLOCK"
            if "not exist" in err: return "NOT_FOUND"
            return None
                
    except Exception:
        return None

def generate_m3u():
    print(f"\n🎬 MeTube M3U Jeneratör - {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)
    
    if not os.path.exists("cookies.txt"):
        print("❌ HATA: cookies.txt bulunamadı! YouTube erişimi engellenecek.")
        # GitHub Actions'ta cookies yoksa durması için (isteğe bağlı):
        # return False

    input_file = 'ids.txt'
    output_file = 'metube.m3u'
    
    if not os.path.exists(input_file):
        print(f"❌ {input_file} bulunamadı!")
        return False
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    m3u_content = ['#EXTM3U']
    success_count = 0
    
    for idx, line in enumerate(lines, 1):
        if '|' not in line: continue
        name, identifier = line.split('|')[:2]
        
        print(f"📺 [{idx}/{len(lines)}] {name.strip()}", end=" ", flush=True)
        hls_url = get_hls_link(identifier)
        
        if hls_url == "BOT_BLOCK":
            print("-> ❌ BOT ENGELİ (Cookies yenileyin)")
        elif hls_url == "NOT_FOUND":
            print("-> ❌ KANAL/VİDEO BULUNAMADI")
        elif hls_url:
            m3u_content.append(f'#EXTINF:-1 group-title="YouTube Canlı",{name.strip()}')
            m3u_content.append(hls_url)
            print("-> ✅ BAŞARILI")
            success_count += 1
        else:
            print("-> ❌ BAŞARISIZ")
        
        if idx < len(lines):
            time.sleep(random.randint(5, 8))
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(m3u_content))
    
    print(f"\n📊 ÖZET: {success_count}/{len(lines)} kanal güncellendi.")
    return success_count > 0

if __name__ == '__main__':
    sys.exit(0 if generate_m3u() else 1)
