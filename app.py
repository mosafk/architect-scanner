import os
import exifread
import base64
from flask import Flask, request, render_template_string

app = Flask(__name__)

# واجهة US Military Cyber Command المتقدمة
MILITARY_HUD = """
<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>US CYBERCOM | ARCHITECT SYSTEM</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
        
        :root {
            --cyber-lime: #32ff7e;
            --tactical-olive: #4b5320;
            --slate-gray: #2c3e50;
            --alert-red: #ff3e3e;
            --bg-ultra-dark: #05070a;
        }

        body {
            background-color: var(--bg-ultra-dark);
            background-image: radial-gradient(circle, #1a1a1a 1px, transparent 1px);
            background-size: 30px 30px;
            color: var(--cyber-lime);
            font-family: 'Roboto Mono', monospace;
            margin: 0;
            padding: 0;
            overflow-x: hidden;
        }

        /* الطبقة العلوية للتشفير */
        .overlay {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), 
                        linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
            background-size: 100% 2px, 3px 100%; pointer-events: none; z-index: 1000;
        }

        .container { padding: 30px; max-width: 1400px; margin: auto; }

        .header-system {
            border: 2px solid var(--tactical-olive);
            padding: 20px;
            background: rgba(75, 83, 32, 0.1);
            backdrop-filter: blur(10px);
            display: flex; justify-content: space-between; align-items: center;
            box-shadow: 0 0 20px rgba(50, 255, 126, 0.1);
            margin-bottom: 25px;
        }

        .top-secret-tag {
            color: var(--alert-red);
            border: 2px solid var(--alert-red);
            padding: 5px 15px;
            font-weight: bold;
            text-transform: uppercase;
            animation: blink 1s infinite;
        }

        @keyframes blink { 50% { opacity: 0; } }

        .main-grid { display: grid; grid-template-columns: 1fr 350px; gap: 20px; }

        .panel {
            background: rgba(44, 62, 80, 0.2);
            border: 1px solid var(--tactical-olive);
            padding: 20px;
            position: relative;
            overflow: hidden;
        }

        .panel::after {
            content: ""; position: absolute; top: 0; right: 0;
            border-style: solid; border-width: 0 15px 15px 0;
            border-color: transparent var(--cyber-lime) transparent transparent;
        }

        #map { height: 600px; width: 100%; filter: invert(90%) hue-rotate(180deg) brightness(1.5); border: 1px solid var(--cyber-lime); }

        .data-stream { font-size: 12px; color: var(--cyber-lime); line-height: 1.5; }

        .upload-zone {
            border: 2px dashed var(--cyber-lime);
            padding: 40px; text-align: center; margin-bottom: 20px;
            background: rgba(50, 255, 126, 0.02);
            transition: 0.3s;
        }

        .upload-zone:hover { background: rgba(50, 255, 126, 0.1); }

        input[type="file"] { display: none; }
        .custom-file-upload {
            background: var(--cyber-lime); color: black;
            padding: 12px 30px; cursor: pointer; font-weight: bold;
            display: inline-block; clip-path: polygon(10% 0, 100% 0, 90% 100%, 0% 100%);
        }

        .biometric-hud {
            border-top: 1px solid var(--tactical-olive);
            margin-top: 15px; padding-top: 15px;
        }

        .status-active { color: var(--cyber-lime); }
        .status-offline { color: var(--alert-red); }

    </style>
</head>
<body>
    <div class="overlay"></div>
    <div class="container">
        <div class="header-system">
            <div>
                <h2 style="margin:0; letter-spacing: 3px;">ARCHITECT // CYBER COMMAND</h2>
                <span style="font-size: 10px; color: var(--tactical-olive);">UNITED STATES CYBER SECURITY PROTOCOL v4.0.1</span>
            </div>
            <div class="top-secret-tag">CLASSIFIED // TOP SECRET</div>
        </div>

        <form method="post" enctype="multipart/form-data">
            <div class="upload-zone">
                <label class="custom-file-upload">
                    <input type="file" name="image" onchange="this.form.submit()"/>
                    إطلاق عملية مسح البيانات الميدانية
                </label>
                <p style="font-size: 11px; margin-top:10px;">انقر لرفع الهدف وتحليل الإحداثيات الاستخباراتية</p>
            </div>
        </form>

        {% if res %}
        <div class="main-grid">
            <div class="panel">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <h3 style="margin:0;">TARGET GEO-LOCATION 🛰️</h3>
                    <span class="status-active">● SIGNAL CONNECTED</span>
                </div>
                {% if res.coords %}
                    <div id="map"></div>
                    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
                    <script>
                        var map = L.map('map').setView([{{ res.coords[0] }}, {{ res.coords[1] }}], 14);
                        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png').addTo(map);
                        L.marker([{{ res.coords[0] }}, {{ res.coords[1] }}]).addTo(map)
                            .bindPopup("<b style='color:black'>إحداثيات الهدف المؤكدة</b>").openPopup();
                    </script>
                {% else %}
                    <div style="height: 400px; display: flex; align-items: center; justify-content: center; border: 1px solid var(--alert-red); color: var(--alert-red);">
                        NO GPS DATA DETECTED IN SIGNAL // ENCRYPTION BLOCKED
                    </div>
                {% endif %}
            </div>

            <div class="panel">
                <h3>INTEL STREAM 🔍</h3>
                <div style="text-align: center; margin-bottom: 20px;">
                    <img src="data:image/jpeg;base64,{{ res.img_base64 }}" style="width: 100%; border: 1px solid var(--cyber-lime); filter: grayscale(50%);" />
                </div>
                <div class="data-stream">
                    <div>[DEVICE] >> <span style="color:white">{{ res.details.Brand }} {{ res.details.Model }}</span></div>
                    <div>[SYSTEM] >> <span style="color:white">{{ res.details.OS }}</span></div>
                    <div>[TIMESTAMP] >> <span style="color:white">{{ res.details.DateTime }}</span></div>
                    <div class="biometric-hud">
                        <div style="font-size: 10px; margin-bottom: 5px;">BIOMETRIC ANALYSIS:</div>
                        <div style="height: 5px; background: #111; margin-bottom: 10px;">
                            <div style="width: 85%; height: 100%; background: var(--cyber-lime);"></div>
                        </div>
                        <div>LAT: {{ res.coords[0]|round(5) if res.coords else '0.00000' }}</div>
                        <div>LON: {{ res.coords[1]|round(5) if res.coords else '0.00000' }}</div>
                    </div>
                </div>
                <div style="margin-top: 20px;">
                    {% if res.coords %}
                    <a href="https://www.google.com/maps?q={{ res.coords[0] }},{{ res.coords[1] }}" target="_blank" 
                       style="display: block; text-align: center; color: black; background: var(--cyber-lime); padding: 10px; text-decoration: none; font-weight: bold;">
                        OPEN GOOGLE MAPS 🛰️
                    </a>
                    {% endif %}
                </div>
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
        "Brand": tags.get('Image Make', 'UNKNOWN'),
        "Model": tags.get('Image Model', 'UNKNOWN'),
        "OS": tags.get('Image Software', 'SECURE_ENV'),
        "DateTime": tags.get('Image DateTime', 'TIME_STAMP_HIDDEN'),
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
    return render_template_string(MILITARY_HUD, res=res)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
