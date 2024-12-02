from phew import server, connect_to_wifi
from machine import SPI, Pin, Timer
from nrf24l01 import NRF24L01
import json
import struct

# Conectar al WiFi
ip = connect_to_wifi("JESUS_VALDES", "123456789")
print("Conectado con IP:", ip)

# Configuración de SPI y NRF24L01
csn = Pin(5, Pin.OUT)
ce = Pin(17, Pin.OUT)
spi = SPI(0, baudrate=10000000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(19), miso=Pin(16))

nrf = NRF24L01(spi, csn, ce, channel=76, payload_size=32)
nrf.open_rx_pipe(0, b'1Node')  # Dirección del transmisor
nrf.start_listening()

# Variables para almacenar lecturas actuales
current_gyro_data = {"gyroX": 0, "gyroY": 0, "gyroZ": 0}
current_acc_data = {"accX": 0, "accY": 0, "accZ": 0}

# Umbral para eliminar ruido
DEAD_ZONE_THRESHOLD = 0.02
STRONG_GYRO_FILTER_THRESHOLD = 0.15  # Aumentar el umbral para gyroZ

# Filtro con media móvil para giroscopio
gyro_buffer = {"gyroX": [], "gyroY": [], "gyroZ": []}
GYRO_BUFFER_SIZE = 10

# Función para filtrar los datos usando un umbral
def apply_dead_zone_filter(value, threshold=DEAD_ZONE_THRESHOLD):
    return value if abs(value) > threshold else 0

# Función para filtrar los datos del giroscopio usando un filtro más fuerte
def apply_strong_gyro_filter(value, threshold=STRONG_GYRO_FILTER_THRESHOLD):
    return value if abs(value) > threshold else 0

# Filtro de media móvil para giroscopio
def apply_moving_average_filter(buffer, new_value):
    buffer.append(new_value)
    if len(buffer) > GYRO_BUFFER_SIZE:
        buffer.pop(0)
    return sum(buffer) / len(buffer)

# Función para recibir y filtrar datos desde el NRF24L01
def recibir_datos():
    if nrf.any():  # Verifica si hay datos disponibles
        try:
            mensaje = nrf.recv()  # Recibir mensaje en binario
            if len(mensaje) >= 24:  # Asegurarse de que el tamaño sea correcto para desempaquetar
                valores = struct.unpack("ffffff", mensaje[:24])  # Desempaquetar los seis datos
                # Aplicar el filtro a cada valor
                gyro_x, gyro_y, gyro_z = (apply_strong_gyro_filter(val) for val in valores[:3])
                acc_x, acc_y, acc_z = (apply_dead_zone_filter(val) for val in valores[3:])

                # Aplicar filtro de media móvil a los valores del giroscopio
                gyro_x = apply_moving_average_filter(gyro_buffer["gyroX"], gyro_x)
                gyro_y = apply_moving_average_filter(gyro_buffer["gyroY"], gyro_y)
                gyro_z = apply_moving_average_filter(gyro_buffer["gyroZ"], gyro_z)  # Eliminar acumulación en gyroZ

                return gyro_x, gyro_y, gyro_z, acc_x, acc_y, acc_z
            else:
                print(f"Mensaje recibido de tamaño incorrecto: {len(mensaje)} bytes")
        except Exception as e:
            print("Error al procesar datos:", e)
    return None  # Retorna None si no hay datos

# Función para actualizar las lecturas en tiempo real
def update_readings(timer):
    global current_gyro_data, current_acc_data

    # Recibir los datos desde el transmisor
    datos = recibir_datos()
    if datos:
        gyro_x, gyro_y, gyro_z = datos[0], datos[1], datos[2]
        acc_x, acc_y, acc_z = datos[3], datos[4], datos[5]

        # Actualizar las lecturas actuales con los datos filtrados
        current_gyro_data = {
            "gyroX": gyro_x,
            "gyroY": gyro_y,
            "gyroZ": gyro_z
        }
        current_acc_data = {
            "accX": acc_x,
            "accY": acc_y,
            "accZ": acc_z
        }

# Configura un temporizador para actualizar lecturas cada 1 ms
timer = Timer(-1)
timer.init(period=1, mode=Timer.PERIODIC, callback=update_readings)

# Ruta principal para mostrar el HTML
@server.route("/", methods=["GET"])
def home(request):
    with open("index.html", "r") as page:
        return page.read()

# Ruta para el archivo de JavaScript
@server.route("/script.js", methods=["GET"])
def serve_js(request):
    with open("script.js", "r") as js_file:
        return js_file.read(), "text/javascript"

# Ruta para enviar datos en JSON
@server.route("/events", methods=["GET"])
def events(request):
    # Procesar los datos antes de enviarlos
    data = {
        "gyro": current_gyro_data,
        "accelerometer": current_acc_data
    }
    return json.dumps(data), "application/json"

# Ruta por defecto para URLs no definidas
@server.catchall()
def catchall(request):
    return "Page not found", 404

# Ejecutar el servidor
server.run()


