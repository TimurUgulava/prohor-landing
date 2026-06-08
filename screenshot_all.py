#!/usr/bin/env python3
"""Снимает все секции лендинга за один запуск Chrome.
Usage: python3 screenshot_all.py <index.html> <outdir> [extra: id:jscall ...]
"""
import sys
from playwright.sync_api import sync_playwright

html = sys.argv[1]
outdir = sys.argv[2]
ids = ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 'sd1', 'sd2', 's8']

with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    pg = b.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
    pg.goto("file://" + html)
    try:
        pg.evaluate("document.fonts.ready")
    except Exception:
        pass
    pg.wait_for_timeout(1300)
    for i in ids:
        pg.evaluate("(s)=>{const e=document.querySelector('#'+s); if(e) window.scrollTo(0, e.offsetTop);}", i)
        pg.wait_for_timeout(450)
        pg.screenshot(path=f"{outdir}/{i}.png")
        print("shot", i)
    # вариант 05 в режиме «промпт»
    pg.evaluate("()=>{ setVS('prompt'); document.querySelector('#s5').scrollIntoView({block:'start'}); }")
    pg.wait_for_timeout(450)
    pg.screenshot(path=f"{outdir}/s5-prompt.png")
    print("shot s5-prompt")
    b.close()
print("done")
