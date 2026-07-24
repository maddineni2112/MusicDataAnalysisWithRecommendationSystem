const apiBase = document.body.dataset.apiBase || "http://localhost:8001";

async function fetchJson(path) {
  const response = await fetch(`${apiBase}${path}`);
  if (!response.ok) throw new Error(`Request failed: ${response.status}`);
  return response.json();
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  }[char]));
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
  node.innerHTML = `
    <div class="toolbar">
      <input aria-label="Search songs" placeholder="Search songs">
      <select aria-label="Language filter"><option value="">All languages</option><option>Hindi</option><option>Telugu</option><option>Tamil</option><option>Malayalam</option><option>Kannada</option><option>Punjabi</option><option>Bengali</option><option>Marathi</option></select>
      <select aria-label="Mood filter"><option value="">All moods</option><option>romantic</option><option>energetic</option><option>devotional</option><option>calm</option><option>sad</option></select>
      <button>Search</button>
    </div>
    <div class="results"></div>`;
  const input = node.querySelector("input");
  const selects = node.querySelectorAll("select");
  const button = node.querySelector("button");
  const results = node.querySelector(".results");
  const load = () => {
    const params = new URLSearchParams();
    if (input.value) params.set("q", input.value);
    if (selects[0].value) params.set("language", selects[0].value);
    if (selects[1].value) params.set("mood", selects[1].value);
    const q = params.toString() ? `?${params}` : "";
    fetchJson(`/api/tracks${q}`).then((data) => {
      results.innerHTML = `<table><thead><tr><th>Song</th><th>Album</th><th>Year</th><th>Labels</th><th></th></tr></thead><tbody>${data.items.map((track) => `<tr><td>${escapeHtml(track.name)}</td><td>${escapeHtml(track.album_name || "")}</td><td>${track.release_year || ""}</td><td>${(track.labels || []).map((l) => `<span class="badge">${escapeHtml(l.dimension)}: ${escapeHtml(l.value)} ${(l.confidence || 0).toFixed(2)}</span>`).join("")}</td><td><button data-track-id="${track.id}">Detail</button></td></tr>`).join("")}</tbody></table><div class="detail-panel"></div>`;
      results.querySelectorAll("[data-track-id]").forEach((detailButton) => {
        detailButton.addEventListener("click", () => {
          fetchJson(`/api/tracks/${detailButton.dataset.trackId}/detail`).then((detail) => {
            const panel = results.querySelector(".detail-panel");
            panel.innerHTML = `
              <h2>${escapeHtml(detail.track.name)}</h2>
              <p>${escapeHtml((detail.artists || []).map((artist) => artist.name).join(", "))} · ${escapeHtml(detail.track.album_name || "Unknown album")} · ${detail.track.release_year || "Unknown year"}</p>
              <h3>Source Playlists</h3>
              <p>${(detail.playlists || []).map((playlist) => `<span class="badge">${escapeHtml(playlist.name)}</span>`).join("") || "No playlist lineage yet."}</p>
              <h3>Similar Songs</h3>
              <table><thead><tr><th>Song</th><th>Score</th><th>Why</th></tr></thead><tbody>${(detail.similar_tracks || []).map((item) => `<tr><td>${escapeHtml(item.track.name)}</td><td>${item.score}</td><td>${escapeHtml(item.reasons.join(", "))}</td></tr>`).join("")}</tbody></table>`;
          });
        });
      });
    });
  };
  button.addEventListener("click", load);
  load();
}

function mountRecommender() {
  const node = document.querySelector('[data-widget="recommender"]');
  if (!node) return;
  node.innerHTML = `
    <div class="toolbar">
      <input aria-label="Seed track ID" placeholder="Seed track ID, e.g. 1">
      <input aria-label="Natural language query" placeholder="Optional query: romantic Telugu songs from the 2010s">
      <select><option value="10">10</option><option value="5">5</option><option value="20">20</option><option value="50">50</option></select>
      <button>Recommend</button>
    </div>
    <div class="results"></div>`;
  const inputs = node.querySelectorAll("input");
  const select = node.querySelector("select");
  const button = node.querySelector("button");
  const results = node.querySelector(".results");
  button.addEventListener("click", () => {
    if (!inputs[0].value) return;
    const params = new URLSearchParams({ track_id: inputs[0].value, limit: select.value });
    if (inputs[1].value) params.set("query", inputs[1].value);
    fetchJson(`/api/recommendations?${params}`).then((data) => {
      results.innerHTML = data.items.length
        ? `<p>Parsed filters: ${JSON.stringify(data.parsed_query_filters)}</p><table><thead><tr><th>Song</th><th>Score</th><th>Reasons</th><th>Breakdown</th></tr></thead><tbody>${data.items.map((item) => `<tr><td>${item.track.name}</td><td>${item.score}</td><td>${item.reasons.join(", ")}</td><td><code>${JSON.stringify(item.score_breakdown)}</code></td></tr>`).join("")}</tbody></table>`
        : "<p>No recommendations found yet. Import more tracks with shared labels.</p>";
    });
  });
}

