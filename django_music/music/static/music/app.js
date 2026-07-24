const apiBase = document.body.dataset.apiBase || "http://localhost:8001";

async function fetchJson(path) {
  const response = await fetch(`${apiBase}${path}`);
  if (!response.ok) throw new Error(`Request failed: ${response.status}`);
  return response.json();
}

function mountOverview() {
  const node = document.querySelector('[data-widget="overview"]');
  if (!node) return;
  fetchJson("/api/dashboard/overview").then((data) => {
    const cards = [
      ["Tracks", data.tracks],
      ["Artists", data.artists],
      ["Playlists", data.playlists],
      ["Languages", data.languages],
      ["Avg Label Confidence", data.label_confidence_avg ? data.label_confidence_avg.toFixed(2) : "N/A"],
      ["Official Popularity Rows", data.official_popularity_available],
    ];
    node.innerHTML = cards.map(([label, value]) => `<article class="card"><div class="metric">${value}</div><div class="label">${label}</div></article>`).join("");
  }).catch(() => { node.innerHTML = '<article class="card">Start the FastAPI service and import sample data to view KPIs.</article>'; });
}

function mountTrends() {
  const node = document.querySelector('[data-widget="trends"]');
  if (!node) return;
  fetchJson("/api/dashboard/trends").then((data) => {
    const rows = data.language_trends || [];
    node.innerHTML = rows.length
      ? `<table><thead><tr><th>Year</th><th>Language</th><th>Tracks</th></tr></thead><tbody>${rows.map((r) => `<tr><td>${r.year}</td><td>${r.language}</td><td>${r.count}</td></tr>`).join("")}</tbody></table>`
      : "<p>No trend data yet. Import the sample dataset and run label inference.</p>";
  });
}

function mountTrackTable() {
  const node = document.querySelector('[data-widget="track-table"]');
  if (!node) return;
  node.innerHTML = '<div class="toolbar"><input aria-label="Search songs" placeholder="Search songs"><button>Search</button></div><div class="results"></div>';
  const input = node.querySelector("input");
  const button = node.querySelector("button");
  const results = node.querySelector(".results");
  const load = () => {
    const q = input.value ? `?q=${encodeURIComponent(input.value)}` : "";
    fetchJson(`/api/tracks${q}`).then((data) => {
      results.innerHTML = `<table><thead><tr><th>Song</th><th>Album</th><th>Year</th><th>Labels</th></tr></thead><tbody>${data.items.map((track) => `<tr><td>${track.name}</td><td>${track.album_name || ""}</td><td>${track.release_year || ""}</td><td>${(track.labels || []).map((l) => `<span class="badge">${l.dimension}: ${l.value} ${(l.confidence || 0).toFixed(2)}</span>`).join("")}</td></tr>`).join("")}</tbody></table>`;
    });
  };
  button.addEventListener("click", load);
  load();
}

function mountRecommender() {
  const node = document.querySelector('[data-widget="recommender"]');
  if (!node) return;
  node.innerHTML = '<div class="toolbar"><input aria-label="Seed track ID" placeholder="Seed track ID, e.g. 1"><select><option value="10">10</option><option value="5">5</option><option value="20">20</option><option value="50">50</option></select><button>Recommend</button></div><div class="results"></div>';
  const input = node.querySelector("input");
  const select = node.querySelector("select");
  const button = node.querySelector("button");
  const results = node.querySelector(".results");
  button.addEventListener("click", () => {
    if (!input.value) return;
    fetchJson(`/api/recommendations?track_id=${encodeURIComponent(input.value)}&limit=${select.value}`).then((data) => {
      results.innerHTML = data.items.length
        ? `<table><thead><tr><th>Song</th><th>Score</th><th>Reasons</th></tr></thead><tbody>${data.items.map((item) => `<tr><td>${item.track.name}</td><td>${item.score}</td><td>${item.reasons.join(", ")}</td></tr>`).join("")}</tbody></table>`
        : "<p>No recommendations found yet. Import more tracks with shared labels.</p>";
    });
  });
}

function mountArtists() {
  const node = document.querySelector('[data-widget="artist-table"]');
  if (!node) return;
  fetchJson("/api/artists").then((artists) => {
    node.innerHTML = artists.length
      ? `<table><thead><tr><th>Artist</th><th>Genres</th></tr></thead><tbody>${artists.map((a) => `<tr><td>${a.name}</td><td>${(a.genres || []).join(", ")}</td></tr>`).join("")}</tbody></table>`
      : "<p>No artists imported yet.</p>";
  });
}

function mountModelInsights() {
  const node = document.querySelector('[data-widget="model-insights"]');
  if (!node) return;
  fetchJson("/api/model-insights").then((data) => {
    node.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
  });
}

mountOverview();
mountTrends();
mountTrackTable();
mountRecommender();
mountArtists();
mountModelInsights();
