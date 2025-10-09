import board
import adafruit_lis3dh
import time
import supervisor
import busio

def i2c_init_if_devices_present(scl_pin = board.SCL, sda_pin = board.SDA, frequency = 400000) -> busio.I2C:
    try:        
        i2c = busio.I2C(scl_pin, sda_pin, frequency=frequency)
        print("I2C initialized successfully")
        return i2c
    except (ValueError, RuntimeError) as e:
        return None

def i2c_list_devices(i2c):
    if i2c is None:
        return []

    # Display I2C devices
    while not i2c.try_lock():
            pass
    try:
        devices = i2c.scan()
        print("I2C addresses found:", [hex(device_address) for device_address in devices])
        return devices
    finally:
        i2c.unlock()

def imu_init_if_present(i2c) -> adafruit_lis3dh.LIS3DH_I2C:
    if i2c is None:
        return None
    try:
        lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c)
        lis3dh.range = adafruit_lis3dh.RANGE_2_G
        return lis3dh
    except OSError as e:
        print("LIS3DH can not be initialized:", e)
        return None
    
def reboot():
    print("Rebooting in ", end="")
    for i in range(3, 0, -1):
        print(i, end="...")
        time.sleep(1)
    supervisor.reload()
    
# Hardware I2C setup:
i2c = i2c_init_if_devices_present()
if i2c:
    i2c_list_devices(i2c)

lis3dh = imu_init_if_present(i2c)

while True:
    try:
        if lis3dh is not None:
            # Read accelerometer values (in m / s ^ 2).  Returns a 3-tuple of x, y,
            # z axis values.
            x, y, z = lis3dh.acceleration
            print('x = {}G, y = {}G, z = {}G'.format(x / 9.806, y / 9.806, z / 9.806))
        
        if i2c is None:
            i2c = i2c_init_if_devices_present()
            if i2c is not None:
                print("I2C device detected")
                reboot()
                
        # Small delay to keep things responsive but give time for interrupt processing.
        time.sleep(0.1)
    except OSError as e:
        print("Error in main loop:", e)
        reboot()