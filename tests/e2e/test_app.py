import pytest
from flask import url_for
from playwright.sync_api import Page, expect
import sys
import multiprocessing

if sys.platform == 'darwin':
    multiprocessing.set_start_method("fork")


@pytest.mark.usefixtures("live_server")
def test_index(page: Page) -> None:
    page.goto(url_for("index", _external=True))

    expect(page.get_by_role("paragraph")).to_contain_text("Hello, World!")
