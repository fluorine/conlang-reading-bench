// Published runs from reports/index.json, in the release order shown below.
const accuracy = {
  "two": [
    {
      "minimal": 43.75,
      "english": 69.79166666666666
    },
    {
      "minimal": 48.95833333333333,
      "english": 84.375
    },
    {
      "minimal": 44.79166666666667,
      "english": 62.5
    },
    {
      "minimal": 98.95833333333334,
      "english": 100
    }
  ],
  "four": [
    {
      "minimal": 100 * 82 / 192,
      "english": 100 * 153 / 192
    },
    {
      "minimal": 100 * 76 / 192,
      "english": 100 * 143 / 192
    },
    {
      "minimal": 100 * 67 / 192,
      "english": 100 * 118 / 192
    },
    {
      "minimal": 100 * 192 / 192,
      "english": 100 * 191 / 192
    }
  ]
};

const models = ["GPT-4o mini (default)", "GPT-4.1 mini (default)", "GPT-5.4 nano (default)", "GPT-6 Luna (low)"];
const shortNames = ["4o mini (default)", "4.1 mini (default)", "5.4 nano (default)", "Luna (low)"];
const releaseDates = ["2024-07-18", "2025-04-14", "2026-03-17", "2026-09-22"];
const dateLabel = new Intl.DateTimeFormat("en", { month: "short", year: "numeric", timeZone: "UTC" });
const plot = document.querySelector("#accuracy-overview");
const tabs = Array.from(document.querySelectorAll("[role=tab][data-tier]"));
let tier = tabs.at(-1).dataset.tier;
const storageKey = "conlang-chart-settings-v1";
const conditions = document.querySelector("#plot-conditions");
const scale = document.querySelector("#plot-scale");
const grid = plot.querySelector(".scatter-grid");
const detail = plot.querySelector(".scatter-detail");
const note = plot.querySelector("#scatter-note");
const legend = plot.querySelector(".scatter-key");
const conditionNames = { minimal: "Conlang score", english: "English control" };

