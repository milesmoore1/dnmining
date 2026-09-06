# REE Prospectivity Atlas

React/TypeScript front end for the Atlas baseline export.

## Run locally

```bash
npm install
npm run dev
```

The application consumes the existing, generated artifacts in `../web`:

- `miles_data.json` — baseline model samples and predictions
- `coalfields2.geojson` — geodatabase coal-field polygons used only as map context

The UI deliberately identifies the records as analysis samples, not mine sites.
A selected sample can show a coal-field polygon only when its coordinate lies in
one; the project does not contain individual mine-footprint geometry.

`npm run build` makes a production bundle in `dist/` and copies the same
existing web artifacts into it.
