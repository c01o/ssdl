from bs4 import BeautifulSoup, Tag
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
    soup = get_soup(url)
    title = get_title(soup)
    pdf_path = dst / f'{url.split("/")[-1]}-{title}.pdf'
    
    if pdf_path.exists():
        raise ValueError(f"{pdf_path} Already exists")

    freeze_support()  # For windows multithreadings
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        download_images(soup, tmpdir)
        convert_to_pdf(tmpdir, pdf_path)

    save_metadata(pdf_path, url, title, None)

def get_soup(url: str) -> BeautifulSoup:
    with urlopen(url) as res:
        text = res.read().decode(res.headers.get_content_charset())
    return BeautifulSoup(text, "html.parser")
    
def get_title(soup: BeautifulSoup) -> str:
    assert isinstance(soup.title, Tag)
    assert soup.title.string is not None

    return soup.title.string

def download_images(soup: BeautifulSoup, dest: Path = Path.cwd() / 'slides/tmp'):
    if not dest.is_dir():
        dest.mkdir(parents=True)

    image_urls = scrape_image_urls(soup)

    n_imgs = len(image_urls)
    logger.info(f"{n_imgs} slides found")
    digits = len(str(n_imgs))
    namer = lambda idx, img_url: f"{idx:>0{digits}}-{img_url.split('/')[-1]}"
        
    with ThreadPoolExecutor() as executor:
        for idx, image_url in enumerate(image_urls, start=1):
            # srcset: csv of image urls, with last value being the highest res
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

def scrape_image_urls(soup: BeautifulSoup):
    # Can't simply gather img urls because they are lazy-loaded
    
    # first, find the number of slides
    n_images = len(soup.find_all("div", {'data-testid': 'slide'}))

    # Source tag are like:
    # <source srcset="https://image.slidesharecdn.com/mysql5-151002054115-lva1-app6892/85/mysql-57-1-320.jpg?cb=1665812242 320w,
    #  https://image.slidesharecdn.com/mysql5-151002054115-lva1-app6892/85/mysql-57-1-638.jpg?cb=1665812242 638w,
    #  https://image.slidesharecdn.com/mysql5-151002054115-lva1-app6892/75/mysql-57-1-2048.jpg?cb=1665812242 2048w"
    #  sizes="100vw" type="image/webp" data-testid="slide-image-source">
    #
    # - `-1-` is the slide index (1-oriented)
    # pick the highest resolution from the srcset
    src = soup.find("source", {'data-testid': "slide-image-source"})
    assert type(src) == Tag
    assert type(srcset := src.get("srcset")) == str
    image_url_example = srcset.split(",")[-1].split("?")[0]

    # image urls are like:
    #  https://image.slidesharecdn.com/mysql5-151002054115-lva1-app6892/75/mysql-57-1-2048.jpg"
    # `-1-` is the slide index (1-oriented)
    # Note that slide title can contain `-1-` as well, so we should replace the last occurrence
    # bad example:
    #    image_urls = [image_url_example.replace("-1-", f"-{idx}-") for idx in range(1, n_images + 1)]
    #
    # Iterate over the number of slides and replace the index
    image_urls: list[str] = [image_url_example.rsplit("-", 2)[0] + f"-{idx}-" + image_url_example.rsplit("-", 1)[1] for idx in range(1, n_images + 1)]

    if not image_urls:
        raise ValueError('No images found')
    
    return image_urls
    

def convert_to_pdf(src: Path, dst: Path):
    slides = [img.open('rb') for img in sorted(src.iterdir())]
    with open(dst, "wb") as pdf:
        pdf.write(img2pdf.convert(slides))

    logger.info(f"PDF saved at {dst} ({src=})")