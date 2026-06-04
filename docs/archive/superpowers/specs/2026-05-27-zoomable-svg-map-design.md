# Zoomable SVG Map — Design Spec

**Date:** 2026-05-27
**Status:** Approved

## Goal

Replace the static zone image with a zoomable map where residents can pinch/zoom to see streets relative to the evacuation zone boundary at any zoom level, with zero external service dependencies.

## Architecture

Two layers, both self-hosted:

1. **Base layer**: A high-resolution (~4000px wide) pre-rendered map image of the Garden Grove area showing streets, labels, and landmarks. Generated from CARTO/Geoapify as a one-time PNG. Served from `/images/zone-map-hires.png`.

2. **SVG overlay**: The evacuation polygon, facility dot, and shelter markers rendered as SVG elements positioned over the base image using pixel coordinates mapped from lat/lon. The SVG scales 1:1 with the base image on zoom.

3. **Pinch/zoom behavior**: CSS `overflow: auto` on the container + a small vanilla JS pinch-zoom handler (~30 lines). Both the image and SVG scale together. No external library.

4. **Fallback**: The current static zone image (`/images/zone-map.png`) stays as the no-JS, no-zoom fallback. Progressive enhancement: if JS loads, upgrade to zoomable. If JS fails, the static image still shows the zone.

## Coordinate Mapping

The base image covers a known geographic bounding box. To position SVG elements:

```
pixelX = (lon - bbox.west) / (bbox.east - bbox.west) * imageWidth
pixelY = (bbox.north - lat) / (bbox.north - bbox.south) * imageHeight
```

The bounding box is determined by the base image's geographic extent (set at generation time). The evacuation polygon coordinates from `config.json` are mapped to pixel coordinates using this formula. This mapping is done once at image generation time and baked into the SVG.

## Components

### Base image
- Source: CARTO basemaps (one-time screenshot at high resolution)
- Resolution: ~4000x2600px (16:10 aspect, street names legible at 2-3x zoom)
- Format: PNG, optimized
- Location: `/images/zone-map-hires.png`

### SVG overlay
- Evacuation polygon: `<polygon>` with semi-transparent blue fill (#3b82f680) and 2px blue stroke
- Facility: `<circle>` red/black dot at GKN Aerospace location
- Shelters: `<g>` groups with house emoji or icon + label, positioned at shelter coordinates
- Viewbox matches the base image pixel dimensions

### Pinch-zoom handler
- ~30 lines of vanilla JS
- Supports: pinch-zoom (mobile), scroll-wheel zoom (desktop), double-tap zoom
- Min zoom: 1x (fit container). Max zoom: 3x.
- Pan via touch-drag or mouse-drag when zoomed in
- No external library

### "Check your zone" button
- Retained from current implementation
- Links to Genasys Protect (protect.genasys.com)
- Positioned below the map

### "Open in Google Maps" link
- Simple `<a>` link to Google Maps centered on the facility
- For users who want Street View, routing, or familiar Google UI
- Not an embed — just a link

### Wind overlay
- Retained from current implementation
- Positioned absolutely over the map container

## Fallback behavior

```
Browser loads dashboard.html
├── Static image loads immediately (in <noscript> or as default src)
├── JS loads?
│   ├── Yes → Upgrade to zoomable view (swap in hires image + SVG overlay)
│   └── No → Static image stays (fully functional, just not zoomable)
```

## Files changed

- `dashboard.html`: Map tab panel content (HTML + CSS + ~30 lines JS)
- `images/zone-map-hires.png`: New high-res base image
- `sw.js`: Add hires image to cache (bump to v5)

## Files NOT changed

- `config.json`: Evacuation polygon coordinates already there
- `vercel.json`: No new external domains needed
- `eval/`: No behavioral test changes needed

## Out of scope

- Address geocoding (use Genasys Protect link)
- Tile servers of any kind
- Google Maps JS API / Embed iframe
- Real-time zone boundary updates (manual image regeneration)
