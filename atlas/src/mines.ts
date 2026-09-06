import type { Mine, Sample } from "./types";

export type MineContextFilter = "all" | "current" | "abandoned";
export type NearbyMine = Mine & { distanceKm: number };

const SEARCH_RADIUS_KM = 25;
const GRID_DEGREES = 0.25;

function radians(value: number) { return value * Math.PI / 180; }

function distanceKm(a: { lat: number; lon: number }, b: { lat: number; lon: number }) {
  const dLat = radians(b.lat - a.lat);
  const dLon = radians(b.lon - a.lon);
  const p = Math.sin(dLat / 2) ** 2 + Math.cos(radians(a.lat)) * Math.cos(radians(b.lat)) * Math.sin(dLon / 2) ** 2;
  return 6371 * 2 * Math.atan2(Math.sqrt(p), Math.sqrt(1 - p));
}

function cellFor(lat: number, lon: number) { return `${Math.floor(lat / GRID_DEGREES)}:${Math.floor(lon / GRID_DEGREES)}`; }

export function makeMineIndex(mines: Mine[]) {
  const index = new Map<string, Mine[]>();
  mines.forEach((mine) => {
    const cell = cellFor(mine.lat, mine.lon);
    index.set(cell, [...(index.get(cell) ?? []), mine]);
  });
  return index;
}

export function isMineInContext(mine: Mine, filter: Exclude<MineContextFilter, "all">) {
  const status = mine.st?.toLowerCase() ?? "";
  if (filter === "abandoned") return status.includes("abandoned");
  return !status.includes("abandoned") && mine.f;
}

function nearbyCandidates(sample: Sample, index: Map<string, Mine[]>) {
  const row = Math.floor(sample.lat / GRID_DEGREES);
  const col = Math.floor(sample.lon / GRID_DEGREES);
  const candidates: Mine[] = [];
  // At the latitude of Alaska a grid cell is only about 11 km wide. Three cells
  // in every direction safely covers a 25-km geographic radius nationwide.
  for (let latStep = -3; latStep <= 3; latStep += 1) {
    for (let lonStep = -3; lonStep <= 3; lonStep += 1) {
      candidates.push(...(index.get(`${row + latStep}:${col + lonStep}`) ?? []));
    }
  }
  return candidates;
}

export function hasNearbyMine(sample: Sample, index: Map<string, Mine[]>, filter: Exclude<MineContextFilter, "all">) {
  return nearbyCandidates(sample, index).some((mine) => isMineInContext(mine, filter) && distanceKm(sample, mine) <= SEARCH_RADIUS_KM);
}

export function nearbyMines(sample: Sample, index: Map<string, Mine[]>, filter: MineContextFilter = "all") {
  return nearbyCandidates(sample, index)
    .filter((mine) => filter === "all" || isMineInContext(mine, filter))
    .map((mine) => ({ ...mine, distanceKm: distanceKm(sample, mine) }))
    .filter((mine) => mine.distanceKm <= SEARCH_RADIUS_KM)
    .sort((a, b) => a.distanceKm - b.distanceKm);
}

export const mineType = (type: Mine["ty"]) => ({ S: "Surface", U: "Underground", F: "Facility", "?": "Not reported" })[type];
