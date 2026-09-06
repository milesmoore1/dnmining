"""Verify mine DENSITY surface + basins in miles_atlas_3d.html."""
import functools, http.server, socketserver, threading, time
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
PORT = 8748


def serve():
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(HERE))
    httpd = socketserver.TCPServer(("127.0.0.1", PORT), h)
    httpd.daemon_threads = True
    threading.Thread(target=httpd.serve_forever, daemon=True).start()


def order_ok(active):
    """mine density must be below the samples (hex/pts) in draw order."""
    mi = active.index("mines") if "mines" in active else -1
    si = min([active.index(x) for x in ("hex", "pts") if x in active] or [-1])
    return mi != -1 and si != -1 and mi < si


def main():
    serve(); time.sleep(0.6)
    problems, notes = [], []
    with sync_playwright() as p:
        br = p.chromium.launch(args=["--use-gl=swiftshader", "--ignore-gpu-blocklist"])
        pg = br.new_page(viewport={"width": 1500, "height": 950})
        cerr, perr = [], []
        pg.on("console", lambda m: cerr.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e: perr.append(str(e)))
        pg.goto(f"http://127.0.0.1:{PORT}/miles_atlas_3d.html", wait_until="networkidle")
        try:
            pg.wait_for_function("window.__ready===true && window.MINES!==null && window.BASINS!==null", timeout=25000)
        except Exception:
            problems.append("not ready / mines or basins not loaded")
        time.sleep(4)

        notes.append(f"HeatmapLayer available: {pg.evaluate('()=>typeof deck.HeatmapLayer')}")
        notes.append(f"mines loaded: {pg.evaluate('()=>MINES.length')}")

        # density surface shown at NATIONAL zoom now, and under the samples
        actNat = pg.evaluate("() => window.__activeLayerIds||[]")
        notes.append(f"@national active layers: {actNat}")
        if "mines" not in actNat:
            problems.append("mine density not shown at national zoom")
        if not order_ok(actNat):
            problems.append(f"layer order wrong (mines must be below samples): {actNat}")
        pg.screenshot(path=str(HERE / "mines_density_national.png"))

        # regional
        pg.evaluate("() => window.__map.easeTo({center:[-82.5,37.5],zoom:7,pitch:45,duration:700})")
        time.sleep(2.5)
        actReg = pg.evaluate("() => window.__activeLayerIds||[]")
        notes.append(f"@zoom7 active layers: {actReg}")
        if "mines" not in actReg or not order_ok(actReg):
            problems.append(f"density/order wrong at zoom7: {actReg}")

        # toggle off/on
        pg.uncheck("#tmines"); time.sleep(0.6)
        off = pg.evaluate("() => window.__activeLayerIds||[]")
        pg.check("#tmines"); time.sleep(0.6)
        on = pg.evaluate("() => window.__activeLayerIds||[]")
        notes.append(f"toggle: off has mines={('mines' in off)}, on has mines={('mines' in on)}")
        if "mines" in off or "mines" not in on:
            problems.append("mine toggle did not work")

        # filter (abandoned+sealed) still renders
        pg.select_option("#minefilter", "abandoned"); time.sleep(0.8)
        if "mines" not in pg.evaluate("() => window.__activeLayerIds||[]"):
            problems.append("abandoned-only filter dropped the layer")
        pg.select_option("#minefilter", "all"); time.sleep(0.5)

        # nearest-mine list still populates (uses point data)
        pg.evaluate("() => { const s=DATA.find(x=>x.basin==='CENTRAL APPALACHIAN'); if(s)selectSample(s); }")
        time.sleep(0.4)
        nmtxt = pg.evaluate("""() => { const d=[...document.querySelectorAll('#panel details')].find(e=>/Nearest MSHA/.test(e.textContent)); return d?d.textContent:null; }""")
        notes.append(f"nearest-mine present: {bool(nmtxt)}, has km: {'km' in (nmtxt or '')}")
        if not nmtxt or "km" not in nmtxt:
            problems.append("nearest-mine list did not populate")

        # eastern KY close-up: samples readable over density
        pg.evaluate("() => window.__map.easeTo({center:[-83.0,37.2],zoom:9,pitch:55,bearing:-15,duration:900})")
        time.sleep(3)
        pg.evaluate("() => { const s=DATA.find(x=>x.basin==='CENTRAL APPALACHIAN'); if(s)selectSample(s); }")
        time.sleep(0.4)
        pg.screenshot(path=str(HERE / "mines_density_ky.png"))

        notes.append(f"console errors: {len(cerr)} | page errors: {len(perr)}")
        if cerr: problems.append("console errors: " + " || ".join(cerr[:6]))
        if perr: problems.append("page errors: " + " || ".join(perr[:6]))
        br.close()

    print("\n=== NOTES ==="); [print("  -", n) for n in notes]
    print("\n=== RESULT ===")
    if problems:
        print("FAIL:"); [print("  ✗", x) for x in problems]; raise SystemExit(1)
    print("PASS — all checks green")
    for f in ["mines_density_national.png", "mines_density_ky.png"]:
        print("  screenshot:", f)


if __name__ == "__main__":
    main()
