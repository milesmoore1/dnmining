import type { GeoCollection, GeoFeature, Geometry, Sample } from "./types";

const empty: GeoCollection = { type: "FeatureCollection", features: [] };

export const EMPTY_COLLECTION = empty;

export function sampleFeature(sample: Sample) {
  return {
    type: "Feature" as const,
    properties: {
      id: sample.id,
      pred: sample.pred,
      split: sample.split,
      score: sample.p_high,
      state: sample.state ?? "Unknown",
    },
    geometry: { type: "Point" as const, coordinates: [sample.lon, sample.lat] },
  };
}

export function samplesCollection(samples: Sample[]) {
  return { type: "FeatureCollection" as const, features: samples.map(sampleFeature) };
}

function isInsideRing(point: [number, number], ring: number[][]) {
  let inside = false;
  const [x, y] = point;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const [xi, yi] = ring[i];
    const [xj, yj] = ring[j];
    const crosses = yi > y !== yj > y;
    const xAtY = ((xj - xi) * (y - yi)) / (yj - yi || Number.EPSILON) + xi;
    if (crosses && x < xAtY) inside = !inside;
  }
  return inside;
}

function isInsidePolygon(point: [number, number], rings: number[][][]) {
  return isInsideRing(point, rings[0]) && !rings.slice(1).some((ring) => isInsideRing(point, ring));
}

function containsPoint(geometry: Geometry, point: [number, number]) {
  if (geometry.type === "Polygon") {
    return isInsidePolygon(point, geometry.coordinates as number[][][]);
  }
  return (geometry.coordinates as number[][][][]).some((polygon) => isInsidePolygon(point, polygon));
}

/**
 * The geodatabase has coal-field polygons, not mine/site polygons. A returned
 * feature is therefore displayed explicitly as coal-field context, never as a
 * fabricated footprint for an assay point.
 */
export function coalFieldForSample(sample: Sample, fields: GeoCollection | null): GeoFeature | null {
  if (!fields) return null;
  return fields.features.find((feature) => containsPoint(feature.geometry, [sample.lon, sample.lat])) ?? null;
}
