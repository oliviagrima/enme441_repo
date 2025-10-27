from http.server import HTTPServer, BaseHTTPRequestHandler
import RPi.GPIO as GPIO
import urllib.parse

GPIO.setmode(GPIO.BCM)
pins = [14, 15, 18]
pwms = []
for pin in pins:
    GPIO.setup(pin, GPIO.OUT)
    pwm = GPIO.PWM(pin, 1000)
    pwm.start(0)
    pwms.append(pwm)

led_brightness = [0, 0, 0]  

def generate_html(selected_led=0):
    slider_value = led_brightness[selected_led]
    html = f"""\
<!DOCTYPE html>
<html>
<head><title>LED Control</title></head>
<body>
<h3>Brightness level:</h3>
<form method="POST" action="/">
    <input type="range" name="brightness" min="0" max="100" value="{slider_value}"><br>
    <h3>Select LED:</h3>
    <input type="radio" id="led1" name="led" value="1" {"checked" if selected_led==0 else ""}>
    <label for="led1">LED 1 ({led_brightness[0]}%)</label><br>
    <input type="radio" id="led2" name="led" value="2" {"checked" if selected_led==1 else ""}>
    <label for="led2">LED 2 ({led_brightness[1]}%)</label><br>
    <input type="radio" id="led3" name="led" value="3" {"checked" if selected_led==2 else ""}>
    <label for="led3">LED 3 ({led_brightness[2]}%)</label><br><br>
    <input type="submit" value="Change Brightness">
</form>
</body>
</html>"""
    return html

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
       
        html = generate_html(led)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-length", str(len(html)))
        self.end_headers()
        # Send response body:
        self.wfile.write(html.encode())

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
