from PIL import Image, ImageDraw, ImageFont

font_size = 30
white = (255, 255, 255)
status_colors = {
    "green": (10, 200, 20),
    "yellow": (255, 200, 0),
    "red": (240, 0, 0)
}

def make_image(status: dict):
    img = Image.new("RGB", (1500, 500), (40,40,45))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("./meiryo.ttc", size=font_size)

    draw.text((25,10), "Service Status", fill=white, font=font)

    max_width = 0
    for service in status.keys():
        width, _ = draw.textsize(service, font=font)
        if  width > max_width:
            max_width = width

    y = 40
    for service in status.keys():
        ex = 450 - font_size
        tx = 450
        draw.ellipse((ex, y + 5, ex + font_size, y + font_size + 5), fill=status_colors[status[service]])
        draw.text((tx + 10, y), service, fill=white, font = font)
        y += font_size + 15

    img.save("./tmp/tmp.png")