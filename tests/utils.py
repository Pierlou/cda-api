from tempfile import NamedTemporaryFile

import requests


def download(url: str) -> str:
    with requests.get(url, stream=True) as response:
        response.raise_for_status()

        with NamedTemporaryFile(delete=False) as tmp:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    tmp.write(chunk)

    return tmp.name
