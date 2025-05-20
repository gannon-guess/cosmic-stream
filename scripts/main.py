import obsws_python as obsws
import random, time, math
import colorsys


host = "localhost"
port = 4455
password = "secret"

scale = 0.4
image_width = 1000 * scale
image_height = 1000 * scale
speed = 2

scene_name = "Bouncing Logo"

hue = random.randint(0, 360)


def change_color(ws):
    global hue
    dhue = random.randint(30, 330)
    hue = (hue + dhue) % 360
    # Color is AABBGGRR
    r, g, b = colorsys.hsv_to_rgb(hue / 360.0, 0.5, 1.0)

    color = int(f"FF{int(r * 255):02X}{int(g * 255):02X}{int(b * 255):02X}", 16)

    ws.set_source_filter_settings(
        source_name="dvd",
        filter_name="Color Correction",
        settings={"color_multiply": color},
    )


def main():
    # OBS WebSocket connection
    ws = obsws.ReqClient(host=host, port=port, password=password)

    angle = random.choice([45, 135, 225])
    vel_x = math.cos(angle) * speed
    vel_y = math.sin(angle) * speed

    image_x = 10
    image_y = 10

    # Do the thing
    try:
        while True:
            if image_x <= 0 or image_x + image_width >= 1920:
                vel_x = -vel_x
                change_color(ws)
            if image_y <= 0 or image_y + image_height >= 1080:
                vel_y = -vel_y
                change_color(ws)
            image_x += vel_x
            image_y += vel_y
            ws.set_scene_item_transform(
                scene_name=scene_name,
                item_id=ws.get_scene_item_id(
                    scene_name=scene_name, source_name="dvd"
                ).scene_item_id,
                transform={
                    "positionX": image_x,
                    "positionY": image_y,
                    "scaleX": scale,
                    "scaleY": scale,
                },
            )
            time.sleep(0.01)
    except KeyboardInterrupt:
        ws.disconnect()


if __name__ == "__main__":
    main()
