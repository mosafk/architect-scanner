import os
import exifread
import base64
from flask import Flask, request, render_template_string

app = Flask(__name__)

# واجهة عسكرية استخباراتية مطورة
MILITARY_INTERFACE = """
<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MILITARY INTELLIGENCE | ARCHITECT</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <style>
        :root { --main-color: #00ff41; --danger-color: #ff0000; --bg-dark: #020202; }
        body { background: var(--bg-dark); color: var(--main-color); font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; overflow-x: hidden; }
        .scanner-line { width: 100%; height: 2px; background: var(--main-color); position: fixed; top: 0; left: 0; box-shadow: 0 0 15px var(--main-color); animation: scan 4s linear infinite; z-index: 100; opacity: 0.3; }
        @keyframes scan { 0% { top: 0; } 100% { top: 100%; } }
        .container { padding: 20px; max-width: 1200px; margin: auto; }
        .header { border-bottom: 2px solid var(--main-color); padding: 10px; text-align: center; background: rgba(0, 255, 65, 0.05); }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }
        .panel { border: 1px solid var(--main-color); background: rgba(0,0,0,0.8); padding: 15px; position: relative; }
        .panel::before { content: "TOP SECRET"; position: absolute; top: -10px; left: 10px; background: var(--bg-dark); padding: 0 5px; font-size: 10px; color: var(--main-color); border: 1px solid var(--main-color); }
        #map { height: 500px; width: 100%; border: 1px solid var(--main-color); filter: hue-rotate(140deg) brightness(0.8) contrast(1.2); }
        .btn-deploy { background: var(--main-color); color: #000; border: none; padding: 15px; width: 100%; font-weight: bold; cursor: pointer; text-transform: uppercase; letter-spacing: 2px; }
        .btn-deploy:hover { box-shadow: 0 0 20px var(--main-color); }
        .data-row { border-bottom: 1px solid #111; padding: 8px 0; display: flex; justify-content: space-between; }
        .label { color: #888; font-size: 0.8em; }
        .value { color: #fff; font-family: 'Courier New'; }
        .warning-box { border: 1px solid var(--danger-color); color: var(--danger-color); padding: 10px; text-align: center; margin-top: 10px; font-size: 12px; }
        @media (max-width: 768px) { .grid { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="scanner-line"></div>
    <div class="container">
        <div class="header">
            <h1 style="margin:0; letter-spacing: 5px;">نظام ARCHITECT لاستخراج البيانات الاستخباراتية</h1>
            <p style="font-size: 12px; opacity: 0.7;">بوابة الدخول العسكرية - التتبع الجغرافي المتقدم</p>
        </div>

        <div class="panel" style="margin-top: 20px; text-align: center;">
            <form method="post" enctype="multipart/form-data">
                <input type="file" name="image" accept="image/*" required style="margin-bottom: 10px;">
                <button type="submit" class="btn-deploy">بدء عملية السحب والتحليل الميداني 💀</button>
            </form>
        </div>

        {% if res %}
        <div class="grid">
            <div class="panel">
                <h3 style="border-bottom: 1px solid var(--main-color);">📍 تحديد الموقع الجغرافي (GPS)</h3>
                {% if res.coords %}
                    <div id="map"></div>
                    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
                    <script>
                        var map = L.map('map').setView([{{ res.coords[0] }}, {{ res.coords[1] }}], 15);
                        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
                        L.marker([{{ res.coords[0] }}, {{ res.coords[1] }}]).addTo(map)
                            .bindPopup("<b>إحداثيات الهدف</b>").openPopup();
                    </script>
                    <div style="margin-top:10px; text-align: center;">
                        <a href="https://www.google.com/maps?q={{ res.coords[0] }},{{ res.coords[1] }}" target="_blank" style="color: var(--main-color);">فتح في خرائط جوجل Google Maps 🛰️</a>
                    </div>
                {% else %}
                    <div class="warning-box">
                        ⚠️ تحذير: لم يتم العثور على إحداثيات GPS في هذه الصورة.<br>
                        السبب المحتمل: الصورة تم ضغطها أو مسح بياناتها بواسطة منصات التواصل.
                    </div>
                    <p style="font-size: 12px; color: #666;">* اطلب من المصدر إرسال الصورة كـ "ملف/مستند" عبر واتساب للحصول على الموقع.</p>
                {% endif %}
            </div>

            <div class="panel">
                <h3 style="border-bottom: 1px solid var(--main-color);">🔍 البيانات الاستخباراتية المستخرجة</h3>
                <div style="text-align: center; margin-bottom: 15px;">
                    <img src="data:image/jpeg;base64,{{ res.img_base64 }}" style="max-height: 200px; border: 1px solid #333;" />
                </div>
                <div class="data-row"><span class="label">الماركة:</span><span class="value">{{ res.details.Brand }}</span></div>
                <div class="data-row"><span class="label">الموديل:</span><span class="value">{{ res.details.Model }}</span></div>
                <div class="data-row"><span class="label">نظام التشغيل:</span><span class="value">{{ res.details.OS }}</span></div>
                <div class="data-row"><span class="label">وقت الالتقاط:</span><span class="value">{{ res.details.DateTime }}</span></div>
                <div class="data-row"><span class="label">الدقة:</span><span class="value">{{ res.details.Resolution }}</span></div>
                <div class="data-row"><span class="label">خط العرض:</span><span class="value">{{ res.coords[0] if res.coords else 'N/A' }}</span></div>
                <div class="data-row"><span class="label">خط الطول:</span><span class="value">{{ res.coords[1] if res.coords else 'N/A' }}</span></div>
            </div>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

def get_exif_data(file_storage):
    tags = exifread.process_file(file_storage)
    details = {
        "Brand": tags.get('Image Make', 'غير معروف'),
        "Model": tags.get('Image Model', 'غير معروف'),
        "OS": tags.get('Image Software', 'غير معروف'),
        "DateTime": tags.get('Image DateTime', 'غير معروف'),
        "Resolution": f"{tags.get('EXIF ExifImageWidth', '0')}x{tags.get('EXIF ExifImageLength', '0')}"
    }
    
    coords = None
    lat_data = tags.get('GPS GPSLatitude')
    lon_data = tags.get('GPS GPSLongitude')
    
    if lat_data and lon_data:
        def convert_to_degrees(value):
            d = float(value.values[0].num) / float(value.values[0].den)
            m = float(value.values[1].num) / float(value.values[1].den)
            s = float(value.values[2].num) / float(value.values[2].den)
            return d + (m / 60.0) + (s / 3600.0)
        
        lat = convert_to_degrees(lat_data)
        lon = convert_to_degrees(lon_data)
        
        if tags.get('GPS GPSLatitudeRef', 'N').values != 'N': lat = -lat
        if tags.get('GPS GPSLongitudeRef', 'E').values != 'E': lon = -lon
        coords = [lat, lon]
        
    return details, coords

@app.route('/', methods=['GET', 'POST'])
def index():
    res = None
    if request.method == 'POST':
        file = request.files.get('image')
        if file:
            img_content = file.read()
            img_base64 = base64.b64encode(img_content).decode('utf-8')
            file.seek(0)
            details, coords = get_exif_data(file)
            res = {"img_base64": img_base64, "details": details, "coords": coords}
    return render_template_string(MILITARY_INTERFACE, res=res)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
