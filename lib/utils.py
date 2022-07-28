from textwrap import dedent
from datetime import datetime
from typing import Optional
from pathlib import Path

from logging import getLogger
logger = getLogger(__name__)

def save_metadata(pdf_path: Path, original_url: str, pdf_url: Optional[str]):
    metadata_path = pdf_path.with_suffix('.pdf.metadata')
    with open(metadata_path, 'w') as f:
        f.write(dedent(
            f"""
            Original_url: {original_url}
            pdf_url: {pdf_url}
            Downloaded_at: {datetime.now()}
        """).strip())
    logger.debug(f"Metadata saved into {metadata_path}")