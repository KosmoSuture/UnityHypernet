---
ha: "0.1.8.docs.webxr-status"
object_type: "document"
status: "active"
visibility: "public"
addressed_by: "2.6.codex"
addressed_at: "2026-05-01"
---
# Hypernet VR — WebXR Status

## The Pivot: Unity to WebXR (A-Frame)

The original plan (documented in UNITY-QUEST3-QUICKSTART.md and UNITY-START-TODAY.md) was a native Unity app compiled to APK and sideloaded onto the Quest 3. That approach required:

- Unity Editor install (~10GB), Android SDK/NDK, OpenJDK
- Meta developer account, USB debugging, APK sideloading
- C# scripts for every feature, 5-10 minute rebuild cycles
- All complexity just to display a photo on a quad

We pivoted to **WebXR via A-Frame**. The entire VR interface is a single HTML file served by the existing Hypernet server. No installs, no builds, no sideloading. Open the Quest browser, type the URL, put on the headset. It works.

The Unity guides remain in this directory as historical reference. The `app/` directory contains a separate FastAPI backend scaffolded for a VR-specific API layer — it has models for bookmarks, notes, contacts, calendar events, etc. That code is unused; the WebXR page talks directly to the Hypernet Core API.

## Current Status

**What's built:** A fully functional spatial browser for the entire Hypernet address space.

**Where the code lives:** `0/0.1 - Hypernet Core/hypernet/static/vr.html` (single file, ~1,800 lines)

**Server route:** `GET /vr` in `hypernet/server.py` (line 1675) serves the HTML.

**API endpoints used by the VR page:**
- `GET /children` — root-level nodes
- `GET /children/{address}` — direct children of any node (one level deep)
- `GET /node/{address}` — full node data
- `GET /node/{address}/links?direction=both` — inter-node links
- `GET /stats` — total node count
- `GET /search?q={query}` — full-text search across node data fields (title, name, description)
- `GET /query?prefix={address}` — fallback if `/children` or `/search` returns no results

## How to Access

### Desktop (development/preview)
1. Start the Hypernet server:
   ```
   cd "c:/Hypernet/Hypernet Structure/0/0.1 - Hypernet Core"
   python -m hypernet launch
   ```
2. Open http://localhost:8000/vr in any browser
3. Navigate with WASD + mouse drag. Click nodes to dive in.

### Quest 3 (immersive VR)
1. Start the server on your PC (same as above)
2. Make sure Quest and PC are on the same WiFi network
3. Find your PC's local IP (run `ipconfig`, look for IPv4 under your WiFi adapter)
4. Open the Meta Quest Browser and navigate to `http://<YOUR-PC-IP>:8000/vr`
5. The page loads in flat mode. Click the VR goggles icon (bottom-right) to enter immersive mode.
6. Use controller laser pointer to select nodes, thumbstick to move.

### Hand Tracking (Quest)
The scene is configured with `webxr="optionalFeatures: hand-tracking"`. Point at nodes and pinch to select. Left hand for locomotion, right hand for laser pointer.

## Features

### Spatial Navigation
- **Hierarchical browsing** — start at root (categories 0-9), click any node to see its children, navigate up/back
- **5 layout modes** — Orbital (default ring), Grid, Helix (spiral tower), Tree (fan arc), Constellation (clustered groups). Cycle with Tab or the Layout button.
- **Breadcrumb trail** — full path shown in HUD, each segment clickable
- **Address jump** — type any address directly into the search box (press `/` to focus)
- **Live search** — type in the search box to search nodes in real-time; matching nodes in current view pulse, non-matching fade; click a result to navigate to its parent
- **Navigation history** — back button (B key) walks through visited nodes
- **Zoom transitions** — clicking a node flies the camera toward it while existing nodes shrink, then rebuilds the scene at the new level
- **Number shortcuts** — press 0-9 at root to jump directly to that category
- **Depth indicator** — visual dots showing how deep you are in the hierarchy

