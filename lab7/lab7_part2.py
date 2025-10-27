from http.server import HTTPServer, BaseHTTPRequestHandler
import RPi.GPIO as GPIO
import urllib.parse

# --- CONFIGURACIÓN DE LOS PINES ---
GPIO.setmode(GPIO.BCM)
pins = [14, 15, 18]  # LED1, LED2, LED3
pwms = []
for pin in pins:
    GPIO.setup(pin, GPIO.OUT)
    pwm = GPIO.PWM(pin, 1000)  # Frecuencia 1 kHz
    pwm.start(0)
    pwms.append(pwm)

# --- VALORES INICIALES ---
led_brightness = [0, 0, 0]


# --- FUNCIÓN PARA GENERAR LA PÁGINA HTML + JAVASCRIPT ---
def generate_html():
    return f"""\
<!DOCTYPE html>
<html>
<head>
    <title>LED Control</title>
    <style>
        body {{ font-family: Arial, sans-serif; text-align: center; margin-top: 40px; }}
        .slider-container {{ width: 300px; margin: 20px auto; text-align: left; }}
        .slider-label {{ display: inline-block; width: 50px; }}
        input[type=range] {{ width: 180px; vertical-align: middle; }}
        .value-display {{ display: inline-block; width: 40px; text-align: right; font-weight: bold; }}
    </style>
</head>
<body>
    <h2>LED Brightness Control</h2>

    <div class="slider-container">
        <span class="slider-label">LED1</span>
        <input type="range" id="led1" min="0" max="100" value="{led_brightness[0]}" oninput="updateLED(1, this.value)">
        <span id="val1" class="value-display">{led_brightness[0]}</span>
    </div>

    <div class="slider-container">
        <span class="slider-label">LED2</span>
        <input type="range" id="led2" min="0" max="100" value="{led_brightness[1]}" oninput="updateLED(2, this.value)">
        <span id="val2" class="value-display">{led_brightness[1]}</span>
    </div>

    <div class="slider-container">
        <span class="slider-label">LED3</span>
        <input type="range" id="led3" min="0" max="100" value="{led_brightness[2]}" oninput="updateLED(3, this.value)">
        <span id="val3" class="value-display">{led_brightness[2]}</span>
    </div>

    <script>
        function updateLED(led, brightness) {{
            document.getElementById('val' + led).textContent = brightness;
            fetch('/', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/x-www-form-urlencoded' }},
                body: 'led=' + led + '&brightness=' + brightness
            }})
            .then(response => {{
                if (!response.ok) {{
                    console.error('Error del servidor:', response.statusText);
                }}
            }})
            .catch(err => console.error('Error de conexión:', err));
        }}
    </script>
</body>
</html>
""".format(led1=led_brightness[0], led2=led_brightness[1], led3=led_brightness[2])
    return html


# --- MANEJADOR DE SOLICITUDES HTTP ---
class LEDHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        html = generate_html()
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-length", str(len(html)))
        self.end_headers()
        self.wfile.write(html.encode())

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

        self.send_response(200)
        self.end_headers()


# --- FUNCIÓN PRINCIPAL ---
def run(server_class=HTTPServer, handler_class=LEDHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Serving on http://localhost:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo servidor...")
    finally:
        for pwm in pwms:
            pwm.stop()
        GPIO.cleanup()
        httpd.server_close()
        print("💡 GPIO limpiado correctamente.")


# --- INICIO ---
if __name__ == "__main__":
    run()
