from typing import List
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from textwrap import wrap
import logging
from pathlib import Path
from glob import glob

logging.basicConfig(
    format='%(asctime)s: %(funcName)s: %(levelname)s: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class Post:
    def __init__(
            self, message='',
            size=1350, template=None,
            bounding_box=None,
            padding=0,
            font_file_path=None,
            font_size=12
    ) -> None:
        self.image = self._load_image(template)
        self.font = self._define_font(
            None if font_file_path is None else Path(font_file_path), font_size)
        self.bounding_box = self._define_bounding_box(bounding_box, size)
        self.message = self._format_message(bounding_box, message, self.font)
        self._X, self._Y = self._center(
            bounding_box, len(self.message), font_size)
        self.leading = font_size+padding
        self._draw()

    def _define_bounding_box(self, bounding_box, size) -> List:
        if bounding_box is None:
            bounding_box = [0.05*size, 0.1*size, 0.95*size, 0.9*size]
        return bounding_box

    def _format_message(self, bounding_box, message, font) -> List:
        width = bounding_box[2]-bounding_box[0]
        pars = [' '.join(par.split()) for par in message.split('\n') if par]
        i = 1
        while True:
            longest = max([max(wrap(par, i), key=len)
                          for par in pars], key=len)
            if font.getsize(longest)[0] > width:
                return [line for par in pars for line in wrap(par, i-2)]
            i += 1

    def _center(self, bounding_box, lines, font_size) -> tuple[int, int]:
        X = (bounding_box[2] - bounding_box[0])/2 + bounding_box[0]
        Y = (bounding_box[3] - bounding_box[1])/2 + \
            bounding_box[1] - (lines-1)*font_size/2
        return X, Y

    def _is_valid(self) -> bool:
        if self._Y < self.bounding_box[1]:
            logger.error("Message bigger than bounding box")
            return False
        return True

    def _load_image(self, template):
        if template is None:
            try:
                return Image.open(glob('*.png')[0])
            except IndexError:
                logger.error("No template found")
                exit()
        else:
            try:
                return Image.open(str(Path(template)))
            except OSError:
                logger.error

    def _define_font(self, path, font_size):
        if path is None:
            try:
                return ImageFont.truetype(glob('*.ttf')[0], size=font_size)
            except IndexError:
                logger.error("No font found")
                exit()
        else:
            try:
                return ImageFont.truetype(str(path), size=font_size)
            except OSError:
                logger.error(f"Font {path} not found")
                exit()

    def _draw(self):
        if self._is_valid():
            draw = ImageDraw.Draw(self.image)
            for line in self.message:
                x, y = self.font.getsize(line)
                draw.text((self._X - x/2, self._Y - y/2),
                          line, fill="black", font=self.font)
                self._Y += self.leading

    def show(self):
        self.image.show()

    def post(api):
        api.post

    def save(self):
        path = Path("posts")
        if not path.exists():
            path.mkdir(exist_ok=True)
        i = 0
        while (path/Path(f'posts_{i}.png')).exists():
            i += 1
        path /= Path(f'posts_{i}.png')
        self.image.save(path, "PNG")


def main():
    bounding_box = [70, 200, 1280, 1150]
    msg = "Sample message.\n This is seriously a sample message. You will not find any info here whatsoever!"
    post = Post(msg, bounding_box=bounding_box, font_size=70, padding=10)
    post.show()
    post.save()


if(__name__ == "__main__"):
    main()
