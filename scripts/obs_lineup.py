text_box_count = 11  # number of visible rows
highlighted_row = 3
scene_name = "Lineup"

lineup = []
with open("lineup.txt", "r") as f:
    lineup = [line.strip() for line in f if line.strip()]


def set_highlight(index, ws):
    # Calculate the scroll window range
    start_index = max(0, index - highlighted_row)
    end_index = start_index + text_box_count
    total = len(lineup)

    # Clamp end if near the bottom
    if end_index > total:
        end_index = total
        start_index = max(0, end_index - text_box_count)

    for box_idx, name_idx in enumerate(range(start_index, end_index)):
        school = lineup[name_idx]

        highlighted = name_idx == index
        dimmed = name_idx < index
        color = "FFAAAAAA" if dimmed else "FFCCFFCC" if highlighted else "FFFFFFFF"
        color = int(color, 16)

        source_name = f"lineup {box_idx}"

        try:
            ws.set_input_settings(
                source_name,
                {
                    "text": f"{'> ' if highlighted else ''}{school}",
                    "color1": color,
                    "color2": color,
                },
                overlay=True,
            )

        except Exception as e:
            print(f"⚠️ Could not set text on {source_name}: {e}")

        for i in range(end_index - start_index, text_box_count):
            source_name = f"lineup {i}"
            ws.set_input_settings(
                source_name,
                {
                    "text": "",
                    "color1": 0xFFFFFFFF,
                    "color2": 0xFFFFFFFF,
                },
                overlay=True,
            )
