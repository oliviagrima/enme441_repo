def generate_html():
    html = """\
<!DOCTYPE html>
<html>
<head>
    <title>LED Control</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin-top: 40px; }
        .slider-container { width: 300px; margin: 20px auto; text-align: left; }
        .slider-label { display: inline-block; width: 50px; }
        input[type=range] { width: 180px; vertical-align: middle; }
        .value-display { display: inline-block; width: 40px; text-align: right; font-weight: bold; }
    </style>
</head>
<body>
    <h2>LED Brightness Control</h2>

    <div class="slider-container">
        <span class="slider-label">LED1</span>
        <input type="range" id="led1" min="0" max="100" value="{led1}" oninput="updateLED(1, this.value)">
        <span id="val1" class="value-display">{led1}</span>
    </div>

    <div class="slider-container">
        <span class="slider-label">LED2</span>
        <input type="range" id="led2" min="0" max="100" value="{led2}" oninput="updateLED(2, this.value)">
        <span id="val2" class="value-display">{led2}</span>
    </div>

    <div class="slider-container">
        <span class="slider-label">LED3</span>
        <input type="range" id="led3" min="0" max="100" value="{led3}" oninput="updateLED(3, this.value)">
        <span id="val3" class="value-display">{led3}</span>
    </div>

    <script>
        function updateLED(led, brightness) {
            // Update number beside slider
            document.getElementById('val' + led).textContent = brightness;
            
            // Send async POST to server
            fetch('/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: 'led=' + led + '&brightness=' + brightness
            })
            .then(response => {
                if (!response.ok) {
                    console.error('Server error:', response.statusText);
                }
            })
            .catch(err => console.error('Fetch error:', err));
        }
    </script>
</body>
</html>
""".format(led1=led_brightness[0], led2=led_brightness[1], led3=led_brightness[2])
    return html

def do_POST(self):
    content_length = int(self.headers['Content-Length'])
    post_data = self.rfile.read(content_length)
    params = urllib.parse.parse_qs(post_data.decode())

    led = int(params.get('led', [1])[0]) - 1
    brightness = int(params.get('brightness', [0])[0])

    if 0 <= led < 3:
        led_brightness[led] = brightness
        pwms[led].ChangeDutyCycle(brightness)
        print(f"→ LED {led+1} brightness set to {brightness}%")

    # Respond with simple OK (no HTML refresh needed)
    self.send_response(200)
    self.end_headers()