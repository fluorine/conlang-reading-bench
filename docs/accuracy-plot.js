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
  "original": [
    null,
    {
      "minimal": 35.41666666666667,
      "english": 71.875
    },
    null,
    {
      "minimal": 100,
      "english": 98.95833333333334
    }
  ],
  "fresh": [
    null,
    {
      "minimal": 43.75,
      "english": 77.08333333333334
    },
    null,
    {
      "minimal": 100,
      "english": 100
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

function render() {
  grid.replaceChildren();
  const isFour = tier.value === "four";
  const sets = isFour ? [["original", "Original stories"], ["fresh", "Fresh stories"]]
                      : [["two", "Reference stories"]];
  detail.textContent = "Select a point to see the exact score.";
  note.textContent = isFour
    ? "Circles show original stories. Squares show fresh stories. Luna used low reasoning with a 2,048-token cap. Empty columns indicate no published run."
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
    sets.forEach(([key, title], j) => {
      const result = accuracy[key][i]?.[condition.value];
      if (result === undefined) return;
      const point = document.createElement("button");
      point.type = "button";
      point.className = key === "fresh" ? "scatter-point fresh" : "scatter-point";
      point.style.setProperty("--y", result + "%");
      if (isFour) point.style.setProperty("--x", j === 0 ? "30%" : "70%");
      const count = Math.round(result * 96 / 100);
      const name = i === 3 ? model + " (low)" : model;
      const message = `${name} · ${title} · ${(count / 96 * 100 + 1e-10).toFixed(2)}% (${count}/96)`;
      point.setAttribute("aria-label", message);
      point.addEventListener("focus", () => { detail.textContent = message; });
      point.addEventListener("click", () => { detail.textContent = message; });
      column.append(point);
    });
    grid.append(column);
  });
}

tier.addEventListener("change", render);
condition.addEventListener("change", render);
render();
plot.hidden = false;
