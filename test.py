import PIL.Image
import json
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

from moviepy.editor import ImageClip, concatenate_videoclips, vfx  # Fixed import

def create_video_from_json(data):
    video_width, video_height = data.get("width", 1920), data.get("height", 1080)  # Use dimensions from JSON
    clips = []
    for item in data["slides"]:  # Iterate over slides within the data object
        image_path = item['image_path']
        duration = item['duration']
        in_effect = item.get('in_effect')
        out_effect = item.get('out_effect')
        effect_duration = item.get('effect_duration', 0)

        # Corrected method names
        clip = ImageClip(image_path).resize((video_width, video_height)).set_duration(duration)

        if in_effect == 'fade' and effect_duration > 0:
            clip = clip.fx(vfx.fadein, effect_duration)
        if out_effect == 'fade' and effect_duration > 0:
            clip = clip.fx(vfx.fadeout, effect_duration)

        clips.append(clip)

    final_clip = concatenate_videoclips(clips)
    final_clip.write_videofile(data.get("output", "output.mp4"), fps=24)


if __name__ == "__main__":
    with open("commands.json", 'r') as f:
        data = json.load(f)
    create_video_from_json(data)  # Pass the entire JSON object