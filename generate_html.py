import json
import os
import time

# خواندن اطلاعات ویدیوها از فایل data.json
with open('data.json', encoding='utf-8') as f:
    videos = [json.loads(line) for line in f]

repo = os.environ.get('REPO', '')  # نام مخزن از environment variable

# قالب HTML (بخش ابتدایی)
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
        .title {{ font-size: 1rem; font-weight: 600; margin-bottom: 8px; line-height: 1.4; }}
        .title a {{ text-decoration: none; color: #0f0f0f; }}
        .title a:hover {{ text-decoration: underline; color: #ff0000; }}
        .channel {{ color: #606060; font-size: 0.85rem; margin-bottom: 10px; }}
        .details {{ display: flex; justify-content: space-between; font-size: 0.75rem; color: #606060; border-top: 1px solid #e5e5e5; padding-top: 10px; margin-top: 5px; }}
        .footer {{ text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #888; font-size: 0.8rem; }}
        @media (max-width: 600px) {{ .results {{ grid-template-columns: 1fr; }} }}
    </style>
</head>
<body>
<div class="container">
    <h1>🎬 نتایج جستجو</h1>
    <div class="search-btn">
        <a href="https://github.com/{repo}/actions/workflows/search.yml" target="_blank">➕ جستجوی جدید</a>
    </div>
    <div class="results">'''

# ساخت کارت‌های ویدیو
cards = []
for v in videos:
    # ---------- مدت زمان (رفع خطای float) ----------
    dur_sec = v.get('duration', 0) or 0
    total_seconds = int(dur_sec)  # تبدیل مستقیم به int
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    if hours > 0:
        duration_str = f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        duration_str = f"{minutes}:{seconds:02d}"

    # ---------- تعداد بازدید ----------
    views = v.get('view_count', 0) or 0
    views_str = f"{views:,}" if views > 0 else "۰"

    # ---------- آدرس عکس بندانگشتی (حل مشکل اصلی) ----------
    thumb = ''
    # روش اول: استفاده از آرایه thumbnails (در حالت --flat-playlist)
    if 'thumbnails' in v and isinstance(v['thumbnails'], list) and len(v['thumbnails']) > 0:
        # آخرین عکس در آرایه معمولاً باکیفیت‌ترین است
        thumb = v['thumbnails'][-1].get('url', '')
    # روش دوم: کلید قدیمی thumbnail
    if not thumb and 'thumbnail' in v:
        thumb = v['thumbnail']
    # اگر هیچکدام نبود، از تصویر placeholder استفاده کن
    if not thumb:
        thumb = "https://placehold.co/320x180?text=No+Image"

    # ---------- نام کانال (در صورت وجود) ----------
    uploader = v.get('uploader', 'نامشخص')

    # ساخت کارت HTML
    card = f'''
        <div class="card">
            <img class="thumb" src="{thumb}" loading="lazy" onerror="this.src='https://placehold.co/320x180?text=Error'">
            <div class="info">
                <div class="title"><a href="{v['webpage_url']}" target="_blank">{v['title']}</a></div>
                <div class="channel">{uploader}</div>
                <div class="details">
                    <span>👁️ {views_str} بازدید</span>
                    <span>⏱️ {duration_str}</span>
                </div>
            </div>
        </div>'''
    cards.append(card)

# بستن تگ‌های HTML
html_footer = f'''
    </div>
    <div class="footer">
        ساخته شده توسط GitHub Actions | آخرین به‌روزرسانی: {time.strftime('%Y-%m-%d %H:%M:%S')}
    </div>
</div>
</body>
</html>'''

# ترکیب نهایی
full_html = html_header + ''.join(cards) + html_footer

# ذخیره فایل
os.makedirs('search_results', exist_ok=True)
with open('search_results/index.html', 'w', encoding='utf-8') as f:
    f.write(full_html)

# کپی در ریشه برای GitHub Pages
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(full_html)

print(f"✅ صفحه HTML ساخته شد. تعداد ویدیوها: {len(videos)}")
