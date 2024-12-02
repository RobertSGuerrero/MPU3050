from machine import Pin, SPI, I2C
from nrf24l01 import NRF24L01
from imu import MPU6050
import struct
import utime

# Configuración de I2C y MPU6050
i2c = I2C(0, scl=Pin(13), sda=Pin(12))
imu = MPU6050(i2c)

# Configuración de SPI y NRF24L01
csn = Pin(5, Pin.OUT)
ce = Pin(17, Pin.OUT)
spi = SPI(0, baudrate=10000000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(19), miso=Pin(16))

nrf = NRF24L01(spi, csn, ce, channel=76, payload_size=32)
nrf.open_tx_pipe(b'1Node')

# Función para enviar datos empaquetados
def enviar_datos():
    try:
        # Obtiene datos del sensor MPU6050
        gyro_x = imu.gyro.x
        gyro_y = imu.gyro.y
        gyro_z = imu.gyro.z
        acc_x = imu.accel.x
        acc_y = imu.accel.y
        acc_z = imu.accel.z

        # Empaqueta los datos en binario (6 floats, 24 bytes en total)
        mensaje = struct.pack("ffffff", gyro_x, gyro_y, gyro_z, acc_x, acc_y, acc_z)

        # Envía los datos por NRF24L01
        nrf.send(mensaje)
        print("Mensaje enviado:", gyro_x, gyro_y, gyro_z, acc_x, acc_y, acc_z)
    except OSError as e:
        print("Error al enviar datos:", e)

# Enviar datos de forma continua sin pausas innecesarias
while True:
    enviar_datos()
    utime.sleep(0.1)  # Intervalo ajustado para tiempo real


