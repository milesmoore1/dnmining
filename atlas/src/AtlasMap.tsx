import { useEffect, useRef } from "react";
import maplibregl, { type GeoJSONSource, type Map as MapLibreMap } from "maplibre-gl";
import { EMPTY_COLLECTION, coalFieldForSample, samplesCollection } from "./geo";
import type { GeoCollection, Prediction, Sample, Split } from "./types";

type AtlasMapProps = {
  samples: Sample[];
  allSamplesById: globalThis.Map<string, Sample>;
  coalFields: GeoCollection | null;
  selected: Sample | null;
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

type MarkerVariant = "high-train" | "high-test" | "low-train" | "low-test";

function markerImage(variant: MarkerVariant) {
  const canvas = document.createElement("canvas");
  canvas.width = canvas.height = 28;
  const context = canvas.getContext("2d")!;
  const [prediction] = variant.split("-") as [Prediction, Split];
  const fill = prediction === "high" ? "#6EF0B1" : "#FF776B";

  context.translate(14, 14);
  context.rotate(prediction === "high" ? Math.PI / 4 : 0);
  // The two shapes are intentionally simple field symbols: a diamond for a
  // higher class, a square for a lower class. They stay legible over imagery.
  context.fillStyle = "rgba(0,0,0,.42)";
  context.fillRect(-5, -3, 10, 10);
  context.fillStyle = fill;
  context.fillRect(-4, -4, 8, 8);
  context.lineWidth = 1.2;
  context.strokeStyle = "#0B1720";
  context.strokeRect(-4, -4, 8, 8);
  return context.getImageData(0, 0, 28, 28);
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

export default function AtlasMap({ samples, allSamplesById, coalFields, selected, onSelect }: AtlasMapProps) {
  const mapNode = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MapLibreMap | null>(null);
  const samplesRef = useRef(samples);
  const byIdRef = useRef(allSamplesById);
  const onSelectRef = useRef(onSelect);
  const fieldsRef = useRef(coalFields);

  samplesRef.current = samples;
  byIdRef.current = allSamplesById;
  onSelectRef.current = onSelect;
  fieldsRef.current = coalFields;

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
      (Object.keys({ "high-train": 1, "high-test": 1, "low-train": 1, "low-test": 1 }) as MarkerVariant[]).forEach((variant) => map.addImage(`marker-${variant}`, markerImage(variant)));
      map.addImage("marker-selected", selectionImage());
      map.addSource("sites", {
        type: "geojson",
        data: samplesCollection(samplesRef.current),
      });
      map.addSource("states", { type: "geojson", data: STATE_BOUNDARIES, attribution: "U.S. Census Bureau TIGERweb" });
      map.addSource("counties", { type: "geojson", data: EMPTY_COLLECTION as never, attribution: "U.S. Census Bureau TIGERweb" });
      map.addSource("selected-site", { type: "geojson", data: EMPTY_COLLECTION as never });
      map.addSource("selected-coal-field", { type: "geojson", data: EMPTY_COLLECTION as never });

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

      (Object.keys({ "high-train": 1, "high-test": 1, "low-train": 1, "low-test": 1 }) as MarkerVariant[]).forEach((variant) => {
        const [prediction, split] = variant.split("-");
        map.addLayer({
          id: `site-${variant}`,
          type: "symbol",
          source: "sites",
          filter: ["all", ["==", ["get", "pred"], prediction], ["==", ["get", "split"], split]],
          layout: { "icon-image": `marker-${variant}`, "icon-size": ["interpolate", ["linear"], ["zoom"], 4, 0.62, 8, 0.8, 12, 1], "icon-allow-overlap": true },
        });
      });
      map.addLayer({
        id: "selected-coal-fill",
        type: "fill",
        source: "selected-coal-field",
        paint: { "fill-color": "#8AC2D4", "fill-opacity": 0.16 },
      });
      map.addLayer({
        id: "selected-coal-line",
        type: "line",
        source: "selected-coal-field",
        paint: { "line-color": "#F5EFC9", "line-width": 2, "line-opacity": 0.92 },
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
      const siteLayers = ["site-high-train", "site-high-test", "site-low-train", "site-low-test"];
      siteLayers.forEach((layer) => map.on("click", layer, selectSite));
      siteLayers.forEach((layer) => {
        map.on("mouseenter", layer, () => (map.getCanvas().style.cursor = "pointer"));
        map.on("mouseleave", layer, () => (map.getCanvas().style.cursor = ""));
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
    setData(map, "sites", samplesCollection(samples));
  }, [samples]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map?.isStyleLoaded()) return;
    if (!selected) {
      setData(map, "selected-site", EMPTY_COLLECTION);
      setData(map, "selected-coal-field", EMPTY_COLLECTION);
      return;
    }
    setData(map, "selected-site", samplesCollection([selected]));
    const coalField = coalFieldForSample(selected, coalFields);
    setData(map, "selected-coal-field", coalField ? { type: "FeatureCollection", features: [coalField] } : EMPTY_COLLECTION);
    map.easeTo({ center: [selected.lon, selected.lat], zoom: Math.max(map.getZoom(), 9.7), duration: 700, essential: true });
  }, [selected, coalFields]);

  return <div className="map" ref={mapNode} aria-label="Interactive map of assessed REE coal samples" />;
}
