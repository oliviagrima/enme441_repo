from http.server import HTTPServer, BaseHTTPRequestHandler
import RPi.GPIO as GPIO
import json

GPIO.setmode(GPIO.BCM)
pins = [14, 15, 18]
pwms = []
for pin in pins:
    GPIO.setup(pin, GPIO.OUT)
    pwm = GPIO.PWM(pin, 1000)
    pwm.start(0)
    pwms.append(pwm)

led_brightness = [0, 0, 0]

html_page = """\
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>LED Control (AJAX)</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            background: #fff;
        }}
        .container {{
            border: 2px solid #000;
            border-radius: 10px;
            padding: 20px 40px;
            display: inline-block;
        }}
        .row {{
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }}
        label {{
            width: 50px;
            font-weight: bold;
        }}
        input[type=range] {{
            flex: 1;
            margin: 0 10px;
        }}
        .value {{
            width: 30px;
            text-align: right;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="row">
            <label>LED1</label>
            <input type="range" id="led1" min="0" max="100" value="0" oninput="updateLED(1, this.value)">
            <span id="val1" class="value">0</span>
        </div>
        <div class="row">
            <label>LED2</label>
            <input type="range" id="led2" min="0" max="100" value="0" oninput="updateLED(2, this.value)">
            <span id="val2" class="value">0</span>
        </div>
        <div class="row">
            <label>LED3</label>
            <input type="range" id="led3" min="0" max="100" value="0" oninput="updateLED(3, this.value)">
            <span id="val3" class="value">0</span>
        </div>
    </div>

    <script>
        function updateLED(led, value) {{
            document.getElementById('val' + led).innerText = value;

            fetch('/', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json'
                }},
                body: JSON.stringify({{ led: led, brightness: value }})
            }})
            .then(response => response.json())
            .then(data => {{
                document.getElementById('val1').innerText = data.leds[0];
                document.getElementById('val2').innerText = data.leds[1];
                document.getElementById('val3').innerText = data.leds[2];
            }})
            .catch(err => console.error('Error:', err));
        }}
    </script>
</body>
</html>
"""

class LEDHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Serve the HTML page
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html_page.encode())

    def do_POST(self):
        # Handle JSON POST requests from JS
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data.decode())
            led = int(data.get('led', 0)) - 1
            brightness = int(data.get('brightness', 0))
            if 0 <= led < 3:
                led_brightness[led] = brightness
                pwms[led].ChangeDutyCycle(brightness)
                print(f"→ LED {led+1} brightness set to {brightness}%")
        except Exception as e:
            print("Error:", e)

        # Respond with current LED brightness values
        response = {'leds': led_brightness}
        response_data = json.dumps(response).encode()

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Content-length", str(len(response_data)))
        self.end_headers()
        self.wfile.write(response_data)

def run(server_class=HTTPServer, handler_class=LEDHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Serving on http://localhost:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
    finally:
        for pwm in pwms:
            pwm.stop()
        GPIO.cleanup()
        httpd.server_close()

if __name__ == "__main__":
    run()
