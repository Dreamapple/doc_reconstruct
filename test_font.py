from PIL import ImageFont, ImageDraw, Image

image = Image.new("RGB", (1024, 512))

draw = ImageDraw.Draw(image)

# use a truetype font
font = ImageFont.truetype("PingFang.ttc", 150)

draw.text((10, 25), "在介绍变现之前", font=font)

image.show()
