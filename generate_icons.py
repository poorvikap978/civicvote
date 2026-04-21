from PIL import Image, ImageDraw, ImageFont
import os

os.makedirs('static/icons', exist_ok=True)

for size in [192, 512]:
    img = Image.new('RGB', (size, size), '#0a2342')
    draw = ImageDraw.Draw(img)

    # Gold circle background
    margin = size // 8
    draw.ellipse([margin, margin, size - margin, size - margin], fill='#f4a726')

    # White ballot box shape
    box_w = size // 3
    box_h = size // 2.5
    bx = (size - box_w) // 2
    by = (size - box_h) // 2 + size // 12
    draw.rectangle([bx, by, bx + box_w, by + box_h], fill='#0a2342')

    # Slot on top of box
    slot_w = box_w // 2
    slot_h = max(4, size // 40)
    sx = bx + (box_w - slot_w) // 2
    sy = by - slot_h - 2
    draw.rectangle([sx, sy, sx + slot_w, sy + slot_h], fill='#0a2342')

    # Check mark / tick inside box
    tick_size = box_w // 3
    tx = bx + box_w // 2
    ty = by + box_h // 2
    draw.line([(tx - tick_size//2, ty), (tx - tick_size//6, ty + tick_size//3),
               (tx + tick_size//2, ty - tick_size//3)],
              fill='#f4a726', width=max(2, size // 64))

    img.save(f'static/icons/icon-{size}.png')
    print(f'Created icon-{size}.png')

print('Done!')