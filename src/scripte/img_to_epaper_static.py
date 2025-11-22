import requests
from PIL import Image, ImageDraw, ImageFont

mac = "1337346152ECA442"   # destination mac address
#mac = "6C353C6758649341"
dither = 1  # set dither to 1 is you're sending photos etc
apip = "192.168.0.12"   # ip address of your access point

# Create a new paletted image with indexed colors
image = Image.new('P', (384, 184))

# Define the color palette (white, black, red)
palette = [
    255, 255, 255,  # white
    0, 0, 0,        # black
    255, 0, 0       # red
]

# Assign the color palette to the image
image.putpalette(palette)

# Initialize the drawing context
draw = ImageDraw.Draw(image)

# Define the text lines
line1 = 'current VIP'
line2 = 'ZermalmerDoc'

# Define the fonts and sizes

# Calculate the text bounding boxes to get the text widths and heights

# Convert the image to 24-bit RGB
#rgb_image = image.convert('RGB')

# Save the image as JPEG with maximum quality
#image_path = 'output.jpg'
#image_path = "/home/sna/src/twitch/src/scripte/imgmagick/create_vip_e_paper_image.sh"
image_path = "/home/sna/src/twitch/src/scripte/imgmagick/vip_epaper.png"
#rgb_image.save(image_path, 'JPEG', quality="maximum")

# Prepare the HTTP POST request
url = "http://" + apip + "/imgupload"
payload = {"dither": dither, "mac": mac}  # Additional POST parameter
files = {"file": open(image_path, "rb")}  # File to be uploaded

# Send the HTTP POST request
response = requests.post(url, data=payload, files=files)

# Check the response status
if response.status_code == 200:
    print("Image uploaded successfully!")
else:
    print("Failed to upload the image.")
