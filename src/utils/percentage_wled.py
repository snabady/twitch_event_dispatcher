import json
import sys

def hex_to_rgb(hex_color):
    """Wandle #RRGGBB oder RRGGBB in ein [R,G,B]-Array um."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        raise ValueError("HEX-Farbe muss 6 Zeichen haben")
    return [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]

def parse_color(color_str):
    """Erkennt RGB-Liste oder HEX-String."""
    if color_str.startswith("#") or len(color_str) == 6:
        return hex_to_rgb(color_str)
    # Versuche als Komma-separierte RGB-Werte
    try:
        parts = [int(x) for x in color_str.split(",")]
        if len(parts) == 3 and all(0 <= x <= 255 for x in parts):
            return parts
    except Exception:
        pass
    raise ValueError("Farbe muss als #RRGGBB, RRGGBB oder R,G,B angegeben werden.")

def wled_percent_2d_json(percent, color, width, height, orientation="row", off_color=[0,0,0]):
    percent = max(0, min(100, percent))
    led_count = width * height
    num_on = int(led_count * percent / 100)
    matrix = []
    for y in range(height):
        row = []
        for x in range(width):
            idx = y * width + x if orientation == "row" else x * height + y
            if idx < num_on:
                row.append(color)
            else:
                row.append(off_color)
        matrix.append(row)
    # Flache Liste für WLED erzeugen (Zeile für Zeile oder Spalte für Spalte)
    led_flat = []
    if orientation == "row":
        for row in matrix:
            led_flat.extend(row)
    else:  # orientation == "col"
        for x in range(width):
            for y in range(height):
                led_flat.append(matrix[y][x])
    return json.dumps({"seg": [{"i": led_flat}]})

def wled_percent_2d_multipin_json(percent, color, pins=4, matrices_per_pin=3, matrix_size=8, off_color=[0,0,0]):
    percent = max(0, min(100, percent))
    leds_per_matrix = matrix_size * matrix_size
    leds_per_pin = leds_per_matrix * matrices_per_pin
    total_leds = leds_per_pin * pins
    num_on = int(total_leds * percent / 100)
    led_flat = []
    count = 0
    for pin in range(pins):
        for mat in range(matrices_per_pin):
            for y in range(matrix_size):
                for x in range(matrix_size):
                    # Mapping: Zeile für Zeile durch jede Matrix, alle Matrizen pro Pin, dann nächster Pin
                    if count < num_on:
                        led_flat.append(color)
                    else:
                        led_flat.append(off_color)
                    count += 1
    return json.dumps({"seg": [{"i": led_flat}]})
def wled_percent_bar_8x96(percent, color, width=96, height=8, pins=4, off_color=[0,0,0]):
    percent = max(0, min(100, percent))
    total_leds = width * height
    num_on = int(total_leds * percent / 100)
    # Wir bauen ein 2D-Pixelarray (Zeile für Zeile, links nach rechts)
    matrix = []
    count = 0
    for y in range(height):
        row = []
        for x in range(width):
            if count < num_on:
                row.append(color)
            else:
                row.append(off_color)
            count += 1
        matrix.append(row)

    # Jetzt muss passend für WLED multipin gemappt werden!
    leds_per_pin = width // pins * height  # = 24*8 = 192
    led_flat = []
    for pin in range(pins):
        x_start = pin * (width // pins)
        x_end = x_start + (width // pins)
        for y in range(height):
            for x in range(x_start, x_end):
                led_flat.append(matrix[y][x])

    return json.dumps({"seg": [{"i": led_flat}]})

if __name__ == "__masdn__":
    if len(sys.argv) < 2:
        print("Nutzung: python wled_8x96_multipin_percentbar.py <prozent> [farbe]")
        print("Standardfarbe: #00FFFF")
        sys.exit(1)
    percent = int(sys.argv[1])
    color = parse_color(sys.argv[2]) if len(sys.argv) > 2 else [0,255,255]
    print(wled_percent_bar_8x96(percent, color))
def wled_percent_bar_json(percent, color, led_count=30, off_color=[0,0,0]):
    percent = max(0, min(100, percent))
    num_on = int(led_count * percent / 100)
    bar = []
    for i in range(led_count):
        if i < num_on:
            bar.append(color)
        else:
            bar.append(off_color)
    # WLED JSON: Ein Segment, alle LEDs gesetzt
    return json.dumps({"seg": [{"i": bar}]})

if __name__ == "__sna__":

    if len(sys.argv) < 5:
        print("Nutzung: python wled_percent_2dmatrix_json.py <prozent> <farbe> <breite> <hoehe> [orientation]")
        print("Beispiel: python wled_percent_2dmatrix_json.py 25 #00FF00 8 8")
        print("         orientation: 'row' (Standard) oder 'col' (Spaltenweise füllen)")
        sys.exit(1)
    percent = int(sys.argv[1])
    color = parse_color(sys.argv[2])
    width = int(sys.argv[3])
    height = int(sys.argv[4])
    orientation = sys.argv[5] if len(sys.argv) > 5 else "row"
    print(wled_percent_2d_json(percent, color, width, height, orientation))
def wled_percent_colbar_8x96(percent, color, width=96, height=8, pins=4, off_color=[0,0,0]):
    percent = max(0, min(100, percent))
    filled_cols = int(width * percent / 100)
    # Matrix: Zeile y, Spalte x. Fülle alle Zeilen in den ersten filled_cols Spalten
    matrix = []
    for y in range(height):
        row = []
        for x in range(width):
            if x < filled_cols:
                row.append(color)
            else:
                row.append(off_color)
        matrix.append(row)

    # Multi-Pin-Mapping: Für jeden Pin, für jede Spalte (dieses Pins), für jede Zeile: matrix[y][x]
    led_flat = []
    cols_per_pin = width // pins  # 24
    for pin in range(pins):
        x_start = pin * cols_per_pin
        x_end = x_start + cols_per_pin
        for x in range(x_start, x_end):
            for y in range(height):
                led_flat.append(matrix[y][x])

    return json.dumps({"seg": [{"i": led_flat}]})

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Nutzung: python wled_8x96_percentbar_cols_multipin.py <prozent> [farbe]")
        print("Standardfarbe: #00FFFF")
        sys.exit(1)
    percent = int(sys.argv[1])
    color = parse_color(sys.argv[2]) if len(sys.argv) > 2 else [0,255,255]
    print(wled_percent_colbar_8x96(percent, color))
if __name__ == "__bkn__":
    if len(sys.argv) < 2:
        print("Nutzung: python wled_2d_multipin_json.py <prozent> [farbe] [pins] [matrizen_pro_pin] [matrix_groesse]")
        print("Standardfarbe: #00FFFF, pins=4, matrizen=3, matrix=8x8")
        sys.exit(1)
    percent = int(sys.argv[1])
    color = parse_color(sys.argv[2]) if len(sys.argv) > 2 else [0,255,255]
    pins = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    matrices_per_pin = int(sys.argv[4]) if len(sys.argv) > 4 else 3
    matrix_size = int(sys.argv[5]) if len(sys.argv) > 5 else 8
    print(wled_percent_2d_multipin_json(percent, color, pins, matrices_per_pin, matrix_size))
