"""Verify the v2 visual overhaul: imagery default, detail takeover, arrows, panels."""
import functools, http.server, socketserver, threading, time
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
PORT = 8750


def serve():
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(HERE))
    httpd = socketserver.TCPServer(("127.0.0.1", PORT), h)
    httpd.daemon_threads = True
    threading.Thread(target=httpd.serve_forever, daemon=True).start()


def main():
    serve(); time.sleep(0.6)
    problems, notes = [], []
    img = {"n": 0}
    with sync_playwright() as p:
        br = p.chromium.launch(args=["--use-gl=swiftshader", "--ignore-gpu-blocklist"])
        pg = br.new_page(viewport={"width": 1500, "height": 950})
        cerr, perr = [], []
        pg.on("console", lambda m: cerr.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e: perr.append(str(e)))
        pg.on("response", lambda r: img.__setitem__("n", img["n"]+1) if ("World_Imagery" in r.url and r.status == 200) else None)
        pg.goto(f"http://127.0.0.1:{PORT}/miles_atlas_v2.html", wait_until="networkidle")
        try:
            pg.wait_for_function("window.__ready===true", timeout=25000)
        except Exception:
            problems.append("not ready")
        time.sleep(5)

        applied = pg.evaluate("() => window.__appliedBasemap")
        notes.append(f"default basemap: {applied}; World_Imagery tiles(200): {img['n']}")
        if applied != "imagery-labels": problems.append(f"default basemap not satellite: {applied}")
        if img["n"] == 0: problems.append("no imagery tiles painted at national")

        act = pg.evaluate("() => window.__activeLayerIds||[]")
        notes.append(f"@national layers: {act}")
        mi = act.index("mines") if "mines" in act else -1
        hi = min([act.index(x) for x in ("hex","pts") if x in act] or [99])
        if not("hex" in act and "mines" in act and mi < hi):
            problems.append(f"layer order wrong (mines under samples expected): {act}")
        elev = pg.evaluate("() => window.__elevDomain||null")
        notes.append(f"hex elevation domain: {elev}")
        if not elev or not(elev[1] > elev[0]): problems.append("hex elevation flat")

        pg.screenshot(path=str(HERE / "v2_national.png"))

        # gear toggles chrome
        pg.click("#gear"); time.sleep(0.5)
        hid = pg.eval_on_selector("#ctrls", "e=>e.classList.contains('min')")
        pg.click("#gear"); time.sleep(0.3)
        if not hid: problems.append("gear did not hide controls")

        # regional
        pg.evaluate("() => window.__map.easeTo({center:[-82.5,37.5],zoom:7,pitch:55,duration:600})")
        time.sleep(2.5); pg.screenshot(path=str(HERE / "v2_regional.png"))

        # open detail (same path the map onClick uses)
        sid = pg.evaluate("""() => { const s=DATA.find(x=>GEO[String(x.id)]&&GEO[String(x.id)].el.Dy&&GEO[String(x.id)].el.Dy.L&&x.basin==='CENTRAL APPALACHIAN')||DATA[0];
            openDetail(s); return String(s.id); }""")
        time.sleep(1.2)
        shown = pg.eval_on_selector("#detail", "e=>e.classList.contains('show')")
        dhid = pg.eval_on_selector("#dh_id", "e=>e.textContent")
        spider = pg.eval_on_selector_all("#p_spider svg", "e=>e.length")
        idxrows = pg.eval_on_selector_all("#p_indices tbody tr", "e=>e.length")
        ctx = pg.eval_on_selector_all("#p_context svg", "e=>e.length")
        pop = pg.eval_on_selector_all("#p_pop svg", "e=>e.length")
        panel = pg.eval_on_selector("#panel", "e=>e.textContent.length")
        notes.append(f"detail: shown={shown} id={dhid} spider={spider} idxRows={idxrows} ctx={ctx} pop={pop} panelChars={panel}")
        if not shown: problems.append("detail did not open")
        if spider == 0 or idxrows == 0 or ctx < 4 or pop == 0: problems.append("geoscience panels incomplete in detail")
        if not panel or panel < 50: problems.append("right-column model panel empty")
        # spider width (hero) should be large
        sw = pg.eval_on_selector("#p_spider svg", "e=>e.getAttribute('width')")
        notes.append(f"spider svg width: {sw}")
        if sw and int(float(sw)) < 480: problems.append(f"spider not hero-sized ({sw})")
        pg.screenshot(path=str(HERE / "v2_detail.png"))

        # arrow-key nav changes the sample
        pg.keyboard.press("ArrowRight"); time.sleep(1.0)
        dhid2 = pg.eval_on_selector("#dh_id", "e=>e.textContent")
        notes.append(f"arrow nav: {dhid} -> {dhid2}")
        if dhid2 == dhid: problems.append("arrow-key navigation did not change sample")

        # Esc closes
        pg.keyboard.press("Escape"); time.sleep(0.6)
        if pg.eval_on_selector("#detail", "e=>e.classList.contains('show')"):
            problems.append("Esc did not close detail")

        notes.append(f"console errors: {len(cerr)} | page errors: {len(perr)}")
        if cerr: problems.append("console errors: " + " || ".join(cerr[:6]))
        if perr: problems.append("page errors: " + " || ".join(perr[:6]))
        br.close()

    print("\n=== NOTES ==="); [print("  -", n) for n in notes]
    print("\n=== RESULT ===")
    if problems:
        print("FAIL:"); [print("  ✗", x) for x in problems]; raise SystemExit(1)
    print("PASS — all checks green")
    for f in ["v2_national.png", "v2_regional.png", "v2_detail.png"]:
        print("  screenshot:", f)


if __name__ == "__main__":
    main()
