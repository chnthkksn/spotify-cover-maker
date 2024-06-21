from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import base64
import uvicorn

app = FastAPI()


class ImageRequest(BaseModel):
    font: str  # regular, regular-italic, medium, bold-italic, extra-bold
    image_base64: str
    title: str
    alignment: str  # 'top-left', 'top-center', 'top-right', 'center-left', 'center', 'center-right', 'bottom-left', 'bottom-center', 'bottom-right'


fontPaths = {
    'regular': './fonts/SpotifyMix-Regular.ttf',
    'regular-italic': './fonts/SpotifyMix-RegularItalic.ttf',
    'medium': './fonts/SpotifyMix-Medium.ttf',
    'bold-italic': './fonts/SpotifyMix-BoldItalic.ttf',
    'extra-bold': './fonts/SpotifyMix-ExtraBold.ttf'
}


def check_font(font):
    if font not in ['regular', 'regular-italic', 'medium', 'bold-italic', 'extra-bold']:
        raise HTTPException(
            status_code=400, detail="Invalid font value, must be one of 'regular', 'regular-italic', 'medium', 'bold-italic', 'extra-bold")


def check_alignment(alignment):
    if alignment not in ['top-left', 'top-center', 'top-right', 'center-left', 'center', 'center-right', 'bottom-left', 'bottom-center', 'bottom-right']:
        raise HTTPException(
            status_code=400, detail="Invalid alignment value, must be one of 'top-left', 'top-center', 'top-right', 'center-left', 'center', 'center-right', 'bottom-left', 'bottom-center', 'bottom-right")


@app.get("/")
async def root():
    return {"message": "Welcome to the text-on-image API"}


@app.post("/text-on-image/")
async def add_text_to_image(request: ImageRequest):
    # Decode the base64 image
    try:
        image_data = base64.b64decode(request.image_base64)
        image = Image.open(BytesIO(image_data))
        image = image.resize((800, 800))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid image data")

    # Check font and alignment values
    check_font(request.font)
    check_alignment(request.alignment)

    # Get the text to be added to the image
    text = request.title

    # Create a drawing object
    draw = ImageDraw.Draw(image)

    # Define text position based on alignment
    width, height = image.size

    # portion of image width you want text width to be
    img_fraction = 0.50

    # Load the font
    font_size = 1
    font_path = fontPaths[request.font]
    font = ImageFont.truetype(font_path, font_size)

    # Get font path and size
    font_color = (255, 255, 255)  # White color
    # get dynamic font size based on image size and text length
    while font.getlength(text) < img_fraction*image.size[0]:
        font_size += 1
        font = ImageFont.truetype(font_path, font_size)

    # add text to the image centered
    text_box = draw.textbbox((0, 0), text, font=font)
    text_width = text_box[2] - text_box[0]
    text_height = text_box[3] - text_box[1]

    # Calculate the position of the text
    if request.alignment == 'top-left':
        position = (0, 0)
    elif request.alignment == 'top-center':
        position = ((width - text_width) // 2, 0)
    elif request.alignment == 'top-right':
        position = (width - text_width, 0)
    elif request.alignment == 'center-left':
        position = (0, (height - text_height) // 2)
    elif request.alignment == 'center':
        position = ((width - text_width) // 2, (height - text_height) // 2)
    elif request.alignment == 'center-right':
        position = (width - text_width, (height - text_height) // 2)
    elif request.alignment == 'bottom-left':
        position = (0, height - text_height)
    elif request.alignment == 'bottom-center':
        position = ((width - text_width) // 2, height - text_height)
    elif request.alignment == 'bottom-right':
        position = (width - text_width, height - text_height)

    # Draw a sample text on the image
    draw.text(position, text, font=font, fill=font_color)

    # Save the edited image to a BytesIO object
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    edited_image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

    return {
        "image_base64": edited_image_base64
    }

if __name__ == "__main__":
    uvicorn.run("__main__:app", host="0.0.0.0",
                port=8000, reload=True, workers=2)