function mountArtists() {
  const node = document.querySelector('[data-widget="artist-table"]');
  if (!node) return;
  fetchJson("/api/artists").then((artists) => {
    node.innerHTML = artists.length
      ? `<div class="toolbar"><button data-action="network">Load artist network</button></div><table><thead><tr><th>Artist</th><th>Genres</th><th></th></tr></thead><tbody>${artists.map((a) => `<tr><td>${escapeHtml(a.name)}</td><td>${escapeHtml((a.genres || []).join(", "))}</td><td><button data-artist-id="${a.id}">Detail</button></td></tr>`).join("")}</tbody></table><div class="detail-panel"></div>`
      : "<p>No artists imported yet.</p>";
    const panel = node.querySelector(".detail-panel");
    node.querySelector('[data-action="network"]').addEventListener("click", () => {
      fetchJson("/api/artist-network").then((network) => {
        panel.innerHTML = `
          <h2>Artist Network</h2>
          <p>${network.nodes.length} artists connected across ${network.track_count} tracks.</p>
          <table><thead><tr><th>Source</th><th>Target</th><th>Shared Tracks</th></tr></thead><tbody>${network.edges.map((edge) => {
            const source = network.nodes.find((node) => node.id === edge.source);
            const target = network.nodes.find((node) => node.id === edge.target);
            return `<tr><td>${escapeHtml(source ? source.name : edge.source)}</td><td>${escapeHtml(target ? target.name : edge.target)}</td><td>${edge.weight}</td></tr>`;
          }).join("")}</tbody></table>`;
      });
    });
    node.querySelectorAll("[data-artist-id]").forEach((detailButton) => {
      detailButton.addEventListener("click", () => {
        fetchJson(`/api/artists/${detailButton.dataset.artistId}/detail`).then((detail) => {
          panel.innerHTML = `
            <h2>${escapeHtml(detail.artist.name)}</h2>
            <h3>Top Tracks</h3>
            <table><thead><tr><th>Song</th><th>Year</th><th>Popularity</th></tr></thead><tbody>${detail.tracks.map((track) => `<tr><td>${escapeHtml(track.name)}</td><td>${track.release_year || ""}</td><td>${track.popularity ?? ""}</td></tr>`).join("")}</tbody></table>
            <h3>Label Mix</h3>
            <p>${detail.label_mix.map((label) => `<span class="badge">${escapeHtml(label.dimension)}: ${escapeHtml(label.value)} (${label.count})</span>`).join("") || "No labels yet."}</p>
            <h3>Collaborators</h3>
            <p>${detail.collaborators.map((artist) => `<span class="badge">${escapeHtml(artist.name)} (${artist.shared_tracks})</span>`).join("") || "No collaborations in this sample yet."}</p>`;
        });
      });
    });
  });
}

function mountModelInsights() {
  const node = document.querySelector('[data-widget="model-insights"]');
  if (!node) return;
  fetchJson("/api/model-insights").then((data) => {
    node.innerHTML = `
      <div class="grid">
        <article class="card"><div class="metric">${data.dataset.tracks}</div><div class="label">Tracks Evaluated</div></article>
        <article class="card"><div class="metric">${data.dataset.labels}</div><div class="label">Inferred Labels</div></article>
        <article class="card"><div class="metric">${data.dataset.label_density}</div><div class="label">Labels Per Track</div></article>
      </div>
      <h2>Recommender</h2>
      <p>${escapeHtml(data.recommender)} uses ${data.signals.map(escapeHtml).join(", ")}.</p>
      <h2>Evaluation</h2>
      <p>${escapeHtml(data.evaluation_plan)}</p>
      <pre>${escapeHtml(JSON.stringify(data, null, 2))}</pre>`;
  });
}

function mountQuality() {
  const node = document.querySelector('[data-widget="quality-summary"]');
  if (!node) return;
  fetchJson("/api/data-quality/summary").then((data) => {
    node.innerHTML = data.checks && data.checks.length
      ? `<table><thead><tr><th>Check</th><th>Status</th><th>Count</th><th>Severity</th></tr></thead><tbody>${data.checks.map((c) => `<tr><td>${c.name}</td><td>${c.status}</td><td>${c.count}</td><td>${c.severity}</td></tr>`).join("")}</tbody></table>`
      : "<p>No quality runs yet. Run the quality CLI or admin endpoint after import.</p>";
  });
}

function mountAdminOps() {
  const node = document.querySelector('[data-widget="admin-ops"]');
  if (!node) return;
  node.innerHTML = `
    <div class="toolbar">
      <input aria-label="Admin token" placeholder="Admin token" value="change-me-local-only">
      <button data-action="import">Import sample CSV</button>
      <button data-action="quality">Run quality checks</button>
      <button data-action="jobs">Refresh job history</button>
    </div>
    <div class="results"></div>`;
  const token = node.querySelector("input");
  const results = node.querySelector(".results");
  const adminFetch = (path, options = {}) => fetch(`${apiBase}${path}`, {
    ...options,
    headers: { "x-admin-token": token.value, ...(options.headers || {}) },
  }).then((response) => response.json());
  const loadJobs = () => {
    adminFetch("/api/admin/jobs").then((data) => {
      results.innerHTML = data.items && data.items.length
        ? `<table><thead><tr><th>ID</th><th>Job</th><th>Status</th><th>Read</th><th>Written</th><th>Skipped</th></tr></thead><tbody>${data.items.map((job) => `<tr><td>${job.id}</td><td>${job.job_type}</td><td>${job.status}</td><td>${job.rows_read}</td><td>${job.rows_written}</td><td>${job.rows_skipped}</td></tr>`).join("")}</tbody></table>`
        : "<p>No jobs logged yet.</p>";
    });
  };
  node.querySelector('[data-action="import"]').addEventListener("click", () => {
    adminFetch('/api/admin/import/csv?path=data/sample/indian_music_sample.csv&source_name=Sample%20Indian%20Music%20Dataset', { method: "POST" }).then(loadJobs);
  });
  node.querySelector('[data-action="quality"]').addEventListener("click", () => {
    adminFetch("/api/admin/quality/run", { method: "POST" }).then(loadJobs);
  });
  node.querySelector('[data-action="jobs"]').addEventListener("click", loadJobs);
  loadJobs();
}

mountOverview();
mountTrends();
mountTrackTable();
mountRecommender();
mountArtists();
mountModelInsights();
mountQuality();
mountAdminOps();
