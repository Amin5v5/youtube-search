import json, os, time, base64, urllib.request

repo = os.environ.get('REPO', '')

# خواندن داده‌ها
if not os.path.exists('data_play.json') or os.path.getsize('data_play.json') == 0:
    apps = []
else:
    with open('data_play.json', encoding='utf-8') as f:
        apps = [json.loads(line) for line in f if line.strip()]

html_header = f'''<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>نتایج جستجو – گوگل‌پلی</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f9f9f9; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ text-align: center; color: #34a853; margin-bottom: 20px; font-size: 2rem; }}
        .search-btn {{ text-align: center; margin-bottom: 30px; }}
        .search-btn a {{ background: #34a853; color: white; padding: 10px 20px; text-decoration: none; border-radius: 8px; display: inline-block; font-weight: bold; }}
        .results {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 25px; }}
        .card {{ background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1); transition: 0.2s; display: flex; padding: 15px; align-items: center; }}
        .card:hover {{ transform: translateY(-5px); }}
        .icon {{ width: 64px; height: 64px; object-fit: cover; border-radius: 12px; margin-left: 15px; }}
        .info {{ flex: 1; }}
        .app-name {{ font-size: 1.1rem; font-weight: 600; margin-bottom: 5px; display: flex; align-items: center; gap: 8px; }}
        .app-name a {{ text-decoration: none; color: #0f0f0f; }}
        .app-name a:hover {{ text-decoration: underline; color: #34a853; }}
        .developer {{ color: #606060; font-size: 0.85rem; margin-bottom: 5px; }}
        .meta {{ display: flex; justify-content: space-between; font-size: 0.8rem; color: #606060; }}
        .rating {{ color: #fbbc04; }}
        .install {{ color: #4285f4; }}
        .copy-btn {{ background: none; border: none; cursor: pointer; font-size: 1rem; color: #606060; }}
        .copy-btn:hover {{ color: #34a853; }}
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
    <h1>📱 نتایج جستجوی گوگل‌پلی</h1>
    <div class="search-btn">
        <a href="https://github.com/{repo}/actions/workflows/search_googleplay.yml" target="_blank">➕ جستجوی جدید</a>
    </div>
    <div class="results">'''

if not apps:
    no_result_card = '''<div style="grid-column: 1/-1; text-align: center; padding: 40px; font-size: 1.2rem; color: #666;">⚠️ هیچ نتیجه‌ای یافت نشد. لطفاً عبارت دیگری را امتحان کنید.</div>'''
    cards = [no_result_card]
else:
    cards = []
    for app in apps:
        title = app.get('title', 'بدون نام')
        dev = app.get('developer', 'نامشخص')
        score = app.get('score', 0) or 0
        installs = app.get('installs', 'نامشخص')
        app_id = app.get('appId', '')
        url = f"https://play.google.com/store/apps/details?id={app_id}" if app_id else "#"

        # آیکون (base64)
        icon_url = app.get('icon', '')
        icon_b64 = None
        if icon_url:
            try:
                with urllib.request.urlopen(icon_url, timeout=10) as resp:
                    image_data = resp.read()
                b64 = base64.b64encode(image_data).decode('utf-8')
                icon_b64 = f"data:image/png;base64,{b64}"
            except Exception as e:
                print(f"خطا در دانلود آیکون {icon_url}: {e}")
        if not icon_b64:
            # placeholder داخلی
            icon_b64 = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='64' height='64'%3E%3Crect width='64' height='64' fill='%23cccccc'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' fill='white' font-size='10' font-family='sans-serif'%3EN/A%3C/text%3E%3C/svg%3E"

        card = f'''
        <div class="card">
            <img class="icon" src="{icon_b64}" loading="lazy" alt="icon">
            <div class="info">
                <div class="app-name">
                    <a href="{url}" target="_blank">{title}</a>
                    <button class="copy-btn" onclick="copyLink('{url}')" title="کپی لینک">📋</button>
                </div>
                <div class="developer">{dev}</div>
                <div class="meta">
                    <span class="rating">⭐ {score}</span>
                    <span class="install">📥 {installs}</span>
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

os.makedirs('search_results/googleplay', exist_ok=True)
with open('search_results/googleplay/index.html', 'w', encoding='utf-8') as f:
    f.write(full_html)

# کپی در ریشه برای GitHub Pages
with open('play_index.html', 'w', encoding='utf-8') as f:
    f.write(full_html)

print(f"✅ صفحه گوگل‌پلی ساخته شد. تعداد برنامه‌ها: {len(apps)}")
