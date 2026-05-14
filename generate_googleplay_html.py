import json
import os
import time
import base64
import urllib.request
import html
import traceback

repo = os.environ.get('REPO', '')
download_owner = 'Amin5v5'
download_repo = 'download'
download_workflow = 'Google_Play_Downloader.yml'  # نام فایل workflow دانلود شما
default_arch = 'arm64-v8a'
default_part_mb = 90

output_dir = 'search_results/googleplay'
output_file = os.path.join(output_dir, 'index.html')

# خواندن داده‌ها
apps = []
if os.path.exists('data_play.json') and os.path.getsize('data_play.json') > 0:
    try:
        with open('data_play.json', 'r', encoding='utf-8') as f:
            apps = [json.loads(line) for line in f if line.strip()]
        print(f"خواندن {len(apps)} برنامه از فایل data_play.json")
    except Exception as e:
        print(f"خطا در خواندن فایل JSON: {e}")

def make_download_url(package_name):
    return (f"https://github.com/{download_owner}/{download_repo}/actions/workflows/{download_workflow}"
            f"?package_name={package_name}"
            f"&architecture={default_arch}"
            f"&max_part_mb={default_part_mb}")

def generate_html():
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
        .results {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 25px; }}
        .card {{ background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1); transition: 0.2s; display: flex; padding: 15px; align-items: center; }}
        .card:hover {{ transform: translateY(-5px); }}
        .icon {{ width: 64px; height: 64px; object-fit: cover; border-radius: 12px; margin-left: 15px; }}
        .info {{ flex: 1; }}
        .app-name {{ font-size: 1.1rem; font-weight: 600; margin-bottom: 5px; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }}
        .app-name a {{ text-decoration: none; color: #0f0f0f; }}
        .app-name a:hover {{ text-decoration: underline; color: #34a853; }}
        .developer {{ color: #606060; font-size: 0.85rem; margin-bottom: 5px; }}
        .meta {{ display: flex; justify-content: space-between; font-size: 0.8rem; color: #606060; flex-wrap: wrap; gap: 8px; }}
        .rating {{ color: #fbbc04; }}
        .install {{ color: #4285f4; }}
        .size {{ color: #0f9d58; }}
        .action-btns {{ margin-top: 8px; }}
        .download-btn {{ background: #34a853; color: white; border: none; cursor: pointer; font-size: 0.9rem; padding: 6px 12px; border-radius: 6px; text-decoration: none; display: inline-block; font-weight: bold; }}
        .download-btn:hover {{ background: #2d9147; }}
        .footer {{ text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #888; font-size: 0.8rem; }}
        @media (max-width: 600px) {{ .results {{ grid-template-columns: 1fr; }} }}
    </style>
    <script>
        function copyLink(url) {{
            navigator.clipboard.writeText(url).then(() => {{
                alert('✅ لینک کپی شد!');
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
        <a href="https://github.com/{repo}/actions/workflows/search_googleplay.yml" target="_blank">🔍 جستجوی جدید</a>
    </div>
    <div class="results">'''

    cards_html = ""
    if not apps:
        cards_html = '''<div style="grid-column: 1/-1; text-align: center; padding: 40px; font-size: 1.2rem; color: #666;">⚠️ هیچ نتیجه‌ای یافت نشد. لطفاً عبارت دیگری را امتحان کنید.</div>'''
    else:
        for i, app_info in enumerate(apps):
            try:
                title = html.escape(str(app_info.get('title', 'بدون نام')))
                dev = html.escape(str(app_info.get('developer', 'نامشخص')))
                installs = html.escape(str(app_info.get('installs', 'نامشخص')))
                app_id = str(app_info.get('appId', ''))
                url = f"https://play.google.com/store/apps/details?id={html.escape(app_id)}" if app_id else "#"
                score = app_info.get('score', 0) or 0
                size = app_info.get('size', 'نامشخص')
                if size and size != 'نامشخص':
                    size_display = str(size).replace('M', ' MB').replace('K', ' KB')
                else:
                    size_display = 'نامشخص'
                
                icon_url = app_info.get('icon', '')
                icon_b64 = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='64' height='64'%3E%3Crect width='64' height='64' fill='%23cccccc'/%3E%3C/svg%3E"
                if icon_url:
                    try:
                        req = urllib.request.Request(icon_url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req, timeout=10) as resp:
                            image_data = resp.read()
                        b64 = base64.b64encode(image_data).decode('utf-8')
                        icon_b64 = f"data:image/png;base64,{b64}"
                    except Exception as e:
                        print(f"اخطار: دانلود آیکون برای {app_id} شکست خورد. از placeholder استفاده می‌شود.")

                card = f'''
        <div class="card">
            <img class="icon" src="{icon_b64}" loading="lazy" alt="icon">
            <div class="info">
                <div class="app-name">
                    <a href="{url}" target="_blank">{title}</a>
                    <button class="copy-btn" onclick="copyLink('{url}')" title="کپی لینک گوگل‌پلی">📋</button>
                </div>
                <div class="developer">{dev}</div>
                <div class="meta">
                    <span class="rating">⭐ {score}</span>
                    <span class="install">📥 {installs}</span>
                    <span class="size">💾 {size_display}</span>
                </div>
                <div class="action-btns">
                    <a href="{make_download_url(app_id)}" class="download-btn" target="_blank">⬇️ دانلود APK</a>
                </div>
            </div>
        </div>'''
                cards_html += card
            except Exception as e:
                print(f"خطا در ساخت کارت برای برنامه {i}: {e}")
                continue

    html_footer = f'''
    </div>
    <div class="footer">
        ساخته شده توسط GitHub Actions | آخرین به‌روزرسانی: {time.strftime('%Y-%m-%d %H:%M:%S')}
    </div>
</div>
</body>
</html>'''

    return html_header + cards_html + html_footer

print("شروع ساخت صفحه HTML...")
try:
    full_html = generate_html()
    full_html = full_html.encode('utf-8', errors='ignore').decode('utf-8')
except Exception as e:
    print(f"خطای مرگبار در ساخت صفحه: {e}")
    traceback.print_exc()
    error_msg = html.escape(f"خطای مرگبار در ساخت صفحه: {e}\n{traceback.format_exc()}")
    full_html = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head><meta charset="UTF-8"><title>خطا</title></head>
<body dir="rtl" style="padding:40px; font-family: Tahoma;">
    <h1 style="color:red;">⚠️ خطا در ساخت صفحه</h1>
    <pre style="background:#f5f5f5; padding:20px; border-radius:8px; white-space: pre-wrap; word-wrap: break-word;">{error_msg}</pre>
</body>
</html>"""

os.makedirs(output_dir, exist_ok=True)
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(full_html)

size_kb = len(full_html.encode('utf-8')) / 1024
print(f"✅ صفحه گوگل‌پلی با موفقیت در {output_file} ذخیره شد. تعداد برنامه‌ها: {len(apps)} | حجم فایل: {size_kb:.1f} KB")
