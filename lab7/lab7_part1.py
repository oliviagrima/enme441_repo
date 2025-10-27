import RPi.GPIO as GPIO
import socket

# --- Configuración de los pines ---
GPIO.setmode(GPIO.BCM)
pins = [14, 15, 18]
for pin in pins:
    GPIO.setup(pin, GPIO.OUT)

# Inicializamos PWM a 1000 Hz
pwms = [GPIO.PWM(p, 1000) for p in pins]
for pwm in pwms:
    pwm.start(0)

# --- Estado inicial de los LEDs ---
led_brightness = [0, 0, 0]

# --- Generar HTML dinámico ---
def generate_html(selected_led=0):
    slider_value = led_brightness[selected_led]
    html = f"""\
<!DOCTYPE html>
<html>
<head><title>LED Control</title></head>
<body>
<h3>Brightness level:</h3>
<form method="POST" action="/">
    <input type="range" name="brightness" min="0" max="100" value="{slider_value}">
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

# --- Parsear POST ---
def parse_post_data(data):
    try:
        body = data.split("\r\n\r\n", 1)[1]
        params = dict(param.split("=") for param in body.split("&"))
        led = int(params.get("led", 1)) - 1
        brightness = int(params.get("brightness", 0))
        return led, brightness
    except:
        return None, None

# --- Servidor ---
def start_server(host="0.0.0.0", port=8080):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(5)
    print(f"Server running at http://{host}:{port}/")

    try:
        while True:
            conn, addr = s.accept()

            # Leer todo el request
            request_data = b""
            while True:
                chunk = conn.recv(1024)
                if not chunk:
                    break
                request_data += chunk
            request = request_data.decode(errors="ignore")

            selected_led = 0

            # Procesar POST
            if "POST" in request:
                led, brightness = parse_post_data(request)
                if led is not None and 0 <= led < 3:
                    led_brightness[led] = brightness
                    pwms[led].ChangeDutyCycle(brightness)
                    selected_led = led
                    print(f"→ LED {led+1} brightness set to {brightness}%")

            # Generar HTML y enviar respuesta
            html = generate_html(selected_led)
            response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {}\r\n\r\n{}".format(len(html), html)
            conn.sendall(response.encode())
            conn.close()

    except KeyboardInterrupt:
        print("\nStopping server...")
    finally:
        for pwm in pwms:
            try:
                pwm.stop()
            except:
                pass
        GPIO.cleanup()
        s.close()

if __name__ == "__main__":
    start_server()
