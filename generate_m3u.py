#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
import time
import random
import shutil
import os
from datetime import datetime

def get_hls_from_channel(channel_id):
    """
    Kanal ID'si üzerinden canlı yayın linkini çeker.
    """
    yt_dlp_cmd = 'yt-dlp'
    if not shutil.which(yt_dlp_cmd):
        yt_dlp_cmd = sys.executable + " -m yt_dlp"

    # YouTube kanalının canlı yayın URL'si
    channel_url = f'https://www.youtube.com/channel/{channel_id}/live'

    cmd = [
        yt_dlp_cmd,
        '--no-warnings',
        '--no-cache-dir',
        '-g', 
        '-f', 'best',
        channel_url
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=40)
        if result.returncode == 0:
            output = result.stdout.strip()
            links = output.split('\n')
            for link in links:
                if '.m3u8' in link or 'manifest' in link:
                    return link
            return links[0] if links else None
    except Exception as e:
        print(f"      ⚠️ Hata: {str(e)[:50]}")
    
    return None

def generate_m3u():
    print(f"\n🚀 MeTube Güncelleyici - {datetime.now().strftime('%H:%M:%S')}")
    print("-" * 50)
    
    input_file = 'ids.txt'
    output_file = 'metube.m3u'
    
    if not os.path.exists(input_file):
        print(f"❌ {input_file} bulunamadı!")
        return False
    
    with open(input_file, 'r', encoding='utf-8') as f:
        # Boş satırları ve # ile başlayan yorumları atla
        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    m3u_content = ['#EXTM3U']
    success_count = 0
    
    for idx, line in enumerate(lines, 1):
        if '|' not in line: continue
        
        name, channel_id = line.split('|')
        name = name.strip()
        channel_id = channel_id.strip()

        print(f"📺 [{idx}/{len(lines)}] {name}")
        
        hls_url = get_hls_from_channel(channel_id)
        
        if hls_url:
            # Logo ve tvg-id kısımlarını attık, sadece temel bilgiler
            m3u_content.append(f'#EXTINF:-1 group-title="YouTube Canlı",{name}')
            m3u_content.append(hls_url)
            print(f"   ✅ Link Alındı")
            success_count += 1
        else:
            print(f"   ❌ Yayın Bulunamadı")
        
        # IP ban yememek için kısa beklemeler
        if idx < len(lines):
            time.sleep(random.randint(3, 6))
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(m3u_content))
    
    print(f"\n📊 Bitti: {success_count}/{len(lines)} kanal güncellendi.")
    return success_count > 0

if __name__ == '__main__':
    generate_m3u()