### Visual Design
- **Color-coded categories** — each top-level category (0=Infrastructure, 1=People, 2=AI, etc.) has a distinct color carried through all child nodes
- **Node sizing** — spheres scale based on child count; nodes with many children appear larger
- **Orbital rings** — each node has a tilted animated ring; nodes with 10+ children get a second counter-rotating ring
- **Inner core glow** — nodes with 5+ children get an animated bright inner sphere
- **Energy beams** — animated particles travel along connection lines from center to each child node
- **Ground grid** — reference grid with radial distance circles
- **Depth rings** — concentric rings on the ground surface indicate current hierarchy depth
- **Starfield** — 150 tinted, twinkling stars in the background
- **Ambient particles** — 60 floating colored particles for atmosphere
- **Fog** — exponential fog fades distant objects into the void
- **Loading screen** — branded spinner during navigation transitions
- **Auto-rotate** — press R to slowly orbit the scene for a cinematic view
- **Enhanced hover** — smooth animated scale-up, glow expansion, and ring brightening on hover

### Inter-Node Links
- Toggle with the Links button — draws gold connection lines between sibling nodes that have Hypernet links to each other
- Fetches link data from the `/node/{address}/links` API

### Info Panel
- **Desktop**: hover over a node to see title, address, type, creation date, category, child count, and all data fields in a slide-in side panel. Full node data is lazy-fetched from the API for richer detail (version, owner, all fields). Click "Enter this node" to navigate.
- **VR**: a floating billboard panel appears above the hovered node with the same information. Clickable "ENTER NODE" button.

### VR Navigation Panel
- In VR mode, a floating panel follows the camera with the current address, breadcrumb, node count, and Up/Root/Layout buttons — all clickable with the laser pointer.

### Leaf Node Detail View
- When navigating to a node with no children, displays the node's full data as a rich 3D presentation
- Fetches complete node data from the API, shows title, category, type, creation date, and all data fields
- Decorative orbital ring animates around the leaf display

### Navigation Effects
- **Particle burst** — 18 particles explode outward in the category color whenever you navigate to a new node
- **Category environment** — the main light and sky subtly tint to match the current category color (e.g., green for People, purple for AI)

### Audio
- Procedural ambient soundscape — layered sine oscillators (55-165 Hz) with slow LFOs and filtered noise
- Navigation sounds — rising chirp on node entry
- Hover sounds — randomized short tones on mouseover
- Toggle with M key or the speaker button

### Pagination
- Nodes with more than 40 children show the first 40 (sorted by child count — most connected first)
- Desktop: "Load More" clickable hint at bottom-right
- VR: "LOAD MORE" button on the VR nav panel with remaining count
- Additional batches of 40 loaded on demand

### Recently Visited
- Left sidebar shows last 6 unique visited addresses with category color borders
- Click any address to return instantly
- Automatically hidden in VR mode

### Minimap
- Bottom-left canvas shows a top-down view of all current nodes with color-coded dots and connection lines to center
- Node dots sized proportionally to child count
- White triangle indicator shows current camera position

### Keyboard Controls
| Key | Action |
|-----|--------|
| WASD | Move |
| Mouse drag | Look |
| Click | Enter node |
| Hover | Inspect node |
| Backspace | Go up one level |
| Home | Return to root |
| Tab | Cycle layout |
| / | Focus search |
| B | Go back |
| M | Toggle sound |
| R | Toggle auto-rotate |
| 0-9 | Jump to root category (at root) |
| Esc | Close panels/search |
| ? | Help overlay |

## Architecture

```
Quest Browser / Desktop Browser
        |
        | HTTP GET /vr
        v
  Hypernet Server (FastAPI, port 8000)
        |
        | serves vr.html (static file)
        v
  A-Frame Scene (client-side)
        |
        | fetch() calls to same origin
        v
  /children, /children/{addr}, /node/{addr}, /stats, /query
        |
        v
  Hypernet Store (node_store.py)
```

The VR page is entirely client-side after initial load. It fetches node data from the same server that served the HTML — no CORS issues, no separate backend needed. Navigation triggers API calls to load children of the target address, then renders them as A-Frame entities in a 3D scene.