function render() {
  grid.replaceChildren();
  const isFour = tier === "four";
  const isResearch = tier === "research";
  const questionCount = isResearch ? 48 : isFour ? 192 : 96;
  const storyCount = isResearch ? 48 : questionCount / 4;
  const activeModels = isResearch ? tier3Research.models.map(model => model.name) : models;
  const activeShortNames = isResearch ? tier3Research.models.map(model => model.shortName) : shortNames;
  const activeDates = isResearch ? tier3Research.models.map(model => model.releaseDate) : releaseDates;
  const activeTimes = activeDates.map(date => Date.parse(date));
  const selected = Array.from(conditions.querySelectorAll("input:checked"), input => input.value);
  const both = selected.length === 2;
  const logarithmic = scale.checked;
  const position = value => logarithmic ? 100 * (Math.log10(value) - 1) : value;
  const ticks = logarithmic ? [10, 20, 40, 60, 100] : [0, 25, 50, 75, 100];
  plot.querySelector("#scatter-label").textContent = logarithmic
    ? "Accuracy (% correct, log scale)" : "Accuracy (% correct)";
  grid.classList.toggle("paired", both);
  for (const key of Object.keys(conditionNames)) {
    legend.querySelector("." + key).hidden = !selected.includes(key);
  }
  detail.textContent = selected.length ? "Select a point to see the exact score." : "Choose a reading condition to show scores.";
  note.textContent = isResearch
    ? "Exploratory five-object grammar: 48 stories per model, medium effort, one question per story. Scores are preliminary and not directly comparable with earlier tiers."
    : isFour
    ? "48 four-transfer stories per model. Luna used low reasoning with a 2,048-token cap."
    : "24 reference stories per model. Luna used low reasoning with a 512-token cap.";
  plot.querySelector("#condition-description").textContent = isResearch
    ? "The conlang score is the percentage correct. English is a separate control. Select a point for its score."
    : "The conlang score is the percentage correct with minimal clues. English is a separate control. Select a point for its score.";
  plot.querySelector("#research-note").hidden = !isResearch;

  for (const value of ticks) {
    const tick = document.createElement("div");
    tick.className = "scatter-tick";
    tick.setAttribute("aria-hidden", "true");
    tick.style.setProperty("--y", position(value) + "%");
    const label = document.createElement("span");
    label.textContent = value + "%";
    tick.append(label);
    grid.append(tick);
  }

  activeModels.forEach((model, i) => {
    const column = document.createElement("div");
    column.className = "scatter-column";
    const firstRelease = Math.min(...activeTimes);
    const elapsed = activeTimes[i] - firstRelease;
    const span = Math.max(...activeTimes) - firstRelease || 1;
    column.style.left = (isResearch ? 25 + 50 * elapsed / span : 10 + 80 * elapsed / span) + "%";
    const date = document.createElement("time");
    date.className = "scatter-date";
    date.dateTime = activeDates[i];
    date.textContent = dateLabel.format(activeTimes[i]);
    column.append(date);
    const scores = isResearch ? tier3Research.models[i].scores : accuracy[tier][i];
    const label = document.createElement("span");
    label.className = "scatter-model";
    label.textContent = activeShortNames[i];
    if (selected.length && scores) {
      const heights = selected.map(key => position(scores[key]));
      const above = Math.max(...heights) < 87;
      const edge = above ? Math.max(...heights) : Math.min(...heights);
      label.style.bottom = `calc(${edge}% + ${above ? ".65rem" : "-1.9rem"})`;
      column.append(label);
    }
    if (scores && both) {
      const connector = document.createElement("span");
      connector.className = "scatter-connector";
      connector.setAttribute("aria-hidden", "true");
      const left = position(scores.minimal);
      const right = position(scores.english);
      connector.style.bottom = (left + right) / 2 + "%";
      connector.style.setProperty("--rise", (left - right) / 100);
      column.append(connector);
    }
    for (const key of selected) {
      if (!scores) break;
      const result = scores[key];
      const point = document.createElement("button");
      point.type = "button";
      point.className = "scatter-point " + key;
      point.style.setProperty("--y", position(result) + "%");
      const count = Math.round(result * questionCount / 100);
      const name = model;
      const message = `${name} · ${activeDates[i]} · ${conditionNames[key]} · ${storyCount} stories · ${(result + 1e-10).toFixed(2)}% (${count}/${questionCount})`;
      point.setAttribute("aria-label", message);
      point.addEventListener("focus", () => { detail.textContent = message; });
      point.addEventListener("click", () => { detail.textContent = message; });
      column.append(point);
    }
    grid.append(column);
  });
}

function saveSettings() {
  try {
    localStorage.setItem(storageKey, JSON.stringify({
      tier, scale: scale.checked ? "log" : "linear",
      conditions: Array.from(conditions.querySelectorAll("input:checked"), input => input.value)
    }));
  } catch (_) { /* Storage can be unavailable in private browsing. */ }
}
function selectTier(value) {
  tier = value;
  tabs.forEach(tab => {
    const active = tab.dataset.tier === tier;
    tab.setAttribute("aria-selected", String(active));
    tab.tabIndex = active ? 0 : -1;
  });
  render();
  saveSettings();
}
try {
  const saved = JSON.parse(localStorage.getItem(storageKey));
  if (saved && tabs.some(tab => tab.dataset.tier === saved.tier)) tier = saved.tier;
  if (saved && ["linear", "log"].includes(saved.scale)) scale.checked = saved.scale === "log";
  if (saved && Array.isArray(saved.conditions)) {
    conditions.querySelectorAll("input").forEach(input => { input.checked = saved.conditions.includes(input.value); });
  }
} catch (_) { /* Use defaults when storage is unavailable or malformed. */ }
tabs.forEach((tab, index) => {
  tab.addEventListener("click", () => selectTier(tab.dataset.tier));
  tab.addEventListener("keydown", event => {
    if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
    event.preventDefault();
    const next = event.key === "Home" ? 0 : event.key === "End" ? tabs.length - 1
      : (index + (event.key === "ArrowRight" ? 1 : -1) + tabs.length) % tabs.length;
    tabs[next].focus();
    selectTier(tabs[next].dataset.tier);
  });
});
conditions.addEventListener("change", () => { render(); saveSettings(); });
scale.addEventListener("change", () => { render(); saveSettings(); });
tabs.forEach(tab => {
  const active = tab.dataset.tier === tier;
  tab.setAttribute("aria-selected", String(active));
  tab.tabIndex = active ? 0 : -1;
});
render();
plot.hidden = false;
