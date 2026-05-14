import json
import os
import time
import base64
import urllib.request
import html

repo = os.environ.get('REPO', '')

# خواندن داده‌ها
videos = []
if os.path.exists('data.json') and os.path.getsize('data.json') > 0:
    with open('data.json', encoding='utf-8') as f:
        videos = [json.loads(line) for line in f if line.strip()]
    print(f"📖 {len(videos)} ویدیو از data.json بارگیری شد.")
else:
    print("⚠️ فایل data.json خالی یا وجود ندارد.")

# تابع تبدیل تعداد بازدید به رشته با کاما
def format_views(views):
    if not views:
        return "۰"
    try:
        return f"{int(views):,}"
    except:
        return str(views)

# تابع تبدیل ثانیه به HH:MM:SS یا MM:SS
def format_duration(seconds):
    if not seconds:
        return "۰:۰۰"
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"

# شروع ساخت HTML
html_header = f'''<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>نتایج جستجو – یوتیوب</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f9f9f9; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ text-align: center; color: #ff0000; margin-bottom: 20px; font-size: 2rem; }}
        .search-btn {{ text-align: center; margin-bottom: 30px; }}
        .search-btn a {{ background: #ff0000; color: white; padding: 10px 20px; text-decoration: none; border-radius: 8px; display: inline-block; font-weight: bold; }}
        .results {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 25px; }}
        .card {{ background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1); transition: 0.2s; }}
        .card:hover {{ transform: translateY(-5px); }}
        .thumb {{ width: 100%; aspect-ratio: 16/9; object-fit: cover; }}
        .info {{ padding: 15px; }}
        .title {{ font-size: 1rem; font-weight: 600; margin-bottom: 8px; line-height: 1.4; display: flex; align-items: flex-start; gap: 8px; }}
        .title a {{ text-decoration: none; color: #0f0f0f; flex: 1; }}
        .title a:hover {{ text-decoration: underline; color: #ff0000; }}
        .channel {{ color: #606060; font-size: 0.85rem; margin-bottom: 10px; word-break: break-word; }}
        .action-btns {{ display: flex; gap: 5px; margin-top: 5px; }}
        .copy-btn, .download-btn {{ background: none; border: none; cursor: pointer; font-size: 1.1rem; padding: 4px 8px; border-radius: 6px; transition: 0.2s; }}
        .copy-btn {{ color: #606060; background: #f1f1f1; }}
        .copy-btn:hover {{ background: #e0e0e0; color: #ff0000; }}
        .download-btn {{ color: white; background: #ff0000; border-radius: 6px; text-decoration: none; display: inline-flex; align-items: center; gap: 4px; }}
        .download-btn:hover {{ background: #cc0000; }}
        .details {{ display: flex; justify-content: space-between; font-size: 0.75rem; color: #606060; border-top: 1px solid #e5e5e5; padding-top: 10px; margin-top: 5px; }}
        .footer {{ text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #888; font-size: 0.8rem; }}
        @media (max-width: 600px) {{ .results {{ grid-template-columns: 1fr; }} }}
    </style>
    <script>
        function copyLink(url) {{
            navigator.clipboard.writeText(url).then(() => alert('✅ لینک کپی شد!')).catch(() => prompt('لینک را کپی کنید:', url));
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

cards_html = ""
if not videos:
    cards_html = '<div style="grid-column: 1/-1; text-align: center; padding: 40px;">⚠️ هیچ نتیجه‌ای یافت نشد. لطفاً عبارت دیگری را امتحان کنید.</div>'
else:
    for v in videos:
        try:
            title = html.escape(v.get('title', 'بدون عنوان'))
            uploader = html.escape(v.get('uploader', 'نامشخص'))
            webpage_url = v.get('webpage_url', '#')
            views = v.get('view_count', 0)
            duration = v.get('duration', 0)
            views_str = format_views(views)
            duration_str = format_duration(duration)
            
            # لینک مستقیم به workflow دانلود با video_url پر شده
            download_url = f"https://github.com/Amin5v5/download/actions/workflows/YouTube_Downloader.yml?video_url={webpage_url}"
            
            # دریافت تصویر بندانگشتی
            thumb_url = ''
            if 'thumbnails' in v and isinstance(v['thumbnails'], list) and len(v['thumbnails']) > 0:
                thumb_url = v['thumbnails'][-1].get('url', '')
            if not thumb_url:
                thumb_url = v.get('thumbnail', '')
            
            thumb_base64 = None
            if thumb_url:
                try:
                    req = urllib.request.Request(thumb_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        image_data = resp.read()
                    b64 = base64.b64encode(image_data).decode('utf-8')
                    thumb_base64 = f"data:image/jpeg;base64,{b64}"
                except Exception:
                    pass
            
            if not thumb_base64:
                thumb_base64 = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='320' height='180'%3E%3Crect width='320' height='180' fill='%23cccccc'/%3E%3C/svg%3E"
            
            card = f'''
        <div class="card">
            <img class="thumb" src="{thumb_base64}" loading="lazy" alt="thumbnail">
            <div class="info">
                <div class="title">
                    <a href="{webpage_url}" target="_blank">{title}</a>
                </div>
                <div class="channel">{uploader}</div>
                <div class="action-btns">
                    <button class="copy-btn" onclick="copyLink('{webpage_url}')" title="کپی لینک ویدیو">📋 کپی لینک</button>
                    <a href="{download_url}" class="download-btn" target="_blank" title="رفتن به صفحه دانلود (مخزن download)">⬇️ دانلود</a>
                </div>
                <div class="details">
                    <span>👁️ {views_str} بازدید</span>
                    <span>⏱️ {duration_str}</span>
                </div>
            </div>
        </div>'''
            cards_html += card
        except Exception as e:
            print(f"⚠️ خطا در ساخت کارت برای یک ویدیو: {e}")

html_footer = f'''
    </div>
    <div class="footer">
        ✅ ساخته شده توسط GitHub Actions | آخرین به‌روزرسانی: {time.strftime('%Y-%m-%d %H:%M:%S')}
    </div>
</div>
</body>
</html>'''

full_html = html_header + cards_html + html_footer

os.makedirs('search_results', exist_ok=True)
with open('search_results/index.html', 'w', encoding='utf-8') as f:
    f.write(full_html)

print(f"✅ صفحه HTML با موفقیت ساخته شد. تعداد ویدیوها: {len(videos)}")
