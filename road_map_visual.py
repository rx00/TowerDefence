from PIL import Image, ImageDraw
from road_map import RoadMap


a = RoadMap(((0, 150), (60, 190), (140, 120), (330, 130),
             (480, 70), (720, 150), (720, 320), (550, 400),
             (450, 300), (280, 410)))

image = Image.new("RGB", (800, 500))
draw = ImageDraw.Draw(image)
for i in a.step_map:
    draw.point(i, "blue")
image.save("img.png", "PNG")