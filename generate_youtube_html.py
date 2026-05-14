import json
import os
import time
import urllib.parse
import html

repo = os.environ.get('REPO', '')
download_owner = 'Amin5v5'
download_repo = 'download'
download_workflow = 'youtube-download.yml'

default_format = 'mp4 (video)'
default_quality = '720p'
default_max_part = '90'
default_upload = 'repository (push to repo)'

output_dir = 'search_results/youtube'
output_file = os.path.join(output_dir, 'index.html')

def make_download_url(video_url):
    base = f"https://github.com/{download_owner}/{download_repo}/actions/workflows/{download_workflow}"
    params = {
        'video_url': video_url,
        'output_format': default_format,
        'desired_quality': default_quality,
        'max_part_mb': default_max_part,
        'upload_method': default_upload
    }
    return base + '?' + urllib.parse.urlencode(params, safe='')

videos = []
# اولویت با data_youtube.json، سپس data.json (خروجی workflow فعلی)
for fname in ('data_youtube.json', 'data.json'):
    if os.path.exists(fname) and os.path.getsize(fname) > 0:
        try:
            with open(fname, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content.startswith('['):
                    videos = json.loads(content)
                else:
                    videos = [json.loads(line) for line in content.splitlines() if line.strip()]
            print(f"خواندن {len(videos)} ویدئو از {fname}")
            break
        except Exception as e:
            print(f"خطا در خواندن {fname}: {e}")
            videos = []

if not videos:
    print("⚠️ هیچ داده‌ای برای ساخت صفحه وجود ندارد.")

def generate_html():
    html_header = f'''<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>نتایج جستجوی یوتیوب</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Tahoma, sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        h1 {{ text-align: center; color: #ff0000; margin-bottom: 20px; }}
        .search-btn {{ text-align: center; margin-bottom: 30px; }}
        .search-btn a {{ background: #ff0000; color: white; padding: 10px 20px; text-decoration: none; border-radius: 8px; font-weight: bold; }}
        .results {{ display: flex; flex-direction: column; gap: 20px; }}
        .video-card {{ background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); display: flex; }}
        .thumbnail {{ width: 240px; height: 135px; object-fit: cover; }}
        .info {{ padding: 15px; flex: 1; }}
        .title {{ font-size: 1.1rem; font-weight: bold; margin-bottom: 8px; display: flex; align-items: center; gap: 8px; }}
        .title a {{ color: #0f0f0f; text-decoration: none; }}
        .title a:hover {{ color: #ff0000; }}
        .copy-btn {{ background: none; border: none; cursor: pointer; font-size: 1rem; color: #606060; }}
        .copy-btn:hover {{ color: #34a853; }}
        .channel {{ color: #606060; font-size: 0.9rem; margin-bottom: 8px; }}
        .meta {{ color: #606060; font-size: 0.8rem; }}
        .download-btn {{ background: #cc0000; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: bold; margin-top: 10px; }}
        .download-btn:hover {{ background: #990000; }}
        .footer {{ text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #888; }}
        @media (max-width: 600px) {{
            .video-card {{ flex-direction: column; }}
            .thumbnail {{ width: 100%; height: auto; }}
        }}
    </style>
    <script>
        function copyLink(url) {{
            navigator.clipboard.writeText(url).then(() => {{
                var toast = document.createElement('div');
                toast.textContent = '✅ لینک کپی شد!';
                toast.style.cssText = 'position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:#333;color:white;padding:10px 20px;border-radius:20px;z-index:9999;opacity:1;transition:opacity 0.5s;';
                document.body.appendChild(toast);
                setTimeout(() => {{ toast.style.opacity = '0'; setTimeout(() => toast.remove(), 500); }}, 1500);
            }}).catch(() => {{
                prompt('لینک را کپی کنید:', url);
            }});
        }}
    </script>
</head>
<body>
<div class="container">
    <h1>🎬 نتایج جستجوی یوتیوب</h1>
    <div class="search-btn">
        <a href="https://github.com/{repo}/actions/workflows/search_youtube.yml" target="_blank">➕ جستجوی جدید</a>
    </div>
    <div class="results">'''

    cards = ""
    if not videos:
        cards = '''<div style="text-align: center; padding: 40px; color: #666;">⚠️ نتیجه‌ای یافت نشد.</div>'''
    else:
        for v in videos:
            try:
                title = html.escape(str(v.get('title', 'بدون عنوان')))
                channel = html.escape(str(v.get('channel', v.get('uploader', 'نامشخص'))))
                duration = str(v.get('duration', ''))
                views = str(v.get('view_count', v.get('views', '')))
                thumb = v.get('thumbnail', v.get('thumbnails', [{}])[-1].get('url', ''))
                video_url = v.get('webpage_url', v.get('url', ''))
                download_link = make_download_url(video_url)

                card = f'''
        <div class="video-card">
            <img class="thumbnail" src="{thumb}" alt="thumbnail">
            <div class="info">
                <div class="title">
                    <a href="{video_url}" target="_blank">{title}</a>
                    <button class="copy-btn" onclick="copyLink('{video_url}')" title="کپی لینک ویدئو">📋</button>
                </div>
                <div class="channel">{channel}</div>
                <div class="meta">⏱ {duration} | 👁 {views}</div>
                <a href="{download_link}" target="_blank"><button class="download-btn">⬇️ دانلود</button></a>
            </div>
        </div>'''
                cards += card
            except Exception as e:
                print(f"خطا در ساخت کارت: {e}")

    html_footer = f'''
    </div>
    <div class="footer">
        ساخته شده توسط GitHub Actions | {time.strftime('%Y-%m-%d %H:%M:%S')}
    </div>
</div>
</body>
</html>'''
    return html_header + cards + html_footer

print("ساخت HTML نتایج یوتیوب...")
try:
    full_html = generate_html()
    full_html = full_html.encode('utf-8', errors='ignore').decode('utf-8')
except Exception as e:
    print(f"خطا: {e}")
    full_html = f"<html><body><h1>خطا در ساخت صفحه</h1><pre>{html.escape(str(e))}</pre></body></html>"

os.makedirs(output_dir, exist_ok=True)
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(full_html)

size_kb = len(full_html.encode('utf-8')) / 1024
print(f"✅ صفحه یوتیوب در {output_file} ذخیره شد. تعداد ویدئوها: {len(videos)} | حجم: {size_kb:.1f} KB")
