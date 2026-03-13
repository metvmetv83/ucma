#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
import json
import os
from datetime import datetime

def generate_m3u():
    print(f"\n🚀 MeTube Full Otomasyon | {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)
    
    api_url = "https://live.weebtv.workers.dev/"
    input_file = 'ids.txt'
    output_file = 'metube.m3u'
    
    try:
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=120) as response:
            api_data = json.loads(response.read().decode())
        
        # API'deki tüm kanalları bir sözlüğe al
        # stream_map[ID] = URL
        stream_map = {item['ChannelID'].strip(): item['StreamURL'] for item in api_data}
        print(f"✅ API'den {len(stream_map)} aktif yayın çekildi.")
        
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")
        return False

    # ids.txt'deki özel isimleri oku
    named_channels = {}
    if os.path.exists(input_file):
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                if '|' in line:
                    name, cid = line.split('|')[:2]
                    # Linkten ID ayıklama
                    cid_clean = cid.strip().split('/')[-1].split('?')[0]
                    named_channels[cid_clean] = name.strip()

    m3u_content = ['#EXTM3U']
    used_ids = set()
    success_count = 0

    # 1. Önce senin istediğin özel isimli kanalları ekle
    print("\n🔗 Tanımlı Kanallar İşleniyor...")
    for cid, name in named_channels.items():
        if cid in stream_map:
            m3u_content.append(f'#EXTINF:-1 group-title="Favoriler",{name}')
            m3u_content.append(stream_map[cid])
            used_ids.add(cid)
            success_count += 1
            print(f"✅ {name}")

    # 2. API'de olup senin listende olmayan diğer her şeyi ekle
    print("\n📦 Diğer Otomatik Kanallar Ekleniyor...")
    for cid, url in stream_map.items():
        if cid not in used_ids:
            m3u_content.append(f'#EXTINF:-1 group-title="Otomatik Tarama",Kanal-{cid[:6]}')
            m3u_content.append(url)
            success_count += 1

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(m3u_content))
    
    print(f"\n📊 Toplam {success_count} kanal ile M3U oluşturuldu.")
    return True

if __name__ == '__main__':
    generate_m3u()
