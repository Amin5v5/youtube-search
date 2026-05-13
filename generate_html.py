import json, os, time

repo = os.environ['REPO']

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

if not videos:
    no_result_card = '''<div style="grid-column: 1/-1; text-align: center; padding: 40px; font-size: 1.2rem; color: #666;">⚠️ هیچ نتیجه‌ای یافت نشد. لطفاً دوباره تلاش کنید.</div>'''
    cards = [no_result_card]
else:
    cards = []
    for v in videos:
        dur_sec = v.get('duration', 0) or 0
        if dur_sec > 0:
            hours = dur_sec // 3600
            minutes = (dur_sec % 3600) // 60
            seconds = dur_sec % 60
            if hours > 0:
                duration_str = f"{hours}:{minutes:02d}:{seconds:02d}"
            else:
                duration_str = f"{minutes}:{seconds:02d}"
        else:
            duration_str = "نامشخص"
        views = v.get('view_count', 0) or 0
        views_str = f"{views:,}" if views > 0 else "۰"
        thumb = v.get('thumbnail', '')
        if not thumb:
            thumb = "https://placehold.co/320x180?text=No+Image"
        card = f'''
        <div class="card">
            <img class="thumb" src="{thumb}" loading="lazy" onerror="this.src='https://placehold.co/320x180?text=Error'">
            <div class="info">
                <div class="title"><a href="{v['webpage_url']}" target="_blank">{v['title']}</a></div>
                <div class="channel">{v['uploader']}</div>
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

print(f"✅ صفحه HTML ساخته شد. تعداد ویدیوها: {len(videos)}")
