from multiprocessing.sharedctypes import Value
from urllib.parse import unquote
from urllib.request import urlopen
from bs4 import BeautifulSoup, Tag
from pathlib import Path

from logging import getLogger
logger = getLogger(__name__)

from .utils import save_metadata

def dl_arxiv(url: str, dst: Path = Path.cwd() / 'slides'):
    assert r"arxiv.org" in url
    
    # https://arxiv.org/abs/1234.56789
    # https://arxiv.org/pdf/1234.56789.pdf
    match url.split('/')[-2]:
        case "pdf":
            abs_url = '.'.join(url.split('.')[:-1]).replace('pdf', 'abs')
            print(abs_url)
            pdf_url = url
        case "abs":
            abs_url = url
            pdf_url = url.replace('abs', 'pdf') + '.pdf'
        case _:
            raise ValueError(f"Unknown URL format: {url}")

    soup = get_soup(abs_url)
    title = get_title(soup)

    pdf_path = dst / f"{unquote(pdf_url.split('/')[-1]).replace('.pdf', '')}-{title}.pdf"
    if pdf_path.exists():
        raise ValueError(f"{pdf_path} Already exists")
        
    with urlopen(pdf_url) as res:
        pdf = res.read()
    with open(pdf_path, 'wb') as f:
        f.write(pdf)

    logger.info(f"PDF saved at {dst} ({url=})")
        
    save_metadata(pdf_path, abs_url, title, pdf_url)
    

def get_soup(url: str) -> BeautifulSoup:
    with urlopen(url) as res:
        text = res.read().decode(res.headers.get_content_charset())
    return BeautifulSoup(text, "html.parser")
    
def get_title(soup: BeautifulSoup):
    title_tag = soup.find("meta", property="og:title")
    title = title_tag["content"] if title_tag else "No_title"

    for tag in soup.find_all("meta"):
        if tag.get("property", None) == "og:title":
            title: str = tag.get("content", None)
            return title.replace('/', '_')
    else:
        raise ValueError('No title meta-tag found')

def scrape_pdf_url(soup: BeautifulSoup) -> str:
    pdf_tag = soup.find(title='Download PDF')
    if not isinstance(pdf_tag, Tag):
        raise ValueError(f'No pdf link found')

    pdf_url = pdf_tag.get('href')
    if not isinstance(pdf_url, str):
        raise ValueError(f"Wrong URL(s): {pdf_url}")

    return pdf_url
