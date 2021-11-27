from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import textwrap
import logging
import os

logging.basicConfig(
    format='%(asctime)s: %(funcName)s: %(levelname)s: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class Post:
    def __init__(
            self, message='',
            size=1350, template="Template.png",
            bounding_box=None,
            padding=0,
            font="C:/Windows/Fonts/arial.ttf",
            font_size=12
    ) -> None:
        self.image = self._load_image(template)
        self.font = self._define_font(font, font_size)
        self.bounding_box = self._define_bounding_box(bounding_box, size)
        self._width_char = self._define_width_char(bounding_box, self.font)
        self.message = self._format_message(message, self._width_char)
        self._X, self._Y = self._center(
            self.bounding_box, len(self.message), font_size)
        self._draw(self.image, self.message, self.font, font_size+padding)

    def _define_bounding_box(self, bounding_box, size):
        if bounding_box is None:
            bounding_box = [0.05*size, 0.1*size, 0.95*size, 0.9*size]
        return bounding_box

    def _define_width_char(self, bounding_box, font):
        width = bounding_box[2]-bounding_box[0]
        width_tester = 'W'
        while font.getsize(width_tester)[0] < width:
            width_tester += 'W'
        logger.info(f"{len(width_tester)}")
        return len(width_tester)

    def _center(self, bounding_box, lines, font_size):
        X = (bounding_box[2] - bounding_box[0])/2 + bounding_box[0]
        Y = (bounding_box[3] - bounding_box[1])/2 + \
            bounding_box[1] - (lines-1)*font_size/2
        return X, Y

    def _is_valid(self):
        if self._Y < self.bounding_box[1]:
            logger.error("Message bigger than bounding box")
            return False
        return True

    def _load_image(self, template):
        image = Image.open(template)
        return image

    def _define_font(self, font, font_size):
        return ImageFont.truetype(font, font_size)

    def _format_message(self, message, width):
        return textwrap.wrap(message, width)

    def _draw(self, image, message, font, leading):
        draw = ImageDraw.Draw(image)
        for line in message:
            x, y = font.getsize(line)
            draw.text((self._X - x/2, self._Y - y/2),
                      line, fill="black", font=font)
            self._Y += leading

    def show(self):
        if self._is_valid:
            self.image.show()

    def save(self):
        i = 0
        while os.path.exists(f"posts/post_{i}.png"):
            i += 1
        self.image.save(f"posts/post_{i}.png", "PNG")


def main():
    bounding_box = [70, 200, 1280, 1150]
    msg = "Sample message. This is seriously a sample message. You will not find any info here whatsoever!"
    post = Post(msg, bounding_box=bounding_box,
                font="courbd.ttf", font_size=70)
    post.show()
    post.save()


if(__name__ == "__main__"):
    main()
