export type Prediction = "high" | "low";
export type Split = "train" | "test";

export type Sample = {
  id: string;
  lat: number;
  lon: number;
  county: string | null;
  state: string | null;
  basin: string | null;
  bed: string | null;
  rank: string | null;
  ash: number | null;
  thick: number | null;
  value: number | null;
  p_high: number;
  pred: Prediction;
  tier: Prediction | null;
  split: Split;
  dl2: Record<string, number | null>;
  feat: Record<string, number | string | null>;
};

export type AtlasMeta = {
  pipeline: string;
  treatment: string;
  basis: string;
  class_names: [Prediction, Prediction];
  his_caveat: string;
  steps: {
    element_rows_loaded: number;
    labeled_rows: number;
    train_rows: number;
    test_rows: number;
  };
  metrics: {
    accuracy: number;
    auc: number;
  };
};

export type AtlasData = { meta: AtlasMeta; samples: Sample[] };

export type Mine = {
  id: string;
  n: string | null;
  o: string | null;
  c: string | null;
  lat: number;
  lon: number;
  st: string | null;
  ty: "S" | "U" | "F" | "?";
  cm: "B" | "A" | "L" | "?";
  e: number | null;
  tw: string | null;
  cty: string | null;
  stt: string | null;
  f: boolean;
};

export type MineData = {
  meta: { source: string; n: number };
  mines: Mine[];
};

export type Geometry = {
  type: "Polygon" | "MultiPolygon";
  coordinates: number[][][] | number[][][][];
};

export type GeoFeature = {
  type: "Feature";
  properties: Record<string, unknown>;
  geometry: Geometry;
};

export type GeoCollection = {
  type: "FeatureCollection";
  features: GeoFeature[];
};
