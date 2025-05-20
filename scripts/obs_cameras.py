camera_count = 6
scene_name = "Cameras"

NORTHWEST = 0
NORTHEAST = 1
SOUTHWEST = 2
SOUTHEAST = 3

camera_names = []
with open("cameras.txt", "r") as f:
    camera_names = [line.strip() for line in f if line.strip()]


def set_text(ws, text, direction):
    source_name = f"{["nw", "ne", "sw", "se"][direction]}_text"
    try:
        ws.set_input_settings(
            name=source_name,
            settings={
                "text": text,
            },
            overlay=True,
        )
    except Exception as e:
        print(f"⚠️ Could not set text on {source_name}: {e}")


def set_full_cam(cam_idx, ws):
    for i in range(camera_count):
        source_name = f"camera {i}"
        displayed = i == cam_idx

        item_id = ws.get_scene_item_id(scene_name, source_name).scene_item_id

        ws.set_scene_item_enabled(
            scene_name=scene_name,
            item_id=item_id,
            enabled=displayed,
        )
        if displayed:
            ws.set_scene_item_transform(
                scene_name=scene_name,
                item_id=item_id,
                transform={
                    "positionX": 0.0,
                    "positionY": 0.0,
                    "scaleX": 1.0,
                    "scaleY": 1.0,
                },
            )

    if cam_idx < 0:
        set_text(ws, "", NORTHWEST)
    else:
        set_text(ws, camera_names[cam_idx], NORTHWEST)
    set_text(ws, "", NORTHEAST)
    set_text(ws, "", SOUTHWEST)
    set_text(ws, "", SOUTHEAST)


def set_split_cam(ws, cam_idxs):
    for i in range(camera_count):
        source_name = f"camera {i}"
        displayed = i in cam_idxs

        item_id = ws.get_scene_item_id(scene_name, source_name).scene_item_id

        ws.set_scene_item_enabled(
            scene_name=scene_name,
            item_id=item_id,
            enabled=displayed,
        )
        if displayed:
            direction = cam_idxs.index(i)
            positionX = 0.0 if direction % 2 == 0 else 1920.0 / 2.0
            positionY = 0.0 if direction // 2 == 0 else 1080.0 / 2.0

            ws.set_scene_item_transform(
                scene_name=scene_name,
                item_id=item_id,
                transform={
                    "positionX": positionX,
                    "positionY": positionY,
                    "scaleX": 0.5,
                    "scaleY": 0.5,
                },
            )

    for direction, cam_idx in enumerate(cam_idxs):
        set_text(ws, "" if cam_idx < 0 else camera_names[cam_idx], direction)
