const searchInput = document.getElementById("team-search");
const resultsBox = document.getElementById("team-search-results");

let debounceTimer = null;

searchInput.addEventListener("input", () => {
  const query = searchInput.value.trim();
  clearTimeout(debounceTimer);

  if (query.length < 2) {
    resultsBox.classList.remove("open");
    resultsBox.innerHTML = "";
    return;
  }

  debounceTimer = setTimeout(() => runSearch(query), 200);
});

document.addEventListener("click", (event) => {
  if (!resultsBox.contains(event.target) && event.target !== searchInput) {
    resultsBox.classList.remove("open");
  }
});

async function runSearch(query) {
  const response = await fetch(`/api/teams?q=${encodeURIComponent(query)}`);
  if (!response.ok) return;
  const teams = await response.json();
  renderResults(teams.slice(0, 10));
}

function renderResults(teams) {
  resultsBox.innerHTML = "";
  if (teams.length === 0) {
    resultsBox.classList.remove("open");
    return;
  }
  for (const team of teams) {
    const link = document.createElement("a");
    link.href = `/team/${encodeURIComponent(team.name)}`;
    link.textContent = `${team.name} (${team.titles} title${team.titles === 1 ? "" : "s"})`;
    resultsBox.appendChild(link);
  }
  resultsBox.classList.add("open");
}
