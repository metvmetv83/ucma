#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
import json
import os
from datetime import datetime

def generate_m3u():
    print(f"\n🚀 MeTube API Jeneratör (Urllib) | {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)
    
    api_url = "https://live.weebtv.workers.dev/"
    input_file = 'ids.txt'
    output_file = 'metube.m3u'
    
    # 1. API'den güncel verileri çek (Standard Library - urllib)
    try:
        print("🌐 API'den güncel linkler alınıyor...")
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as response:
            if response.status != 200:
                print(f"❌ API Hatası: {response.status}")
                return False
            api_data = json.loads(response.read().decode())
        
        stream_map = {item['ChannelID']: item['StreamURL'] for item in api_data}
        print(f"✅ API'den {len(stream_map)} kanal verisi alındı.")
        
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")
        return False

    # 2. ids.txt dosyasını oku ve eşleştir
    if not os.path.exists(input_file):
        print(f"❌ {input_file} bulunamadı!")
        return False
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except Exception as e:
        print(f"❌ Dosya okuma hatası: {e}")
        return False
    
    m3u_content = ['#EXTM3U']
    success_count = 0
    
    print("\n🔗 Eşleştirme başlatılıyor...")
    for line in lines:
        if '|' not in line: continue
        parts = line.split('|')
        name = parts[0].strip()
        channel_id = parts[1].strip()
        
        print(f"📺 {name}", end=" ")
        
        if channel_id in stream_map:
            hls_url = stream_map[channel_id]
            m3u_content.append(f'#EXTINF:-1 group-title="YouTube Canlı",{name}')
            m3u_content.append(hls_url)
            print("-> ✅ OK")
            success_count += 1
        else:
            print("-> ❌ API'DE BULUNAMADI")

    # 3. Dosyayı kaydet
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(m3u_content))
    
    print(f"\n📊 Özet: {success_count}/{len(lines)} kanal güncellendi.")
    return success_count > 0

if __name__ == '__main__':
    import sys
    sys.exit(0 if generate_m3u() else 1)
