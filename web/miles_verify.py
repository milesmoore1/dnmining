"""Real-browser verification of miles_atlas.html. Fails loudly; loads the page."""
import functools, http.server, socketserver, threading, time
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
PORT = 8734


def serve():
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(HERE))
    httpd = socketserver.TCPServer(("127.0.0.1", PORT), h)
    httpd.daemon_threads = True
    threading.Thread(target=httpd.serve_forever, daemon=True).start()


def main():
    serve(); time.sleep(0.6)
    problems, notes = [], []
    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_page(viewport={"width": 1400, "height": 900})
        cerr, perr = [], []
        pg.on("console", lambda m: cerr.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e: perr.append(str(e)))
        pg.goto(f"http://127.0.0.1:{PORT}/miles_atlas.html", wait_until="networkidle")
        try:
            pg.wait_for_function("window.__ready===true", timeout=15000)
        except Exception:
            problems.append("window.__ready never true")

        box = pg.eval_on_selector("#map", "el=>({w:el.clientWidth,h:el.clientHeight})")
        notes.append(f"map {box['w']}x{box['h']}")
        if not box["w"] or not box["h"]:
            problems.append("map container zero size")

        time.sleep(2.0)
        tiles = pg.eval_on_selector_all("img.leaflet-tile", "e=>e.filter(x=>x.complete&&x.naturalWidth>0).length")
        notes.append(f"tiles painted: {tiles}")
        if tiles == 0:
            problems.append("zero tiles painted")

        feats = pg.eval_on_selector_all("path.leaflet-interactive", "e=>e.length")
        notes.append(f"vector features: {feats}")
        if feats == 0:
            problems.append("no data features rendered")

        # metrics box populated with his numbers
        acc = pg.eval_on_selector("#m_acc", "e=>e.textContent")
        auc = pg.eval_on_selector("#m_auc", "e=>e.textContent")
        notes.append(f"sidebar metrics: acc={acc} auc={auc}")
        if acc.strip() in ("", "–"):
            problems.append("metrics not populated")

        # panel populates on click (select a sample programmatically like a click)
        sid = pg.evaluate("() => { const s=DATA[0]; selectSample(s); return s.id; }")
        time.sleep(0.3)
        big = pg.eval_on_selector("#panel .hd .big", "e=>e.textContent")
        pid = pg.evaluate("() => document.querySelector('#panel .geo b').textContent")
        notes.append(f"panel after click: id={pid} P(high)={big}")
        if not big or "%" not in big or pid != sid:
            problems.append(f"panel did not populate on click (id={pid}, big={big})")

        pg.screenshot(path=str(HERE / "miles_shot_national.png"))
        pg.evaluate("map.setView([37.3,-82.0],8)"); time.sleep(1.3)  # Central Appalachian
        pg.evaluate("() => { const s=DATA.find(x=>x.p_high>0.8)||DATA[0]; selectSample(s); }")
        time.sleep(0.4)
        pg.screenshot(path=str(HERE / "miles_shot_points.png"))
        pg.locator("#panel").scroll_into_view_if_needed()
        pg.locator("#side").screenshot(path=str(HERE / "miles_panel.png"))

        notes.append(f"console errors: {len(cerr)} | page errors: {len(perr)}")
        if cerr:
            problems.append("console errors: " + " || ".join(cerr[:5]))
        if perr:
            problems.append("page errors: " + " || ".join(perr[:5]))
        br.close()

    print("\n=== NOTES ==="); [print("  -", n) for n in notes]
    print("\n=== RESULT ===")
    if problems:
        print("FAIL:"); [print("  ✗", p) for p in problems]; raise SystemExit(1)
    print("PASS — all checks green")
    for f in sorted(HERE.glob("miles_shot_*.png")) + [HERE / "miles_panel.png"]:
        print("  screenshot:", f.name)


if __name__ == "__main__":
    main()
