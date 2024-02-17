from textwrap import dedent
from datetime import datetime
from typing import Optional
from pathlib import Path
from urllib.request import Request, urlopen

from logging import getLogger
logger = getLogger(__name__)

def urlopen_with_ua(url: str, ua: str = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0'):
    req = Request(url)
    req.add_header('User-Agent', ua)
    return urlopen(req)


def save_metadata(pdf_path: Path, original_url: str, title: str, pdf_url: Optional[str]):
    metadata_path = pdf_path.with_suffix('.pdf.log')
    print(title)
    with open(metadata_path, 'w', encoding='utf-8') as f:
        f.write(dedent(
            f"""
            Original_url: {original_url}
            pdf_url: {pdf_url}
            title: {title}
            Downloaded_at: {datetime.now()}
        """).strip())
    logger.debug(f"Metadata saved into {metadata_path}")