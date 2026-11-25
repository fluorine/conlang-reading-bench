// Draw the Tier 5 accuracy-by-stage bars from tier5-results.js.
const ladder = document.querySelector("#tier5-ladder");
if (ladder && typeof tier5Research !== "undefined") {
  const classes = ["first", "second", "third", "fourth"];
  const models = tier5Research.models;
  const legend = ladder.querySelector(".legend");
  const plot = ladder.querySelector(".plot");
  models.forEach((model, i) => {
    const entry = document.createElement("span");
    entry.className = classes[i];
    entry.append(document.createElement("i"), `${model.shortName} · ${model.stories} stories`);
    legend.append(entry);
  });
  const rows = Array.from({ length: tier5Research.stages }, (_, stage) => ({
    label: stage === 0 ? "No rules" : `${stage} rule${stage === 1 ? "" : "s"}`,
    value: model => model.stageCurve[stage], control: false,
  }));
  rows.push({ label: "English control", value: model => model.scores.english, control: true });
  for (const row of rows) {
    const wrapper = document.createElement("div");
    wrapper.className = "chart-row" + (row.control ? " control" : "");
    const term = document.createElement("dt");
    term.textContent = row.label;
    const cell = document.createElement("dd");
    models.forEach((model, i) => {
      const value = row.value(model);
      const series = document.createElement("div");
      series.className = "series " + classes[i];
      const track = document.createElement("span");
      track.className = "track";
      track.setAttribute("aria-hidden", "true");
      const bar = document.createElement("i");
      bar.style.width = value + "%";
      track.append(bar);
      const number = document.createElement("span");
      number.className = "number";
      const name = document.createElement("span");
      name.className = "sr-only";
      name.textContent = model.name + " ";
      number.append(name, value.toFixed(1) + "%");
      series.append(track, number);
      cell.append(series);
    });
    wrapper.append(term, cell);
    plot.append(wrapper);
  }
  const paired = tier5Research.paired.map(m => `${m.shortName} ${m.minimal.toFixed(1)}%`).join(", ");
  const refusals = models.filter(m => m.refused).map(m => `${m.shortName} refused ${m.refused}`);
  let text = `Models ran different numbers of stories. Overall scores on the first ${tier5Research.pairedStories} stories, which every model ran: ${paired}.`;
  if (refusals.length) text += ` Refused responses count as wrong (${refusals.join(", ")}).`;
  ladder.querySelector("#tier5-paired").textContent = text;
  ladder.hidden = false;
}
