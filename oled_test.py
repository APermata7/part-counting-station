from luma.core.interface.serial import i2c
from luma.oled.device import sh1106
from PIL import Image, ImageDraw

# Setup I2C
serial = i2c(port=1, address=0x3C)

# Setup OLED
device = sh1106(serial)

# Buat gambar
image = Image.new("1", (device.width, device.height))

draw = ImageDraw.Draw(image)

# Tampilkan text
draw.text((10, 10), "OLED TEST", fill=255)

# Kirim ke OLED
device.display(image)

print("OLED OK")
