"""Verify the separation-index layer + panel in miles_atlas_v2.html."""
import functools, http.server, socketserver, threading, time
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent; PORT=8752
def serve():
    h=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(HERE))
    s=socketserver.TCPServer(("127.0.0.1",PORT),h); s.daemon_threads=True
    threading.Thread(target=s.serve_forever,daemon=True).start()

def main():
    serve(); time.sleep(0.6); problems,notes=[],[]
    with sync_playwright() as p:
        br=p.chromium.launch(args=["--use-gl=swiftshader","--ignore-gpu-blocklist"])
        pg=br.new_page(viewport={"width":1500,"height":950})
        cerr,perr=[],[]
        pg.on("console",lambda m:cerr.append(m.text) if m.type=="error" else None)
        pg.on("pageerror",lambda e:perr.append(str(e)))
        pg.goto(f"http://127.0.0.1:{PORT}/miles_atlas_v2.html",wait_until="networkidle")
        try: pg.wait_for_function("window.__ready===true",timeout=25000)
        except Exception: problems.append("not ready")
        time.sleep(5)

        # sepindex loaded + attached
        att=pg.evaluate("() => ({withIdx:DATA.filter(d=>d.sepidx!=null).length, hiCmf:DATA.filter(d=>d.cmf>0.5).length})")
        notes.append(f"samples w/ sepidx={att['withIdx']} cmf>0.5={att['hiCmf']}")
        if att["withIdx"]<4000: problems.append("sepindex not loaded/attached")
        if att["hiCmf"]<100: problems.append("no high-imputation samples for censoring markers")

        pg.screenshot(path=str(HERE/"_phigh.png")); phigh=(HERE/"_phigh.png").read_bytes()

        # switch to SEPARATION INDEX
        pg.click("#modeseg button[data-mode='sepindex']"); time.sleep(2.5)
        leg=pg.eval_on_selector("#leglbl","e=>e.textContent")
        legsub=pg.eval_on_selector("#legsub","e=>e.textContent")
        notes.append(f"legend after switch: {leg!r}")
        if "separation index" not in leg.lower(): problems.append("legend did not switch to sep index")
        if "imputed" not in legsub.lower(): problems.append("censoring caveat not in legend")
        act=pg.evaluate("() => window.__activeLayerIds||[]")
        if "hex" not in act: problems.append("no hex layer in sep-index mode")
        pg.screenshot(path=str(HERE/"sepindex_national.png")); sep=(HERE/"sepindex_national.png").read_bytes()
        if sep==phigh: problems.append("map did not recolor on mode switch")
        else: notes.append(f"recolor confirmed (phigh {len(phigh)}B vs sepindex {len(sep)}B)")

        # info tooltip text present
        info=pg.eval_on_selector("#modeinfo","e=>e.title")
        if "feed-composition" not in (info or "").lower(): problems.append("mode info tooltip missing label")

        # open a full-suite sample -> sep-index panel next to spidergram
        sid=pg.evaluate("""() => { const s=DATA.find(x=>x.sepidx!=null && x.cmf>0.5)||DATA.find(x=>x.sepidx!=null); openDetail(s); return String(s.id); }""")
        time.sleep(1.2)
        spider=pg.eval_on_selector_all("#p_spider svg","e=>e.length")
        sepsvg=pg.eval_on_selector_all("#p_sepindex svg","e=>e.length")
        barcnt=pg.eval_on_selector_all("#p_sepindex rect","e=>e.length")
        sepcap=pg.eval_on_selector("#sepcap","e=>e.textContent")
        notes.append(f"detail: spider={spider} sepSvg={sepsvg} bars={barcnt} cap~{sepcap[:60]!r}")
        if spider==0 or sepsvg==0 or barcnt==0: problems.append("sep-index panel/bars not rendered")
        if "imputed" not in (sepcap or "").lower(): problems.append("censored fraction not shown in panel")
        pg.screenshot(path=str(HERE/"sepindex_panel.png"))
        pg.keyboard.press("Escape"); time.sleep(0.4)

        # basin distribution draws
        pg.evaluate("""() => { const s=document.querySelector('#basinsel'); s.value='UINTA'; s.dispatchEvent(new Event('change',{bubbles:true})); }""")
        time.sleep(2.5)
        viol=pg.eval_on_selector_all("#basinviol svg","e=>e.length")
        notes.append(f"basin violin svg={viol}")
        if viol==0: problems.append("basin distribution not drawn")

        notes.append(f"console errors: {len(cerr)} | page errors: {len(perr)}")
        if cerr: problems.append("console: "+" || ".join(cerr[:6]))
        if perr: problems.append("page: "+" || ".join(perr[:6]))
        br.close()
    (HERE/"_phigh.png").unlink(missing_ok=True)
    print("\n=== NOTES ==="); [print("  -",n) for n in notes]
    print("\n=== RESULT ===")
    if problems: print("FAIL:"); [print("  ✗",x) for x in problems]; raise SystemExit(1)
    print("PASS — all checks green")
    for f in ["sepindex_national.png","sepindex_panel.png"]: print("  screenshot:",f)

if __name__=="__main__": main()
