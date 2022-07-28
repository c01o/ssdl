from bs4 import BeautifulSoup
import img2pdf
from multiprocessing import freeze_support
from concurrent.futures import ThreadPoolExecutor
from urllib.request import urlopen
from pathlib import Path
from tempfile import TemporaryDirectory

from logging import getLogger
logger = getLogger(__name__)

from .utils import save_metadata

def dl_slideshare(url: str, dst: Path = Path.cwd() / 'slides'):
    assert r"www.slideshare.net" in url
    pdf_path = dst / f'{url.split("/")[-1]}.pdf'
    
    if pdf_path.exists():
        raise ValueError(f"{pdf_path} Already exists")

    freeze_support()  # For windows multithreadings
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        download_images(url, tmpdir)
        convert_to_pdf(tmpdir, pdf_path)

    save_metadata(pdf_path, url, None)

def download_images(url: str, dest: Path = Path.cwd() / 'slides/tmp'):
    if not dest.is_dir():
        dest.mkdir(parents=True)

    images = scrape_image_urls(url)

    n_imgs = len(images)
    logger.info(f"{n_imgs} slides found")
    digits = len(str(n_imgs))
    namer = lambda idx, img_url: f"{idx:>0{digits}}-{img_url.split('/')[-1]}"
        
    with ThreadPoolExecutor() as executor:
        for idx, image in enumerate(images, start=1):
            # srcset: csv of image urls, with last value being the highest res
            image_url = image.get("srcset").split(",")[-1].split("?")[0]
            image_name = namer(idx, image_url)
            image_path = dest / image_name

            if image_path.is_file():
                logger.debug(f"Slide: {idx} exists; skip download")
            else:
                executor.submit(download_slide, idx, image_url, image_path)

    logger.info("Images downloaded")

def download_slide(idx: int, image_url: str, image_path: Path):
    """ Download a slide (page) """

    logger.debug(f"Downloading slide {idx}")
    with open(image_path, "wb") as image:
        with urlopen(image_url) as res:
            image.write(res.read())

def scrape_image_urls(url: str):
    with urlopen(url) as res:
        text = res.read().decode(res.headers.get_content_charset())
    soup = BeautifulSoup(text, "html.parser")
    images = soup.find_all("img", class_="slide-image")

    if not images:
        raise ValueError('No images found')
    
    return images
    

def convert_to_pdf(src: Path, dst: Path):
    slides = [img.open('rb') for img in sorted(src.iterdir())]
    with open(dst, "wb") as pdf:
        pdf.write(img2pdf.convert(slides))

    logger.info(f"PDF saved at {dst} ({src=})")