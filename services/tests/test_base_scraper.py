import sys
from pathlib import Path
import pytest

sys.path.append(str(Path(__file__).parent.parent))
from base_scraper import BaseScraper, WrongProxyStructure, NotWorkingProxy


@pytest.mark.asyncio
async def test_base_scraper():
    scraper = BaseScraper()

    data = await scraper.request("https://example.com/")
    assert "Example Domain" in data


@pytest.mark.asyncio
async def test_base_scraper_proxy():
    proxy = "168.196.238.17:9494@TbUVdy:MGHGRx"

    scraper = await BaseScraper.new(proxy)
    data = await scraper.request("https://example.com/")
    assert "Example Domain" in data


@pytest.mark.asyncio
async def test_base_scraper_not_working_proxy():
    proxy = "154.195.18.33:63004@GFNau6gw:9J9siqgu"

    error = None
    try:
        scraper = await BaseScraper.new(proxy)
    except NotWorkingProxy as ex:
        error = ex

    assert isinstance(error, NotWorkingProxy)


@pytest.mark.asyncio
async def test_base_srcaper_fake_proxy():
    proxy = "abc@3134:14123"

    error = None
    try:
        scraper = await BaseScraper.new(proxy)
    except WrongProxyStructure as ex:
        error = ex

    assert isinstance(error, WrongProxyStructure)
