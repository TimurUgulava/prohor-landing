#!/usr/bin/env python3
"""Рендер секции лендинга в PNG через системный Chrome (Playwright).
Usage: python3 screenshot.py <index.html> <out.png> [css-selector]
Если selector задан — скроллит секцию в верх вьюпорта и снимает 1920x1080.
"""
import sys
from playwright.sync_api import sync_playwright

html = sys.argv[1]
out = sys.argv[2]
sel = sys.argv[3] if len(sys.argv) > 3 else None

with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    pg = b.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=2)
    pg.goto("file://" + html)
    try:
        pg.evaluate("document.fonts.ready")
    except Exception:
        pass
    pg.wait_for_timeout(900)
    if sel:
        pg.evaluate(
            """(s)=>{const el=document.querySelector(s); if(el){el.scrollIntoView({block:'start'});}}""",
            sel,
        )
        pg.wait_for_timeout(500)
    pg.screenshot(path=out)
    b.close()
print("saved", out)
