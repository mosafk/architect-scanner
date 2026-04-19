import os
import exifread
from flask import Flask, request, render_template_string

app = Flask(__name__)

# تصميم الواجهة الاحترافية (HTML + CSS + JS)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>Architect Elite Scanner</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <style>
        body { background: #0a0a0a; color: #00ff41; font-family: 'Courier New', Courier, monospace; margin: 0; padding: 20px; }
        .header { border-bottom: 2px solid #00ff41; padding-bottom: 10px; margin-bottom: 20px; text-align: center; text-shadow: 0 0 10px #00ff41; }
        .upload-section { background: #111; border: 1px dashed #00ff41; padding: 30px; text-align: center; border-radius: 10px; }
        .main-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }
        .card { background: #161616; border: 1px solid #333; padding: 15px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,255,65,0.1); }
        #map { height: 450px; width: 100%; border-radius: 8px; border: 1px solid #00ff41; }
        .info-line { border-bottom: 1px solid #222; padding: 8px 0; display: flex; justify-content: space-between; }
        .info-line b { color: #fff; }
        button { background: #00ff41; color: #000; border: none; padding: 10px 25px; font-weight: bold; cursor: pointer; border-radius: 5px; }
        button:hover { background: #00cc33; }
        img { max-width: 100%; border-radius: 5px; border: 1px solid #333; }
        .status-ok { color: #00ff41; font-weight: bold; }
        .status-fail { color: #ff3e3e; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🌐 نظام ARCHITECT لاستخراج البيانات الاستخباراتية 🌐</h1>
    </div>

    <div class="upload-section">
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="image" accept="image/*" required>
            <button type="submit">بدء سحب البيانات 💀</button>
        </form>
    </div>

    {% if res %}
    <div class="main-grid">
        <div class="card">
            <h3>📷 الصورة المحللة والمعلومات:</h3>
            <img src="data:image/jpeg;base64,{{ res.img_base64 }}" /><br><br>
            <div class="info-line"><span>الماركة:</span> <b>{{ res.details.Brand }}</b></div>
            <div class="info-line"><span>الموديل:</span> <b>{{ res.details.Model }}</b></div>
            <div class="info-line"><span>نظام التشغيل:</span> <b>{{ res.details.OS }}</b></div>
            <div class="info-line"><span>وقت الالتقاط:</span> <b>{{ res.details.DateTime }}</b></div>
            <div class="info-line"><span>الدقة:</span> <b>{{ res.details.Resolution }}</b></div>
            <div class="info-line"><span>حالة الـ GPS:</span> 
                <span class="{{ 'status-ok' if res.coords else 'status-fail' }}">
                    {{ '✅ متوفر' if res.coords else '❌ غير متوفر' }}
                </span>
            </div>
        </div>

        <div class="card">
            <h3>📍 الموقع الجغرافي (الدقة العالية):</h3>
            {% if res.coords %}
                <div id="map"></div>
                <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
                <script>
                    var map = L.map('map').setView([{{ res.coords[0] }}, {{ res.coords[1] }}], 17);
                    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
                    L.marker([{{ res.coords[0] }}, {{ res.coords[1] }}]).addTo(map)
                        .bindPopup("<b>موقع الهدف</b>").openPopup();
                </script>
            {% else %}
                <div style="padding: 100px 20px; text-align: center; background: #222;">
                    <p class="status-fail">⚠️ لم يتم العثور على إحداثيات GPS مخفية.</p>
                    <p>السبب: واتساب قام بحذف البيانات أو أن الهدف أغلق الـ GPS أثناء التصوير.</p>
                    <p>💡 اطلب من الهدف إرسال الصورة "كمستند" (Document).</p>
                </div>
            {% endif %}
        </div>
    </div>
    {% endif %}
</body>
</html>
"""

import base64

def get_exif_data(file_storage):
    tags = exifread.process_file(file_storage)
    details = {
        "Brand": tags.get('Image Make', 'غير معروف'),
        "Model": tags.get('Image Model', 'غير معروف'),
        "OS": tags.get('Image Software', 'غير معروف'),
        "DateTime": tags.get('Image DateTime', 'غير معروف'),
        "Resolution": f"{tags.get('EXIF ExifImageWidth')}x{tags.get('EXIF ExifImageLength')}"
    }
    
    # تحويل إحداثيات GPS
    coords = None
    lat = tags.get('GPS GPSLatitude')
    lon = tags.get('GPS GPSLongitude')
    if lat and lon:
        def to_deg(v):
            d = float(v.values[0].num) / float(v.values[0].den)
            m = float(v.values[1].num) / float(v.values[1].den)
            s = float(v.values[2].num) / float(v.values[2].den)
            return d + (m / 60.0) + (s / 3600.0)
        
        lat_v, lon_v = to_deg(lat), to_deg(lon)
        if str(tags.get('GPS GPSLatitudeRef', 'N')) != 'N': lat_v = -lat_v
        if str(tags.get('GPS GPSLongitudeRef', 'E')) != 'E': lon_v = -lon_v
        coords = [lat_v, lon_v]
        
    return details, coords

@app.route('/', methods=['GET', 'POST'])
def index():
    res = None
    if request.method == 'POST':
        file = request.files.get('image')
        if file:
            # قراءة الصورة لتحويلها لـ Base64 للعرض
            img_stream = file.read()
            img_base64 = base64.b64encode(img_stream).decode('utf-8')
            
            # العودة لبداية الملف لقراءته بواسطة exifread
            file.seek(0)
            details, coords = get_exif_data(file)
            res = {"img_base64": img_base64, "details": details, "coords": coords}
            
    return render_template_string(HTML_TEMPLATE, res=res)

if __name__ == '__main__':
    # تشغيل السيرفر على بورت 8080
    app.run(host='0.0.0.0', port=8080, debug=False)
