#!/usr/bin/env python3
"""Финальная проверка лендинга. Usage: python3 test_interactions.py <index.html>"""
import sys
from playwright.sync_api import sync_playwright

html = sys.argv[1]
out = []
def ok(name, cond): out.append(("✅ PASS " if cond else "❌ FAIL ") + name)

with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    pg = b.new_page(viewport={"width": 1920, "height": 1080})
    msgs = []
    pg.on("console", lambda m: msgs.append(f"{m.type}: {m.text}") if m.type == "error" else None)
    pg.on("pageerror", lambda e: msgs.append(f"PAGEERROR: {e}"))
    pg.goto("file://" + html)
    pg.wait_for_timeout(1300)

    imgs = pg.eval_on_selector_all("img", "els=>els.map(e=>({s:e.getAttribute('src'),w:e.naturalWidth}))")
    broken = [i['s'] for i in imgs if not i['w']]
    ok(f"все изображения загрузились ({len(imgs)} шт)", len(broken) == 0)
    if broken: out.append("     битые: " + ", ".join(broken))

    ok("экранов = 10", pg.eval_on_selector_all(".screen", "e=>e.length") == 10)
    ok("навигационных точек = 10", pg.eval_on_selector_all("#dots a", "e=>e.length") == 10)

    # карусель s4
    a0 = pg.eval_on_selector("#s4 .cstep.active", "e=>e.querySelector('h3').textContent")
    pg.click("#s4 .cnav button:last-child"); pg.wait_for_timeout(650)
    a1 = pg.eval_on_selector("#s4 .cstep.active", "e=>e.querySelector('h3').textContent")
    ok(f"карусель «что делает» листает ({a0} → {a1})", a0 != a1)

    # тумблер s5
    pg.click("#bp"); pg.wait_for_timeout(160)
    ok("тумблер Промпт ⇄ Скилл", pg.get_attribute("#s5", "data-state") == "prompt")
    pg.click("#bs"); pg.wait_for_timeout(160)

    # проводник s6 — раскрыть папку и кликнуть видимый файл
    files = pg.query_selector_all("#s6 .node.file")
    pg.click("#s6 .node.dir"); pg.wait_for_timeout(220)
    vis = pg.query_selector_all("#s6 .kids:not(.closed) .node.file")
    bef = pg.inner_text("#dname"); vis[0].click(); pg.wait_for_timeout(160)
    ok(f"проводник «под капотом» ({len(files)} файлов, раскрытие+выбор)", pg.inner_text("#dname") != bef)

    # прорастание s7
    pg.eval_on_selector("#s7 .way", "e=>e.click()"); pg.wait_for_timeout(250)
    ok("прорастание «3 пути» (клик раскрывает шаги)", pg.eval_on_selector("#s7 .way", "e=>e.classList.contains('open')"))

    # hover-улыбка s3 (наличие двух слоёв)
    ok("Прохор: 2 слоя для hover-улыбки", pg.eval_on_selector_all("#s3 .figwrap img", "e=>e.length") == 2)

    # навигация
    pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(200)
    pg.keyboard.press("ArrowDown"); pg.wait_for_timeout(750)
    ok(f"навигация ↓ листает экраны (scrollY={int(pg.evaluate('window.scrollY'))})", pg.evaluate("window.scrollY") > 100)

    b.close()

print("\n".join(out))
print("\nЛог консоли/ошибки:", " | ".join(msgs) if msgs else "чисто, ошибок нет")
fails = [o for o in out if o.startswith("❌")]
print("\nИТОГ:", "ВСЁ РАБОТАЕТ ✅" if not fails else f"{len(fails)} проблем — чиним")
