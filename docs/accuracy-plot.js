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

const models = ["GPT-4o mini", "GPT-4.1 mini", "GPT-5.4 nano", "GPT-6 Luna"];
const shortNames = ["4o mini", "4.1 mini", "5.4 nano", "Luna"];
const releaseDates = ["2024-07-18", "2025-04-14", "2026-03-17", "2026-09-22"];
const releaseTimes = releaseDates.map(date => Date.parse(date));
const dateLabel = new Intl.DateTimeFormat("en", { month: "short", year: "numeric", timeZone: "UTC" });
const plot = document.querySelector("#accuracy-overview");
const tier = document.querySelector("#plot-tier");
const conditions = document.querySelector("#plot-conditions");
const scale = document.querySelector("#plot-scale");
const grid = plot.querySelector(".scatter-grid");
const detail = plot.querySelector(".scatter-detail");
const note = plot.querySelector("#scatter-note");
const legend = plot.querySelector(".scatter-key");
const conditionNames = { minimal: "Minimal clues", english: "English control" };

function render() {
  grid.replaceChildren();
  const isFour = tier.value === "four";
  const questionCount = isFour ? 192 : 96;
  const storyCount = questionCount / 4;
  const selected = Array.from(conditions.querySelectorAll("input:checked"), input => input.value);
  const both = selected.length === 2;
  const logarithmic = scale.value === "log";
  const position = value => logarithmic ? 100 * (Math.log10(value) - 1) : value;
  const ticks = logarithmic ? [10, 20, 40, 60, 100] : [0, 25, 50, 75, 100];
  plot.querySelector("#scatter-label").textContent = logarithmic
    ? "Accuracy (% correct, log scale)" : "Accuracy (% correct)";
  grid.classList.toggle("paired", both);
  for (const key of Object.keys(conditionNames)) {
    legend.querySelector("." + key).hidden = !selected.includes(key);
  }
  detail.textContent = selected.length ? "Select a point to see the exact score." : "Choose a reading condition to show scores.";
  note.textContent = isFour
    ? "48 four-transfer stories per model. Luna used low reasoning with a 2,048-token cap."
    : "24 reference stories per model. Luna used low reasoning with a 512-token cap.";

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

  models.forEach((model, i) => {
    const column = document.createElement("div");
    column.className = "scatter-column";
    const elapsed = releaseTimes[i] - releaseTimes[0];
    const span = releaseTimes.at(-1) - releaseTimes[0];
    column.style.left = (10 + 80 * elapsed / span) + "%";
    const date = document.createElement("time");
    date.className = "scatter-date";
    date.dateTime = releaseDates[i];
    date.textContent = dateLabel.format(releaseTimes[i]);
    column.append(date);
    const scores = accuracy[tier.value][i];
    const label = document.createElement("span");
    label.className = "scatter-model";
    label.textContent = shortNames[i];
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
      const name = i === 3 ? model + " (low)" : model;
      const message = `${name} · ${releaseDates[i]} · ${conditionNames[key]} · ${storyCount} stories · ${(result + 1e-10).toFixed(2)}% (${count}/${questionCount})`;
      point.setAttribute("aria-label", message);
      point.addEventListener("focus", () => { detail.textContent = message; });
      point.addEventListener("click", () => { detail.textContent = message; });
      column.append(point);
    }
    grid.append(column);
  });
}

tier.addEventListener("change", render);
conditions.addEventListener("change", render);
scale.addEventListener("change", render);
render();
plot.hidden = false;
