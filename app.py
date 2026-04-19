import os
import exifread
import base64
from flask import Flask, request, render_template_string

app = Flask(__name__)

# واجهة US Military Cyber Warfare Command المتقدمة (Deep Red Edition)
CYBER_WARFARE_UI = """
<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>US CYBERCOM | RED ALERT SYSTEM</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
        
        :root {
            --war-red: #ff0000;
            --deep-red: #4a0000;
            --cyber-black: #050000;
            --tactical-gray: #1a1a1a;
        }

        body {
            background-color: var(--cyber-black);
            color: var(--war-red);
            font-family: 'Roboto Mono', monospace;
            margin: 0; padding: 0; overflow-x: hidden;
            background-image: linear-gradient(rgba(0,0,0,0.9), rgba(0,0,0,0.9)), 
                              url('https://www.transparenttextures.com/patterns/carbon-fibre.png');
        }

        /* شريط البيانات المتحرك (Binary Matrix) */
        .matrix-bg {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            opacity: 0.1; pointer-events: none; z-index: -1;
            font-size: 10px; overflow: hidden; color: var(--war-red);
        }

        .container { padding: 20px; max-width: 1400px; margin: auto; position: relative; }

        .header-command {
            border: 1px solid var(--war-red);
            background: rgba(74, 0, 0, 0.2);
            padding: 15px; display: flex; justify-content: space-between; align-items: center;
            box-shadow: 0 0 30px rgba(255, 0, 0, 0.2);
            border-right: 10px solid var(--war-red);
            margin-bottom: 30px;
        }

        .top-secret {
            background: var(--war-red); color: black;
            padding: 5px 20px; font-weight: bold; border-radius: 2px;
            animation: pulse 1.5s infinite;
        }

        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }

        .main-layout { display: grid; grid-template-columns: 1fr 400px; gap: 20px; }

        .panel-war {
            background: rgba(26, 26, 26, 0.8);
            border: 1px solid #333; border-top: 3px solid var(--war-red);
            padding: 20px; position: relative; backdrop-filter: blur(5px);
        }

        #map { 
            height: 550px; width: 100%; 
            filter: grayscale(1) invert(1) sepia(1) hue-rotate(-50deg) saturate(5) brightness(0.7); 
            border: 1px solid var(--war-red);
        }

        .upload-btn {
            background: transparent; color: var(--war-red);
            border: 2px solid var(--war-red); padding: 15px 40px;
            font-weight: bold; cursor: pointer; text-transform: uppercase;
            transition: 0.4s; position: relative; overflow: hidden;
        }

        .upload-btn:hover { background: var(--war-red); color: black; box-shadow: 0 0 50px var(--war-red); }

        .intel-box { font-size: 13px; line-height: 1.8; }
        .intel-label { color: #666; text-transform: uppercase; font-size: 10px; }
        .intel-value { color: #fff; border-bottom: 1px solid #222; display: block; }

        .hud-scan {
            position: absolute; top: 0; left: 0; width: 100%; height: 2px;
            background: var(--war-red); box-shadow: 0 0 15px var(--war-red);
            animation: scanning 3s linear infinite;
        }

        @keyframes scanning { 0% { top: 0; } 100% { top: 100%; } }

        @media (max-width: 900px) { .main-layout { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="matrix-bg" id="matrix"></div>
    <div class="container">
        <div class="header-command">
            <div>
                <h1 style="margin:0; letter-spacing: 5px;">ARCHITECT // CYBER WARFARE</h1>
                <small style="color: #666;">COMMAND CENTER - LEVEL 5 ACCESS ONLY</small>
            </div>
            <div class="top-secret">TOP SECRET // CLASSIFIED</div>
        </div>

        <div style="text-align: center; margin-bottom: 40px;">
            <form method="post" enctype="multipart/form-data">
                <label>
                    <input type="file" name="image" onchange="this.form.submit()" style="display:none;"/>
                    <div class="upload-btn">بدء عملية سحب البيانات الاستخباراتية 🔒</div>
                </label>
            </form>
        </div>

        {% if res %}
        <div class="main-layout">
            <div class="panel-war">
                <div class="hud-scan"></div>
                <h3 style="margin-top:0;">📍 تتبع الموقع الجغرافي (TARGET GPS)</h3>
                {% if res.coords %}
                    <div id="map"></div>
                    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
                    <script>
                        var map = L.map('map').setView([{{ res.coords[0] }}, {{ res.coords[1] }}], 13);
                        L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png').addTo(map);
                        L.marker([{{ res.coords[0] }}, {{ res.coords[1] }}]).addTo(map);
                    </script>
                    <div style="margin-top:15px; text-align:center;">
                        <a href="https://www.google.com/maps?q={{ res.coords[0] }},{{ res.coords[1] }}" target="_blank" style="color: var(--war-red); text-decoration: none; border: 1px solid var(--war-red); padding: 5px 15px;">Google Maps 🛰️</a>
                    </div>
                {% else %}
                    <div style="height:400px; display:flex; align-items:center; justify-content:center; border: 1px dashed var(--war-red); color: var(--war-red);">
                        [ACCESS DENIED] >> NO GPS COORDINATES FOUND IN PACKET
                    </div>
                {% endif %}
            </div>

            <div class="panel-war">
                <h3>INTEL REPORT 🔍</h3>
                <div style="text-align:center; margin-bottom: 20px;">
                    <img src="data:image/jpeg;base64,{{ res.img_base64 }}" style="width: 100%; border: 1px solid var(--war-red); filter: grayscale(1) contrast(1.5);" />
                </div>
                <div class="intel-box">
                    <span class="intel-label">الموديل:</span>
                    <span class="intel-value">{{ res.details.Brand }} {{ res.details.Model }}</span>
                    
                    <span class="intel-label">وقت الالتقاط:</span>
                    <span class="intel-value">{{ res.details.DateTime }}</span>
                    
                    <span class="intel-label">الحالة الجغرافية:</span>
                    <span class="intel-value">{{ 'مؤمنة' if res.coords else 'مشفرة/مخفية' }}</span>
                    
                    <div style="margin-top: 20px; font-size: 10px; color: #444;">
                        CRYPTO-HASH: {{ res.img_base64[:40] }}...
                    </div>
                </div>
            </div>
        </div>
        {% endif %}
    </div>

    <script>
        // تأثير شاشة المصفوفة (Matrix)
        const matrix = document.getElementById('matrix');
        let code = "";
        for(let i=0; i<5000; i++) {
            code += Math.floor(Math.random()*2);
            if(i % 100 == 0) code += "<br>";
        }
        matrix.innerHTML = code;
    </script>
</body>
</html>
"""

def get_exif_data(file_storage):
    tags = exifread.process_file(file_storage)
    details = {
        "Brand": tags.get('Image Make', 'UNKNOWN'),
        "Model": tags.get('Image Model', 'UNKNOWN'),
        "DateTime": tags.get('Image DateTime', 'HIDDEN'),
    }
    coords = None
    lat_data = tags.get('GPS GPSLatitude')
    lon_data = tags.get('GPS GPSLongitude')
    if lat_data and lon_data:
        def convert(v):
            d = float(v.values[0].num) / float(v.values[0].den)
            m = float(v.values[1].num) / float(v.values[1].den)
            s = float(v.values[2].num) / float(v.values[2].den)
            return d + (m/60.0) + (s/3600.0)
        lat, lon = convert(lat_data), convert(lon_data)
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
    return render_template_string(CYBER_WARFARE_UI, res=res)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