Key libraries:
- **A-Frame 1.7.0** — WebXR framework built on Three.js
- **A-Frame Extras 7.6.1** — movement-controls component for WASD + thumbstick locomotion

Custom A-Frame components registered in the page:
- `billboard` — makes text always face the camera
- `follow-camera` — VR nav panel smoothly follows head position
- `vr-button` — clickable VR UI buttons
- `node-interact` — hover/click behavior for node spheres
- `energy-beam` — animated particle traveling along connection lines

## Performance Notes for Quest

The Quest 3 browser runs Chromium with WebXR support. Key considerations:

- **Target 72 FPS** (Quest default refresh rate). The scene uses emissive materials rather than real-time lighting to keep GPU load low.
- **Entity count** — each node creates ~5-7 A-Frame entities (sphere, glow, ring, text x2-3, optional inner core and second ring). With 20+ child nodes that's 100-140 entities plus 60 particles and 150 stars. This is within Quest browser limits but could get heavy past ~50 visible nodes.
- **Fog culling** — exponential fog (density 0.008) hides distant geometry, reducing effective draw distance.
- **No physics** — no collision or physics simulation; all interaction is raycaster-based.
- **Single draw per navigation** — nodes are created once per navigation event, not every frame. Only animations and the billboard component run per-tick.
- **Font rendering** — A-Frame's SDF text renderer (roboto) is GPU-efficient. Text entities use `billboard` for readability but this adds per-frame lookAt calls.
- **Texture-free** — no image textures loaded; everything is procedural geometry and flat/emissive materials. This means minimal memory and no texture upload stalls.

If performance becomes an issue at deeper hierarchy levels with many children:
- Reduce particle count (currently 60) and star count (currently 150)
- Implement LOD — only render nodes within a radius
- Use instanced rendering for identical geometries
- Paginate children (fetch first N, load more on demand)

## Completed Enhancements (Session 2+)

- **Search results in 3D** — live search with debounce, matching nodes pulse/glow, non-matching fade, result dropdown with click-to-navigate
- **Full-text search API** — `/search?q=` endpoint searches across all node data fields (title, name, description, etc.)
- **Node preview content** — full node data lazy-fetched on hover for richer info panel (version, owner, all fields)
- **Leaf node detail view** — rich 3D presentation of node data when navigating to a node with no children
- **Category-themed environment** — main light and sky tint shift to match current category color
- **Navigation particle burst** — particle explosion effect in category color on every navigation
- **Zoom transitions** — camera flies toward clicked node while existing nodes shrink
- **Auto-rotate** — slow cinematic rotation of the scene (R key)
- **Number key shortcuts** — 0-9 jumps to root categories
- **Enhanced hover effects** — smooth animated scale/glow with easing
- **Smooth layout transitions** — cycling layouts animates nodes to new positions (700ms eased)
- **Pagination** — nodes with 40+ children show first 40 sorted by child count; "Load More" in both desktop and VR
- **Camera position memory** — remembers camera position at each hierarchy level; restored when returning
- **Recently visited panel** — quick-access sidebar showing last 6 visited addresses with color-coded borders
- **Cinematic intro** — camera starts far back and zooms in on first load with loading status messages
- **Improved minimap** — camera position triangle indicator, node dots sized by child count
- **Fixed navigation history** — clean back-navigation without sentinel values

## Next Steps / Future Enhancements

- **Photo/media rendering** — display actual images on quad planes for media nodes
- **AI chat in VR** — floating text panel connected to `/chat` endpoint, voice input via Web Speech API
- **Multi-user** — WebRTC or WebSocket-based shared presence (see each other's avatars)
- **Node editing** — create/update nodes from within VR using virtual keyboard
- **Timeline mode** — arrange nodes chronologically, fly through time
- **Link graph visualization** — full force-directed graph of inter-node links, not just sibling links
- **Mobile AR** — A-Frame supports WebXR AR on Android; could overlay Hypernet nodes on the real world
- **Performance profiling** — run Quest browser developer tools to identify actual bottlenecks
