#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
import time
import random
import os
from datetime import datetime

def get_hls_from_channel(channel_id):
    """
    Kanal ID'si üzerinden canlı yayın linkini çeker.
    PATH sorununu aşmak için 'python -m yt_dlp' yapısını kullanır.
    """
    channel_url = f'https://www.youtube.com/channel/{channel_id}/live'

    # En sağlam çalıştırma yöntemi: Python modülü olarak çağırmak
    cmd = [
        sys.executable, '-m', 'yt_dlp',
        '--no-warnings',
        '--no-cache-dir',
        '-g', 
        '-f', 'best',
        channel_url
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
        if result.returncode == 0:
            output = result.stdout.strip()
            links = output.split('\n')
            for link in links:
                if '.m3u8' in link or 'manifest' in link:
                    return link
            return links[0] if links else None
        else:
            print(f"      ⚠️ Hata Mesajı: {result.stderr[:100].strip()}")
    except Exception as e:
        print(f"      ⚠️ Beklenmedik Hata: {str(e)[:50]}")
    
    return None

def generate_m3u():
    print(f"\n🚀 MeTube Güncelleyici - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    input_file = 'ids.txt'
    output_file = 'metube.m3u'
    
    if not os.path.exists(input_file):
        print(f"❌ {input_file} dosyası bulunamadı!")
        return False
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    if not lines:
        print("⚠️ ids.txt dosyası boş!")
        return False

    m3u_content = ['#EXTM3U']
    success_count = 0
    
    for idx, line in enumerate(lines, 1):
        if '|' not in line: continue
        
        name, channel_id = line.split('|')
        name = name.strip()
        channel_id = channel_id.strip()

        print(f"📺 [{idx}/{len(lines)}] {name} taranıyor...")
        
        hls_url = get_hls_from_channel(channel_id)
        
        if hls_url:
            m3u_content.append(f'#EXTINF:-1 group-title="YouTube Canlı",{name}')
            m3u_content.append(hls_url)
            print(f"   ✅ Link başarılı.")
            success_count += 1
        else:
            print(f"   ❌ Yayın bulunamadı.")
        
        # YouTube IP limitlerine takılmamak için kısa bekleme
        if idx < len(lines):
            time.sleep(random.randint(4, 8))
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(m3u_content))
    
    print(f"\n📊 ÖZET: {success_count}/{len(lines)} kanal başarıyla eklendi.")
    return success_count > 0

if __name__ == '__main__':
    # İşlem başarılıysa 0, başarısızsa 1 koduyla çık (Actions için önemli)
    sys.exit(0 if generate_m3u() else 1)
