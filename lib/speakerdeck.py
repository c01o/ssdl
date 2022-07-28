from urllib.parse import unquote
from urllib.request import urlopen
from bs4 import BeautifulSoup, Tag
from pathlib import Path

from logging import getLogger
logger = getLogger(__name__)

from .utils import save_metadata

def dl_speakerdeck(url: str, dst: Path = Path.cwd() / 'slides'):
    assert r"speakerdeck.com" in url
    pdf_url = scrape_pdf_url(url)

    pdf_path = dst / unquote(pdf_url.split('/')[-1])
    if pdf_path.exists():
        raise ValueError(f"{pdf_path} Already exists")
        
    with urlopen(pdf_url) as res:
        pdf = res.read()
    with open(pdf_path, 'wb') as f:
        f.write(pdf)

    logger.info(f"PDF saved at {dst} ({url=})")
        
    save_metadata(pdf_path, url, pdf_url)

def scrape_pdf_url(url: str) -> str:
    with urlopen(url) as res:
        text = res.read().decode(res.headers.get_content_charset())
    soup = BeautifulSoup(text, "html.parser")
    pdf_tag = soup.find(title='Download PDF')
    if not isinstance(pdf_tag, Tag):
        raise ValueError(f'No pdf link found on {url}')

    pdf_url = pdf_tag.get('href')
    if not isinstance(pdf_url, str):
        raise ValueError(f"Wrong URL(s): {pdf_url}")

    return pdf_url
