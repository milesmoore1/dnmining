import { useEffect, useRef } from "react";
import maplibregl, { type GeoJSONSource, type Map as MapLibreMap } from "maplibre-gl";
import { EMPTY_COLLECTION, sampleFeature, samplesCollection } from "./geo";
import type { MineStatus, Sample, ViewBy } from "./types";

type AtlasMapProps = {
  samples: Sample[];
  allSamplesById: globalThis.Map<string, Sample>;
  selected: Sample | null;
  viewBy: ViewBy;
  mineStatusById: Map<string, MineStatus>;
  onSelect: (sample: Sample) => void;
};

// Satellite stays primary: it is the useful visual anchor for sample context.
// Reference labels remain a separate raster layer so they never wash out the imagery.
const mapStyle = {
  version: 8,
  glyphs: "https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf",
  sources: {
    imagery: { type: "raster", tileSize: 256, attribution: "Esri World Imagery", tiles: ["https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"] },
    reference: { type: "raster", tileSize: 256, attribution: "Esri", tiles: ["https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}"] },
  },
  layers: [
    { id: "satellite", type: "raster", source: "imagery", paint: { "raster-saturation": -0.16, "raster-contrast": 0.07, "raster-brightness-min": 0.06, "raster-brightness-max": 0.88 } },
    { id: "place-reference", type: "raster", source: "reference", paint: { "raster-opacity": 0.74 } },
  ],
};

const STATE_BOUNDARIES = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/State_County/MapServer/0/query?where=1%3D1&outFields=NAME&returnGeometry=true&outSR=4326&maxAllowableOffset=0.02&f=geojson";
const COUNTY_BOUNDARIES = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/State_County/MapServer/1/query";

type MarkerVariant = "prospect-high" | "prospect-low" | "mine-current" | "mine-abandoned";

const MARKER_VARIANTS: MarkerVariant[] = ["prospect-high", "prospect-low", "mine-current", "mine-abandoned"];

const markerStyles: Record<MarkerVariant, { fill: string; diamond?: boolean }> = {
  "prospect-high": { fill: "#6EF0B1", diamond: true },
  "prospect-low": { fill: "#FF776B" },
  "mine-current": { fill: "#F5EFC9", diamond: true },
  "mine-abandoned": { fill: "#A896D6" },
};

function markerFor(sample: Sample, viewBy: ViewBy, mineStatus: MineStatus): MarkerVariant {
  if (viewBy === "prospectivity") return sample.pred === "high" ? "prospect-high" : "prospect-low";
  return mineStatus === "abandoned" ? "mine-abandoned" : "mine-current";
}

function siteCollection(samples: Sample[], viewBy: ViewBy, mineStatusById: Map<string, MineStatus>) {
  return {
    type: "FeatureCollection" as const,
    features: samples.map((sample) => {
      const feature = sampleFeature(sample);
      const mineStatus = mineStatusById.get(sample.id) ?? "none";
      return { ...feature, properties: { ...feature.properties, marker: markerFor(sample, viewBy, mineStatus), mineStatus } };
    }),
  };
}

function markerImage(variant: MarkerVariant) {
  const canvas = document.createElement("canvas");
  canvas.width = canvas.height = 32;
  const context = canvas.getContext("2d")!;
  const style = markerStyles[variant];

  context.translate(16, 16);
  context.fillStyle = style.fill;
  context.beginPath();
  if (style.diamond) {
    context.moveTo(0, -6.5); context.lineTo(6.5, 0); context.lineTo(0, 6.5); context.lineTo(-6.5, 0); context.closePath();
  } else {
    context.roundRect(-5.4, -5.4, 10.8, 10.8, 1.2);
  }
  context.fill();
  return context.getImageData(0, 0, 32, 32);
}

