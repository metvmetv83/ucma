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
    Kanal ID'si üzerinden canlı yayın m3u8 linkini çeker.
    """
    # Kanal canlı yayın URL'si
    target_url = f'https://www.youtube.com/channel/{channel_id.strip()}/live'

    # En sağlam çalıştırma komutu (Python modülü olarak)
    cmd = [
        sys.executable, '-m', 'yt_dlp',
        '--no-warnings',
        '--no-cache-dir',
        '--nocheckcertificate',
        '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        '-g', 
        '-f', 'best',
        target_url
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            output = result.stdout.strip()
            # Satırları kontrol et, m3u8 veya googlevideo içeren ilk linki al
            for line in output.split('\n'):
                line = line.strip()
                if '.m3u8' in line or 'googlevideo.com' in line:
                    return line
            return output.split('\n')[0] if output else None
        else:
            # Hata mesajını temizleyip göster
            err = result.stderr.lower()
            if 'sign in' in err:
                print(f"      ⚠️ Bot Engeli: Oturum hatası (Sign in)")
            elif 'not exist' in err:
                print(f"      ⚠️ Kanal bulunamadı veya ID yanlış")
            else:
                print(f"      ⚠️ Hata: {result.stderr[:50].strip()}...")
                
    except Exception as e:
        print(f"      ⚠️ Sistem Hatası: {str(e)[:50]}")
    
    return None

def generate_m3u():
    print(f"\n🎬 YouTube M3U Güncelleyici - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    input_file = 'ids.txt'
    output_file = 'metube.m3u'
    
    if not os.path.exists(input_file):
        print(f"❌ {input_file} bulunamadı!")
        return False
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    m3u_content = ['#EXTM3U']
    success_count = 0
    total = len(lines)
    
    for idx, line in enumerate(lines, 1):
        if '|' not in line:
            continue
            
        name, channel_id = line.split('|')[:2]
        print(f"📺 [{idx}/{total}] {name.strip()}")
        
        hls_url = get_hls_from_channel(channel_id)
        
        if hls_url:
            m3u_content.append(f'#EXTINF:-1 group-title="YouTube Canlı",{name.strip()}')
            m3u_content.append(hls_url)
            print(f"   ✅ BAŞARILI!")
            success_count += 1
        else:
            print(f"   ❌ BAŞARISIZ")
        
        # IP engeli yememek için her kanaldan sonra kısa bekleme
        if idx < total:
            wait_time = random.randint(5, 10)
            print(f"   ⏳ {wait_time} sn bekleniyor...")
            time.sleep(wait_time)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(m3u_content))
    
    print(f"\n📊 ÖZET: {success_count}/{total} kanal başarıyla eklendi.")
    return success_count > 0

if __name__ == '__main__':
    # GitHub Actions'ın başarılı olup olmadığını anlaması için return code önemli
    success = generate_m3u()
    sys.exit(0 if success else 1)
