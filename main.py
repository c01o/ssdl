#!/usr/bin/env python3
import fire
from urllib.parse import urlparse
from pathlib import Path
from typing import Optional

from logging import basicConfig, getLogger, INFO
basicConfig(level=INFO)
logger = getLogger(__name__)

from lib.slideshare import dl_slideshare
from lib.speakerdeck import dl_speakerdeck
from lib.arxiv import dl_arxiv


def main(url: str, to: Optional[str] = None):
    """
    Download slides.

    Available sites:
     - www.slideshare.net
     - speakerdeck.com
     
    :param url: URL to download.
    :param to: /path/to/download/destination/directory. (Default: `./slides`)
    """
    if to is not None:
        dst = Path(to)
    else:
        dst = Path.cwd() / 'slides'
        
    # Ensure dst
    if not dst.is_dir():
        dst.mkdir(parents=True)
        logger.info(f"Created {dst}")

    match urlparse(url).netloc:
        case 'www.slideshare.net':
            dl_slideshare(url, dst)
        case 'speakerdeck.com':
            dl_speakerdeck(url, dst)
        case 'arxiv.org':
            dl_arxiv(url, dst)
            
if __name__ == '__main__':
    fire.Fire(main)