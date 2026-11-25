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
const modelKey = plot.querySelector("#scatter-model-key");
const conditionNames = { minimal: "Conlang score", english: "English control" };

function render() {
  grid.replaceChildren();
  modelKey.replaceChildren();
  const isFour = tier === "four";
  const isResearch = tier === "research";
  const isTier4 = tier === "tier4";
  const isTier5 = tier === "tier5";
  const isExperimental = isResearch || isTier4 || isTier5;
  const series = isTier5 ? tier5Research.models.slice() : isTier4 ? tier4Research.models.slice()
    : isResearch ? tier3Research.models.slice() : null;
  if (series) series.sort((a, b) => a.releaseDate.localeCompare(b.releaseDate));
  const dense = Boolean(series && series.length > 5);
  modelKey.hidden = false;
  modelKey.classList.toggle("compact-only", !dense);
  const questionCount = isResearch ? 48 : isFour || isTier4 ? 192 : 96;
  const storyCount = isExperimental ? 48 : questionCount / 4;
  const activeModels = isExperimental ? series.map(model => model.name) : models;
  const activeShortNames = isExperimental ? series.map(model => model.shortName) : shortNames;
  const activeDates = isExperimental ? series.map(model => model.releaseDate) : releaseDates;
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
  detail.textContent = selected.length ? "Select a point to see its score and output-format details." : "Choose a reading condition to show scores.";
  note.textContent = isTier5
    ? "Rules are revealed one at a time over 8 stages; the score is the mean accuracy across all stages. Haiku ran all 48 held-out stories and Sonnet the first 8, so Sonnet's interval is wide. Results are provisional and cannot be compared directly across tiers."
    : isTier4
    ? "48 longer stories per configuration, four questions each. Scores use the final JSON array; extra preceding text is allowed. Fresh contexts; results are provisional and cannot be compared directly across tiers."
    : isResearch
    ? "Exploratory five-object grammar: 48 stories per model, one question per story. Scores use the final JSON array; extra preceding text is allowed. Sonnet high reached its output limit on 30 of 48 conlang stories, counted as incorrect. Results are preliminary and not directly comparable with earlier tiers."
    : isFour
    ? "48 four-transfer stories per model. Luna used low reasoning with a 2,048-token cap."
    : "24 reference stories per model. Luna used low reasoning with a 512-token cap.";
  plot.querySelector("#condition-description").textContent = isTier5
    ? "The conlang score is the mean accuracy over all disclosure stages, from no rules to every rule. English is a separate control. Select a point for its score."
    : isTier4
    ? "The conlang score is correct answers with no disclosed suffix meanings. English is a separate control. Select a point for its score."
    : isResearch
    ? "The conlang score is the percentage correct. English is a separate control. Select a point for its score."
    : "The conlang score is the percentage correct with minimal clues. English is a separate control. Select a point for its score.";
  plot.querySelector("#research-note").hidden = !isResearch;
  plot.querySelector("#tier4-note").hidden = !isTier4;
  plot.querySelector("#tier5-note").hidden = !isTier5;

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
    const sameDate = activeTimes.map((time, index) => time === activeTimes[i] ? index : -1).filter(index => index >= 0);
    const dateRank = sameDate.indexOf(i);
    const base = isExperimental && activeModels.length > 2 ? 35 + 40 * elapsed / span
      : isExperimental ? 25 + 50 * elapsed / span : 10 + 80 * elapsed / span;
    column.style.left = base + "%";
    if (sameDate.length > 1) {
      const spacing = sameDate.length > 2 ? 3.3 : 5;
      const offset = (dateRank - (sameDate.length - 1) / 2) * spacing;
      column.style.transform = `translateX(${offset}rem)`;
    }
    const date = document.createElement("time");
    date.className = "scatter-date";
    date.dateTime = activeDates[i];
    date.textContent = dateLabel.format(activeTimes[i]);
    if (sameDate.length > 2 && dateRank !== Math.floor(sameDate.length / 2)) date.hidden = true;
    if (dense) date.hidden = activeDates.slice(0, i).some(d => d.slice(0, 7) === activeDates[i].slice(0, 7));
    column.append(date);
    const scores = isExperimental ? series[i].scores : accuracy[tier][i];
    const label = document.createElement("span");
    label.className = "scatter-model";
    label.textContent = dense ? String(i + 1) : activeShortNames[i];
    const keyItem = document.createElement("button");
    keyItem.type = "button";
    keyItem.className = "scatter-model-entry";
    const scoreSummary = scores && selected.length
      ? selected.map(key => `${conditionNames[key]} ${(scores[key] + 1e-10).toFixed(2)}%`).join(" · ")
      : "Select a reading condition";
    keyItem.textContent = `${i + 1} · ${activeShortNames[i]} · ${activeDates[i]} · ${scoreSummary}`;
    modelKey.append(keyItem);
    if (selected.length && scores) {
      const heights = selected.map(key => position(scores[key]));
      const above = Math.max(...heights) < 87;
      const edge = above ? Math.max(...heights) : Math.min(...heights);
      const groupHeights = isExperimental ? sameDate.flatMap(index => selected.map(key => position(series[index].scores[key]))) : [];
      const groupAbove = groupHeights.length && Math.max(...groupHeights) < 87;
      const groupEdges = isExperimental ? sameDate.map(index => {
        const heights = selected.map(key => position(series[index].scores[key]));
        return groupAbove ? Math.max(...heights) : Math.min(...heights);
      }) : [];
      const clustered = groupEdges.length > 1 && Math.max(...groupEdges) - Math.min(...groupEdges) < 12;
      if (clustered && !dense) {
        const anchor = groupAbove ? Math.max(...groupEdges) : Math.min(...groupEdges);
        const offset = groupAbove ? .65 + dateRank * 1.1 : -.65 - (sameDate.length - dateRank) * 1.1;
        label.style.bottom = `calc(${anchor}% + ${offset}rem)`;
      } else {
        label.style.bottom = `calc(${edge}% + ${above ? .65 : dense ? -1.15 : -1.9}rem)`;
      }
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
      const markerNumber = document.createElement("span");
      markerNumber.className = "scatter-point-number";
      markerNumber.textContent = String(i + 1);
      markerNumber.setAttribute("aria-hidden", "true");
      point.append(markerNumber);
      point.style.setProperty("--y", position(result) + "%");
      const count = Math.round(result * questionCount / 100);
      const name = model;
      let message = `${name} · ${activeDates[i]} · ${conditionNames[key]} · ${storyCount} stories · ${(result + 1e-10).toFixed(2)}% (${count}/${questionCount})`;
      if (isTier5) {
        const item = series[i];
        const curve = item.stageCurve;
        message = `${name} · ${activeDates[i]} · ${conditionNames[key]} · ${item.stories} stories · ${result.toFixed(2)}%`;
        if (key === "minimal") {
          message += ` (95% interval ${item.interval[0].toFixed(1)}–${item.interval[1].toFixed(1)}) · ${curve[0].toFixed(1)}% with no rules, ${curve.at(-1).toFixed(1)}% with all ${curve.length - 1}`;
          if (item.refused) message += ` · ${item.refused} refused response${item.refused === 1 ? '' : 's'} scored as wrong`;
          if (item.capped) message += ` · ${item.capped} response${item.capped === 1 ? '' : 's'} hit the output cap`;
        }
      } else if (isExperimental) {
        const item = series[i];
        const strict = item.strictScores[key];
        const format = item.formatCompliance[key];
        const capped = item.capped[key];
        message += ` · Original strict score ${strict.toFixed(2)}% · Complete bare-JSON responses ${format.toFixed(2)}% (${Math.round(format * storyCount / 100)}/${storyCount})`;
        if (capped) message += ` · ${capped} response${capped === 1 ? '' : 's'} hit the output cap`;
      }
      point.setAttribute("aria-label", message);
      point.addEventListener("focus", () => { detail.textContent = message; });
      point.addEventListener("click", () => { detail.textContent = message; });
      if (key === selected[0]) keyItem.addEventListener("click", () => { detail.textContent = message; });
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
