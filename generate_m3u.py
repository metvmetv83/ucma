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
    Parametre hatalarını önlemek için en temel komut yapısını kullanan fonksiyon.
    """
    id_clean = identifier.strip()
    
    # URL Belirleme
    if id_clean.startswith('UC'):
        target_url = f'https://www.youtube.com/channel/{id_clean}/live'
    else:
        target_url = f'https://www.youtube.com/watch?v={id_clean}'

    # Hata veren --nocheckcertificate gibi opsiyonları kaldırıp en sade haliyle çağırıyoruz
    # Sadece m3u8 linkini çekmeye odaklı minimal parametre seti
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--no-cache-dir",
        "--no-warnings",
        "-f", "best",
        "-g",
        target_url
    ]
    
    try:
        # Popen yerine run kullanarak daha stabil bir süreç yönetimi sağlıyoruz
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=60,
            # Bazı sistemlerde çevre değişkenleri sorun yaratabilir, temizliyoruz
            env={**os.environ, "PYTHONIOENCODING": "utf-8"}
        )
        
        if result.returncode == 0:
            stdout = result.stdout.strip()
            if stdout:
                # Birden fazla link dönerse (audio+video), m3u8 içeren satırı seç
                for line in stdout.split('\n'):
                    if '.m3u8' in line or 'googlevideo.com' in line:
                        return line.strip()
                return stdout.split('\n')[0].strip()
        else:
            # Hata mesajını sadeleştirip göster
            err_msg = result.stderr.split('\n')[0] if result.stderr else "Bilinmeyen Hata"
            print(f"      ⚠️ yt-dlp Hatası: {err_msg[:70]}")
                
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
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except Exception as e:
        print(f"❌ Dosya okuma hatası: {e}")
        return False
    
    if not lines:
        print("⚠️ Liste boş.")
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
            m3u_content.append(f'#EXTINF:-1 group-title="YouTube Canlı",{name}')
            m3u_content.append(hls_url)
            print(f"   ✅ BAŞARILI")
            success_count += 1
        else:
            print(f"   ❌ BAŞARISIZ")
        
        if idx < total:
            # YouTube bot algılamasını geciktirmek için kısa bekleme
            time.sleep(random.randint(4, 7))
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(m3u_content))
    except Exception as e:
        print(f"❌ Yazma hatası: {e}")
        return False
    
    print(f"\n📊 ÖZET: {success_count}/{total} kanal güncellendi.")
    return success_count > 0

if __name__ == '__main__':
    # İşlem sonucu başarılıysa 0 döner (GitHub Actions için)
    sys.exit(0 if generate_m3u() else 1)
