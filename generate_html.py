import json, os, time, base64, urllib.request

repo = os.environ.get('REPO', '')

# خواندن داده‌ها (اگر فایل وجود نداشت یا خالی بود)
if not os.path.exists('data.json') or os.path.getsize('data.json') == 0:
    videos = []
else:
    with open('data.json', encoding='utf-8') as f:
        videos = [json.loads(line) for line in f if line.strip()]

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
        .copy-btn {{ background: none; border: none; cursor: pointer; font-size: 1.1rem; padding: 2px; color: #606060; transition: 0.2s; }}
        .copy-btn:hover {{ color: #ff0000; }}
        .channel {{ color: #606060; font-size: 0.85rem; margin-bottom: 10px; }}
        .details {{ display: flex; justify-content: space-between; font-size: 0.75rem; color: #606060; border-top: 1px solid #e5e5e5; padding-top: 10px; margin-top: 5px; }}
        .footer {{ text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #888; font-size: 0.8rem; }}
        @media (max-width: 600px) {{ .results {{ grid-template-columns: 1fr; }} }}
    </style>
    <script>
        function copyLink(url) {{
            navigator.clipboard.writeText(url).then(() => {{
                alert('لینک کپی شد!');
            }}).catch(() => {{
                prompt('لینک را کپی کنید:', url);
            }});
        }}
    </script>
</head>
<body>
<div class="container">
    <h1>🎬 نتایج جستجو</h1>
    <div class="search-btn">
        <a href="https://github.com/{repo}/actions/workflows/search.yml" target="_blank">➕ جستجوی جدید</a>
    </div>
    <div class="results">'''

if not videos:
    no_result_card = '''<div style="grid-column: 1/-1; text-align: center; padding: 40px; font-size: 1.2rem; color: #666;">⚠️ هیچ نتیجه‌ای یافت نشد. لطفاً دوباره تلاش کنید.</div>'''
    cards = [no_result_card]
else:
    cards = []
    for v in videos:
        # ---------- مدت زمان ----------
        dur_sec = v.get('duration', 0) or 0
        total_seconds = int(dur_sec)
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

        # ---------- تصویر (دانلود و تبدیل به base64) ----------
        thumb_url = ''
        if 'thumbnails' in v and isinstance(v['thumbnails'], list) and len(v['thumbnails']) > 0:
            # بالاترین کیفیت (آخرین عنصر)
            thumb_url = v['thumbnails'][-1].get('url', '')
        if not thumb_url:
            thumb_url = v.get('thumbnail', '')

        thumb_base64 = None
        if thumb_url:
            try:
                # دانلود تصویر از سرور گیت‌هاب (دسترسی آزاد دارد)
                with urllib.request.urlopen(thumb_url, timeout=10) as resp:
                    image_data = resp.read()
                b64 = base64.b64encode(image_data).decode('utf-8')
                # معمولاً jpg است، ولی می‌توان با توجه به content-type دقیقتر عمل کرد
                thumb_base64 = f"data:image/jpeg;base64,{b64}"
            except Exception as e:
                print(f"خطا در دانلود تصویر {thumb_url}: {e}")

        if not thumb_base64:
            # تصویر جایگزین (همان placeholder) را هم به base64 تبدیل می‌کنیم تا بدون شبکه هم کار کند
            # یک تصویر ساده‌ی خاکستری 1x1 پیکسل به صورت base64
            thumb_base64 = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='320' height='180'%3E%3Crect width='320' height='180' fill='%23cccccc'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' fill='white' font-size='16' font-family='sans-serif'%3ENo Image%3C/text%3E%3C/svg%3E"

        # ---------- نام کانال ----------
        uploader = v.get('uploader', 'نامشخص')
        webpage_url = v['webpage_url']

        card = f'''
        <div class="card">
            <img class="thumb" src="{thumb_base64}" loading="lazy" alt="thumbnail">
            <div class="info">
                <div class="title">
                    <a href="{webpage_url}" target="_blank">{v['title']}</a>
                    <button class="copy-btn" onclick="copyLink('{webpage_url}')" title="کپی لینک">📋</button>
                </div>
                <div class="channel">{uploader}</div>
                <div class="details">
                    <span>👁️ {views_str} بازدید</span>
                    <span>⏱️ {duration_str}</span>
                </div>
            </div>
        </div>'''
        cards.append(card)

html_footer = f'''
    </div>
    <div class="footer">
        ساخته شده توسط GitHub Actions | آخرین به‌روزرسانی: {time.strftime('%Y-%m-%d %H:%M:%S')}
    </div>
</div>
</body>
</html>'''

full_html = html_header + ''.join(cards) + html_footer

os.makedirs('search_results', exist_ok=True)
with open('search_results/index.html', 'w', encoding='utf-8') as f:
    f.write(full_html)

# کپی در ریشه برای GitHub Pages
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(full_html)

print(f"✅ صفحه HTML ساخته شد. تعداد ویدیوها: {len(videos)}")
