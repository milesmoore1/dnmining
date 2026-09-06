"""Verify the geoscience slide-over panels in miles_atlas_3d.html."""
import functools, http.server, socketserver, threading, time
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
PORT = 8746


def serve():
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(HERE))
    httpd = socketserver.TCPServer(("127.0.0.1", PORT), h)
    httpd.daemon_threads = True
    threading.Thread(target=httpd.serve_forever, daemon=True).start()


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
            pg.wait_for_function("window.__ready===true && window.GEO!==null", timeout=25000)
        except Exception:
            problems.append("not ready / geochem not loaded")
        time.sleep(2)

        # pick a Central-Appalachian sample whose Dy is below detection (sawtooth-relevant)
        sid = pg.evaluate("""() => {
            const s=DATA.find(x=>GEO[String(x.id)] && GEO[String(x.id)].el.Dy && GEO[String(x.id)].el.Dy.L
                                  && x.basin==='CENTRAL APPALACHIAN') ||
                    DATA.find(x=>GEO[String(x.id)] && GEO[String(x.id)].el.Dy && GEO[String(x.id)].el.Dy.L);
            return s?String(s.id):null; }""")
        notes.append(f"test sample: {sid}")
        if not sid:
            problems.append("no censored-Dy sample found")
        pg.evaluate("(id)=>openGeo(id)", sid); time.sleep(1.2)

        shown = pg.eval_on_selector("#geo", "e=>e.classList.contains('show')")
        if not shown: problems.append("geo slide-over did not open")

        # Panel 1 spider
        spider_svgs = pg.eval_on_selector_all("#p_spider svg", "e=>e.length")
        face_d = pg.eval_on_selector_all("#p_spider path[stroke='#c0392b']", "e=>e.map(p=>p.getAttribute('d'))")
        dl2_d = pg.eval_on_selector_all("#p_spider path[stroke='#2a6fb0']", "e=>e.map(p=>p.getAttribute('d'))")
        open_syms = pg.eval_on_selector_all("#p_spider circle[fill='#fff']", "e=>e.length")
        cens_labels = pg.eval_on_selector_all("#p_spider text.c", "e=>e.filter(t=>/\\d+%/.test(t.textContent)).length")
        notes.append(f"spider svgs={spider_svgs} faceLine={len(face_d)} dl2Line={len(dl2_d)} openSymbols={open_syms} censLabels={cens_labels}")
        if spider_svgs == 0: problems.append("spider not rendered")
        if not face_d or not dl2_d: problems.append("spider missing face or dl2 line")
        elif face_d[0] == dl2_d[0]: problems.append("FACE and DL/2 spider lines identical (no visible difference)")
        if open_syms == 0: problems.append("no open (below-detection) symbols on spider")
        if cens_labels < 5: problems.append(f"per-element censoring labels missing ({cens_labels})")

        # Panel 2 indices for both treatments
        idx = pg.evaluate("""() => {
            const rows=[...document.querySelectorAll('#p_indices tbody tr')];
            const pick=(name)=>{const r=rows.find(r=>r.children[0].textContent.includes(name));
                return r?{face:r.children[1].textContent.trim(),dl2:r.children[2].textContent.trim()}:null;};
            return {n:rows.length, eu:pick('Eu/Eu'), ce:pick('Ce/Ce'), layb:pick('La/Yb'), tree:pick('REE')};
        }""")
        notes.append(f"indices rows={idx['n']} Eu/Eu*={idx['eu']} (La/Yb)N={idx['layb']}")
        num = lambda t: t not in (None, "", "—", "n/a") and any(c.isdigit() for c in t)
        for key in ("eu", "ce", "layb", "tree"):
            o = idx[key]
            if not o or not num(o["face"]) or not num(o["dl2"]):
                problems.append(f"index {key} not computed for both FACE and DL/2: {o}")

        # Panel 3 context (ternary + bivariates) and Panel 4 population
        ctx_svgs = pg.eval_on_selector_all("#p_context svg", "e=>e.length")
        pop_svgs = pg.eval_on_selector_all("#p_pop svg", "e=>e.length")
        notes.append(f"context svgs={ctx_svgs} (expect 4: ternary+3 scatter), pop svgs={pop_svgs}")
        if ctx_svgs < 4: problems.append(f"provenance context panels incomplete ({ctx_svgs})")
        if pop_svgs < 1: problems.append("population panel not rendered")

        # screenshots — spider panel is the priority image
        pg.locator("#p_spider").scroll_into_view_if_needed()
        pg.locator("#p_spider").screenshot(path=str(HERE / "geo_spider.png"))
        pg.locator(".gp.wide").first.screenshot(path=str(HERE / "geo_spider_panel.png"))
        pg.locator("#geo").screenshot(path=str(HERE / "geo_full.png"))

        notes.append(f"console errors: {len(cerr)} | page errors: {len(perr)}")
        if cerr: problems.append("console errors: " + " || ".join(cerr[:6]))
        if perr: problems.append("page errors: " + " || ".join(perr[:6]))
        br.close()

    print("\n=== NOTES ==="); [print("  -", n) for n in notes]
    print("\n=== RESULT ===")
    if problems:
        print("FAIL:"); [print("  ✗", x) for x in problems]; raise SystemExit(1)
    print("PASS — all checks green")
    for f in ["geo_spider.png", "geo_spider_panel.png", "geo_full.png"]:
        print("  screenshot:", f)


if __name__ == "__main__":
    main()
