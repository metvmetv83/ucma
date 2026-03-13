#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
import time
import random
import os
from datetime import datetime

def get_hls_link(identifier):
    """
    Hem Kanal ID hem de Video ID destekleyen, 
    komut dizimi hatasını önleyen geliştirilmiş fonksiyon.
    """
    id_clean = identifier.strip()
    
    # Eğer identifier bir kanal ID'si ise (UC ile başlıyorsa)
    if id_clean.startswith('UC'):
        target_url = f'https://www.youtube.com/channel/{id_clean}/live'
    # Eğer doğrudan bir video ID'si ise
    else:
        target_url = f'https://www.youtube.com/watch?v={id_clean}'

    # Parametre sıralaması 'Usage' hatasını önlemek için optimize edildi
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--no-warnings",
        "--no-cache-dir",
        "--nocheckcertificate",
        "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "-f", "best",
        "-g",
        target_url
    ]
    
    try:
        # stdout ve stderr'i ayırarak daha iyi hata takibi yapıyoruz
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate(timeout=60)
        
        if process.returncode == 0:
            links = stdout.strip().split('\n')
            for link in links:
                if '.m3u8' in link or 'googlevideo.com' in link:
                    return link.strip()
            return links[0].strip() if links else None
        else:
            print(f"      ⚠️ Detaylı Hata: {stderr[:100].strip()}")
                
    except Exception as e:
        print(f"      ⚠️ Sistem Hatası: {str(e)[:50]}")
    
    return None

def generate_m3u():
    print(f"\n🎬 MeTube M3U Jeneratör - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    input_file = 'ids.txt'
    output_file = 'metube.m3u'
    
    if not os.path.exists(input_file):
        print(f"❌ {input_file} bulunamadı!")
        return False
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    if not lines:
        print("⚠️ Liste boş, işlem yapılmadı.")
        return False

    m3u_content = ['#EXTM3U']
    success_count = 0
    total = len(lines)
    
    for idx, line in enumerate(lines, 1):
        if '|' not in line:
            continue
            
        parts = line.split('|')
        name = parts[0].strip()
        identifier = parts[1].strip()
        
        print(f"📺 [{idx}/{total}] {name}")
        
        hls_url = get_hls_link(identifier)
        
        if hls_url:
            # Bazı oynatıcılar için linkin sonuna User-Agent eklemek gerekebilir (isteğe bağlı)
            m3u_content.append(f'#EXTINF:-1 group-title="YouTube Canlı",{name}')
            m3u_content.append(hls_url)
            print(f"   ✅ BAŞARILI")
            success_count += 1
        else:
            print(f"   ❌ BAŞARISIZ")
        
        if idx < total:
            wait = random.randint(5, 10)
            time.sleep(wait)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(m3u_content))
    
    print(f"\n📊 ÖZET: {success_count}/{total} kanal başarıyla eklendi.")
    return success_count > 0

if __name__ == '__main__':
    # Kodun sonucuna göre çıkış yap
    sys.exit(0 if generate_m3u() else 1)