function selectionImage() {
  const canvas = document.createElement("canvas");
  canvas.width = canvas.height = 32;
  const context = canvas.getContext("2d")!;
  context.strokeStyle = "#F5EFC9";
  context.lineWidth = 2;
  const corners: Array<[number, number, number, number, number, number]> = [
    [4, 11, 4, 4, 11, 4], [21, 4, 28, 4, 28, 11], [4, 21, 4, 28, 11, 28], [21, 28, 28, 28, 28, 21],
  ];
  corners.forEach(([x1, y1, x2, y2, x3, y3]) => { context.beginPath(); context.moveTo(x1, y1); context.lineTo(x2, y2); context.lineTo(x3, y3); context.stroke(); });
  return context.getImageData(0, 0, 32, 32);
}

function setData(map: MapLibreMap, sourceId: string, data: unknown) {
  (map.getSource(sourceId) as GeoJSONSource | undefined)?.setData(data as never);
}

function escapeHtml(value: string | null | undefined) {
  return (value ?? "Not reported").replace(/[&<>'"]/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[character]!);
}

export default function AtlasMap({ samples, allSamplesById, selected, viewBy, mineStatusById, onSelect }: AtlasMapProps) {
  const mapNode = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MapLibreMap | null>(null);
  const samplesRef = useRef(samples);
  const byIdRef = useRef(allSamplesById);
  const onSelectRef = useRef(onSelect);
  const viewByRef = useRef(viewBy);
  const mineStatusRef = useRef(mineStatusById);

  samplesRef.current = samples;
  byIdRef.current = allSamplesById;
  onSelectRef.current = onSelect;
  viewByRef.current = viewBy;
  mineStatusRef.current = mineStatusById;

  useEffect(() => {
    if (!mapNode.current || mapRef.current) return;
    const map = new maplibregl.Map({
      container: mapNode.current,
      style: mapStyle as never,
      center: [-96.5, 38.5],
      zoom: 3.45,
      minZoom: 2.5,
      maxZoom: 15,
      fadeDuration: 0,
      attributionControl: { compact: true },
    });
    mapRef.current = map;
    // Defaults are deliberately conservative. These rates preserve the native
    // inertial feel while making both trackpad and wheel travel much more direct.
    map.scrollZoom.setZoomRate(1 / 38);
    map.scrollZoom.setWheelZoomRate(1 / 260);
    map.touchZoomRotate.setZoomRate(1.2);
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "bottom-right");

    map.on("load", () => {
      MARKER_VARIANTS.forEach((variant) => map.addImage(`marker-${variant}`, markerImage(variant)));
      map.addImage("marker-selected", selectionImage());
      map.addSource("sites", {
        type: "geojson",
        data: siteCollection(samplesRef.current, viewByRef.current, mineStatusRef.current),
      });
      map.addSource("states", { type: "geojson", data: STATE_BOUNDARIES, attribution: "U.S. Census Bureau TIGERweb" });
      map.addSource("counties", { type: "geojson", data: EMPTY_COLLECTION as never, attribution: "U.S. Census Bureau TIGERweb" });
      map.addSource("selected-site", { type: "geojson", data: EMPTY_COLLECTION as never });

      map.addLayer({
        id: "state-boundaries",
        type: "line",
        source: "states",
        paint: { "line-color": "#F5EFC9", "line-width": 1.2, "line-opacity": 0.78 },
      });
      map.addLayer({
        id: "county-boundaries",
        type: "line",
        source: "counties",
        minzoom: 5,
        paint: { "line-color": "#E8EEE8", "line-width": 0.7, "line-opacity": 0.64 },
      });
      map.addLayer({
        id: "site-symbols",
        type: "symbol",
        source: "sites",
        layout: {
          "icon-image": ["concat", "marker-", ["get", "marker"]] as never,
          "icon-size": ["interpolate", ["linear"], ["zoom"], 3, 0.52, 7, 0.66, 12, 0.9],
          "icon-allow-overlap": true,
          "icon-ignore-placement": true,
        },
      });
      map.addLayer({
        id: "selected-site-brackets",
        type: "symbol",
        source: "selected-site",
        layout: { "icon-image": "marker-selected", "icon-size": ["interpolate", ["linear"], ["zoom"], 4, 0.75, 9, 1, 12, 1.25], "icon-allow-overlap": true },
      });

      const selectSite = (event: maplibregl.MapLayerMouseEvent) => {
        const id = event.features?.[0]?.properties?.id as string | undefined;
        const sample = id ? byIdRef.current.get(id) : undefined;
        if (sample) onSelectRef.current(sample);
      };
      map.on("click", "site-symbols", selectSite);
      const hoverPopup = new maplibregl.Popup({ closeButton: false, closeOnClick: false, offset: 12, className: "site-popup" });
      map.getCanvas().style.cursor = "crosshair";
      map.on("mousemove", "site-symbols", (event) => {
        const id = event.features?.[0]?.properties?.id as string | undefined;
        const sample = id ? byIdRef.current.get(id) : undefined;
        if (!sample) return;
        const mineStatus = mineStatusRef.current.get(sample.id) ?? "none";
        const mineLabel = mineStatus === "current" ? "Current coal mine at site" : mineStatus === "abandoned" ? "Abandoned coal mine at site" : "No coal mine at site";
        hoverPopup
          .setLngLat(event.lngLat)
          .setHTML(`<div class="site-popup__id">${escapeHtml(sample.id)}</div><div class="site-popup__place">${escapeHtml([sample.county, sample.state].filter(Boolean).join(", "))}</div><div class="site-popup__metrics"><b>${Math.round(sample.p_high * 100)}%</b> P(high) <span>${sample.split === "test" ? "Test" : "Training"}</span></div><div class="site-popup__mine">${mineLabel}</div>`)
          .addTo(map);
      });
      map.on("mouseleave", "site-symbols", () => {
        hoverPopup.remove();
        map.getCanvas().style.cursor = "crosshair";
      });

      // County polygons are loaded only for the active viewport after zoom 5.
      // This gives crisp Census boundaries without making national navigation carry
      // the entire county geometry for the country.
      let lastCountyView = "";
      let countyAbort: AbortController | null = null;
      const loadVisibleCounties = () => {
        if (map.getZoom() < 5) {
          setData(map, "counties", EMPTY_COLLECTION);
          lastCountyView = "";
          return;
        }
        const bounds = map.getBounds();
        const key = [bounds.getWest(), bounds.getSouth(), bounds.getEast(), bounds.getNorth()].map((value) => value.toFixed(1)).join(",");
        if (key === lastCountyView) return;
        lastCountyView = key;
        countyAbort?.abort();
        countyAbort = new AbortController();
        const params = new URLSearchParams({
          where: "1=1",
          outFields: "NAME",
          returnGeometry: "true",
          outSR: "4326",
          geometryType: "esriGeometryEnvelope",
          geometry: `${bounds.getWest()},${bounds.getSouth()},${bounds.getEast()},${bounds.getNorth()}`,
          spatialRel: "esriSpatialRelIntersects",
          maxAllowableOffset: "0.003",
          f: "geojson",
        });
        fetch(`${COUNTY_BOUNDARIES}?${params.toString()}`, { signal: countyAbort.signal })
          .then((response) => response.ok ? response.json() : Promise.reject(new Error("County boundaries unavailable")))
          .then((features) => { if (key === lastCountyView) setData(map, "counties", features); })
          .catch((reason: unknown) => { if (!(reason instanceof DOMException && reason.name === "AbortError")) console.warn(reason); });
      };
      map.on("moveend", loadVisibleCounties);
      loadVisibleCounties();
    });

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map?.isStyleLoaded()) return;
    setData(map, "sites", siteCollection(samples, viewBy, mineStatusById));
  }, [samples, viewBy, mineStatusById]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map?.isStyleLoaded()) return;
    if (!selected) {
      setData(map, "selected-site", EMPTY_COLLECTION);
      return;
    }
    setData(map, "selected-site", samplesCollection([selected]));
    map.easeTo({ center: [selected.lon, selected.lat], zoom: Math.max(map.getZoom(), 9.7), duration: 700, essential: true });
  }, [selected]);

  return <div className="map" ref={mapNode} aria-label="Interactive map of assessed REE coal samples" />;
}
