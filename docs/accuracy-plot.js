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
    null,
    {
      "minimal": 100 * 76 / 192,
      "english": 100 * 143 / 192
    },
    null,
    {
      "minimal": 100,
      "english": 100 * 191 / 192
    }
  ]
};

const models = ["GPT-4o mini", "GPT-4.1 mini", "GPT-5.4 nano", "GPT-6 Luna"];
const shortNames = ["4o mini", "4.1 mini", "5.4 nano", "Luna"];
const plot = document.querySelector("#accuracy-overview");
const tier = document.querySelector("#plot-tier");
const condition = document.querySelector("#plot-condition");
const grid = plot.querySelector(".scatter-grid");
const detail = plot.querySelector(".scatter-detail");
const note = plot.querySelector("#scatter-note");
const legend = plot.querySelector(".scatter-key");
const conditionNames = { minimal: "Minimal clues", english: "English" };

function render() {
  grid.replaceChildren();
  const isFour = tier.value === "four";
  const questionCount = isFour ? 192 : 96;
  const storyCount = questionCount / 4;
  const both = condition.value === "both";
  const selected = both ? Object.keys(conditionNames) : [condition.value];
  grid.classList.toggle("paired", both);
  for (const key of Object.keys(conditionNames)) {
    legend.querySelector("." + key).hidden = !selected.includes(key);
  }
  detail.textContent = "Select a point to see the exact score.";
  note.textContent = isFour
    ? "48 four-transfer stories per model. Luna used low reasoning with a 2,048-token cap. Empty columns indicate no published run."
    : "24 reference stories per model. Luna used low reasoning with a 512-token cap.";

  for (const value of [0, 25, 50, 75, 100]) {
    const tick = document.createElement("div");
    tick.className = "scatter-tick";
    tick.setAttribute("aria-hidden", "true");
    tick.style.setProperty("--y", value + "%");
    const label = document.createElement("span");
    label.textContent = value + "%";
    tick.append(label);
    grid.append(tick);
  }

  models.forEach((model, i) => {
    const column = document.createElement("div");
    column.className = "scatter-column";
    const label = document.createElement("span");
    label.className = "scatter-model";
    label.textContent = shortNames[i];
    column.append(label);
    const scores = accuracy[tier.value][i];
    if (scores && both) {
      const connector = document.createElement("span");
      connector.className = "scatter-connector";
      connector.setAttribute("aria-hidden", "true");
      connector.style.bottom = Math.min(scores.minimal, scores.english) + "%";
      connector.style.height = Math.abs(scores.minimal - scores.english) + "%";
      column.append(connector);
    }
    for (const key of selected) {
      if (!scores) break;
      const result = scores[key];
      const point = document.createElement("button");
      point.type = "button";
      point.className = "scatter-point " + key;
      point.style.setProperty("--y", result + "%");
      const count = Math.round(result * questionCount / 100);
      const name = i === 3 ? model + " (low)" : model;
      const message = `${name} · ${conditionNames[key]} · ${storyCount} stories · ${(result + 1e-10).toFixed(2)}% (${count}/${questionCount})`;
      point.setAttribute("aria-label", message);
      point.addEventListener("focus", () => { detail.textContent = message; });
      point.addEventListener("click", () => { detail.textContent = message; });
      column.append(point);
    }
    grid.append(column);
  });
}

tier.addEventListener("change", render);
condition.addEventListener("change", render);
render();
plot.hidden = false;
