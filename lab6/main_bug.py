# ejemplo de uso
from bug import Bug
import time

b = Bug()  # usa valores por defecto: timestep=0.1, x=3, isWrapOn=False

b.start()  # empieza a mover el LED

time.sleep(5)  # deja que se mueva por 5 segundos

b.stop()   # detiene y apaga LEDs
