"""Real-browser verification of miles_atlas_3d.html (deck.gl + MapLibre + terrain)."""
import functools, http.server, socketserver, threading, time
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
PORT = 8744


def serve():
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(HERE))
    httpd = socketserver.TCPServer(("127.0.0.1", PORT), h)
    httpd.daemon_threads = True
    threading.Thread(target=httpd.serve_forever, daemon=True).start()


def main():
    serve(); time.sleep(0.6)
    problems, notes = [], []
    cnt = {"dem": 0, "img": 0, "gray": 0}
    def on_resp(r):
        if r.status == 200:
            if "elevation-tiles-prod/terrarium" in r.url: cnt["dem"] += 1
            elif "World_Imagery" in r.url: cnt["img"] += 1
            elif "World_Light_Gray_Base" in r.url: cnt["gray"] += 1
    with sync_playwright() as p:
        br = p.chromium.launch(args=["--use-gl=swiftshader", "--ignore-gpu-blocklist"])
        pg = br.new_page(viewport={"width": 1400, "height": 900})
        cerr, perr = [], []
        pg.on("console", lambda m: cerr.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e: perr.append(str(e)))
        pg.on("response", on_resp)

        pg.goto(f"http://127.0.0.1:{PORT}/miles_atlas_3d.html", wait_until="networkidle")
        try:
            pg.wait_for_function("window.__ready===true", timeout=20000)
        except Exception:
            problems.append("window.__ready never true")
        time.sleep(6)

        canv = pg.eval_on_selector_all("#map canvas", "els=>els.map(c=>({w:c.width,h:c.height}))")
        notes.append(f"canvases: {canv}")
        if not any(c["w"] > 0 and c["h"] > 0 for c in canv):
            problems.append("no non-zero canvas")

        terr = pg.evaluate("() => { const t=window.__map.getTerrain(); return t?{source:t.source,exaggeration:t.exaggeration}:null; }")
        notes.append(f"map.getTerrain(): {terr}")
        if not terr:
            problems.append("terrain not applied (getTerrain null)")
        notes.append(f"DEM tiles (200): {cnt['dem']}")
        if cnt["dem"] == 0:
            problems.append("no DEM/terrarium tiles loaded")

        elev = pg.evaluate("() => window.__elevDomain || null")
        notes.append(f"hex elevation domain: {elev}")
        if not elev or not (elev[1] > elev[0]):
            problems.append(f"elevation range degenerate: {elev}")

        active = pg.evaluate("() => window.__activeLayerIds || []")
        notes.append(f"active layers @national: {active}")
        if "hex" not in active:
            problems.append("hex layer not active at national zoom")

        # national terrain screenshot
        pg.screenshot(path=str(HERE / "miles3d_terrain_national.png"))
        terr_shot = (HERE / "miles3d_terrain_national.png").read_bytes()

        # hover tooltip
        hovered = False
        for lon, lat in [(-81.6, 37.4), (-82.0, 37.8), (-80.8, 38.2)]:
            xy = pg.evaluate("([lo,la]) => { const p=window.__map.project([lo,la]); return [p.x,p.y]; }", [lon, lat])
            pg.mouse.move(xy[0], xy[1]); time.sleep(0.5)
            txt = pg.evaluate("""() => { const els=[...document.querySelectorAll('#map div')];
                const t=els.find(e=>/mean P\\(high\\)|P\\(high\\)/.test(e.textContent||'')); return t?t.textContent:null; }""")
            if txt: hovered = True; notes.append(f"tooltip: {txt[:50]!r}"); break
        if not hovered:
            problems.append("hover tooltip never fired")

        # click opens panel (hex)
        s = pg.evaluate("() => { const s=DATA.find(x=>x.basin==='CENTRAL APPALACHIAN')||DATA[0]; return [s.lon,s.lat]; }")
        xy = pg.evaluate("([lo,la]) => { const p=window.__map.project([lo,la]); return [p.x,p.y]; }", s)
        pg.mouse.click(xy[0], xy[1]); time.sleep(0.5)
        big = pg.eval_on_selector("#panel .hd .big", "e=>e?e.textContent:null")
        notes.append(f"panel after click: {big}")
        if not big or "%" not in big:
            problems.append("click did not open panel")

        # basemap switcher: Imagery
        pg.click("#bmseg button[data-m='imagery']"); time.sleep(4)
        applied = pg.evaluate("() => window.__appliedBasemap")
        notes.append(f"after Imagery click, applied={applied}, imagery tiles(200)={cnt['img']}")
        if applied != "imagery":
            problems.append(f"basemap switch to imagery failed (applied={applied})")
        if cnt["img"] == 0:
            problems.append("no World_Imagery tiles loaded")
        pg.screenshot(path=str(HERE / "_img_full.png"))
        img_shot = (HERE / "_img_full.png").read_bytes()
        if img_shot == terr_shot:
            problems.append("imagery view identical to terrain view (basemap did not repaint)")
        else:
            notes.append(f"imagery vs terrain screenshots differ ({len(terr_shot)} vs {len(img_shot)} bytes) -> basemap repainted")

        # Imagery + labels
        pg.click("#bmseg button[data-m='imagery-labels']"); time.sleep(2)
        applied = pg.evaluate("() => window.__appliedBasemap")
        notes.append(f"after Imagery+labels click, applied={applied}")
        if applied != "imagery-labels":
            problems.append(f"basemap switch to imagery-labels failed (applied={applied})")

        # back to terrain
        pg.click("#bmseg button[data-m='terrain']"); time.sleep(1.5)
        if pg.evaluate("() => window.__appliedBasemap") != "terrain":
            problems.append("basemap switch back to terrain failed")

        # southern WV hexes over terrain (grounding eyeball) at zoom 6
        pg.evaluate("() => window.__map.easeTo({center:[-81.6,37.7],zoom:6,pitch:60,bearing:-20,duration:800})")
        time.sleep(2.5)
        pg.screenshot(path=str(HERE / "miles3d_terrain_wv_hex.png"))

        # zoom transition to points + auto-imagery at close zoom
        pg.evaluate("() => window.__map.easeTo({center:[-81.6,37.7],zoom:11,pitch:60,duration:900})")
        time.sleep(4)
        active2 = pg.evaluate("() => window.__activeLayerIds || []")
        applied2 = pg.evaluate("() => window.__appliedBasemap")
        notes.append(f"@zoom11: active={active2}, auto-applied basemap={applied2}, imgTiles={cnt['img']}")
        if "pts" not in active2:
            problems.append(f"points not active at zoom 11: {active2}")
        if applied2 != "imagery-labels":
            problems.append(f"auto-imagery did not engage at zoom>=10 (applied={applied2})")
        pg.evaluate("() => { const s=DATA.find(x=>x.basin==='CENTRAL APPALACHIAN'&&x.p_high>0.7)||DATA[0]; selectSample(s); }")
        time.sleep(0.5)
        pg.screenshot(path=str(HERE / "miles3d_imagery_closeup.png"))
        pg.locator("#side").screenshot(path=str(HERE / "miles3d_terrain_panel.png"))

        notes.append(f"console errors: {len(cerr)} | page errors: {len(perr)}")
        if cerr: problems.append("console errors: " + " || ".join(cerr[:5]))
        if perr: problems.append("page errors: " + " || ".join(perr[:5]))
        br.close()

    (HERE / "_img_full.png").unlink(missing_ok=True)
    print("\n=== NOTES ==="); [print("  -", n) for n in notes]
    print("\n=== RESULT ===")
    if problems:
        print("FAIL:"); [print("  ✗", x) for x in problems]; raise SystemExit(1)
    print("PASS — all checks green")
    for f in ["miles3d_terrain_national.png", "miles3d_terrain_wv_hex.png",
              "miles3d_imagery_closeup.png", "miles3d_terrain_panel.png"]:
        print("  screenshot:", f)


if __name__ == "__main__":
    main()
