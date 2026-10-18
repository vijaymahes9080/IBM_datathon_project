import os
from PIL import Image, ImageDraw, ImageFont

def make_play_thumbnail():
    thumb_path = "d:/current project/IBM/demo_video/thumbnail.png"
    out_path = "d:/current project/IBM/demo_video/thumbnail_play.png"
    out_root = "d:/current project/IBM/thumbnail_play.png"
    
    if not os.path.exists(thumb_path):
        print("Thumbnail not found!")
        return
        
    img = Image.open(thumb_path).convert("RGBA")
    w, h = img.size
    
    # Create overlay
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Slight dark vignette over center
    cx, cy = w // 2, h // 2
    
    # Outer circle for Play button
    r_outer = 64
    draw.ellipse(
        [cx - r_outer - 10, cy - r_outer - 10, cx + r_outer + 10, cy + r_outer + 10],
        fill=(0, 0, 0, 160)
    )
    draw.ellipse(
        [cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer],
        fill=(15, 23, 42, 220),
        outline=(56, 189, 248, 255),
        width=4
    )
    
    # Play triangle
    tri_w = 40
    tri_h = 48
    draw.polygon(
        [
            (cx - tri_w // 3, cy - tri_h // 2),
            (cx - tri_w // 3, cy + tri_h // 2),
            (cx + 2 * tri_w // 3, cy)
        ],
        fill=(255, 255, 255, 255)
    )
    
    # Try fonts
    font_bold = None
    font_sub = None
    try:
        font_bold = ImageFont.truetype("arialbd.ttf", 26)
        font_sub = ImageFont.truetype("arial.ttf", 18)
    except:
        font_bold = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        
    # Text banner below play button
    text1 = "CLICK TO PLAY DEMONSTRATION VIDEO"
    text2 = "1080p Full HD • 160s • Authentic Live Screen Recording • Subtitles Burned"
    
    # Measure text
    bbox1 = draw.textbbox((0, 0), text1, font=font_bold)
    tw1 = bbox1[2] - bbox1[0]
    bbox2 = draw.textbbox((0, 0), text2, font=font_sub)
    tw2 = bbox2[2] - bbox2[0]
    
    # Background pill for text
    pill_w = max(tw1, tw2) + 60
    pill_h = 75
    pill_y = cy + r_outer + 25
    draw.rounded_rectangle(
        [cx - pill_w // 2, pill_y, cx + pill_w // 2, pill_y + pill_h],
        radius=14,
        fill=(10, 15, 30, 230),
        outline=(56, 189, 248, 180),
        width=2
    )
    
    draw.text((cx - tw1 // 2, pill_y + 12), text1, fill=(255, 255, 255, 255), font=font_bold)
    draw.text((cx - tw2 // 2, pill_y + 44), text2, fill=(147, 197, 253, 255), font=font_sub)
    
    # Composite
    final_img = Image.alpha_composite(img, overlay).convert("RGB")
    final_img.save(out_path, "PNG", quality=95)
    final_img.save(out_root, "PNG", quality=95)
    print(f"Play button thumbnail created: {out_path} and {out_root}")

if __name__ == "__main__":
    make_play_thumbnail()
