// Draw the Tier 5 accuracy-by-stage line chart from tier5-results.js.
const ladder = document.querySelector("#tier5-ladder");
if (ladder && typeof tier5Research !== "undefined") {
  const svgNS = "http://www.w3.org/2000/svg";
  const models = tier5Research.models;
  const stages = tier5Research.stages;
  // Slot follows the model's position in the data, never its rank.
  const slots = ["series-1", "series-2", "series-3", "series-4"];
  const canvas = ladder.querySelector(".ladder-canvas");
  const tip = ladder.querySelector(".ladder-tip");
  const stageName = stage => stage === 0 ? "No rules" : `${stage} rule${stage === 1 ? "" : "s"}`;
  const columns = [
    ...Array.from({ length: stages }, (_, stage) => ({
      key: String(stage), name: stageName(stage), value: m => m.stageCurve[stage], at: stage })),
    { key: "english", name: "English control", value: m => m.scores.english, at: stages + 0.4 },
  ];

  const legend = ladder.querySelector(".legend");
  models.forEach((model, i) => {
    const entry = document.createElement("span");
    entry.className = slots[i];
    entry.append(document.createElement("i"), `${model.shortName} · ${model.stories} stories`);
    legend.append(entry);
  });

  const table = ladder.querySelector(".ladder-table table");
  const head = table.createTHead().insertRow();
  ["Stage", ...models.map(m => m.shortName)].forEach(text => {
    const cell = document.createElement("th");
    cell.scope = "col";
    cell.textContent = text;
    head.append(cell);
  });
  const body = table.createTBody();
  for (const column of columns) {
    const row = body.insertRow();
    const label = document.createElement("th");
    label.scope = "row";
    label.textContent = column.name;
    row.append(label);
    models.forEach(model => { row.insertCell().textContent = column.value(model).toFixed(1) + "%"; });
  }

  const node = (name, attrs, parent) => {
    const element = document.createElementNS(svgNS, name);
    for (const [key, value] of Object.entries(attrs)) element.setAttribute(key, value);
    parent.append(element);
    return element;
  };

  let drawnWidth = 0;
  function draw() {
    const width = canvas.clientWidth;
    if (!width || width === drawnWidth) return;
    drawnWidth = width;
    const narrow = width < 420;
    const height = Math.round(Math.min(340, Math.max(250, width * 0.52)));
    const margin = { top: 14, right: 14, bottom: 48, left: 38 };
    const plotW = width - margin.left - margin.right;
    const plotH = height - margin.top - margin.bottom;
    const last = columns.at(-1).at;
    const x = at => margin.left + 10 + (plotW - 20) * at / last;
    const y = value => margin.top + plotH * (1 - value / 100);
    canvas.querySelector("svg")?.remove();
    const svg = node("svg", { width, height, viewBox: `0 0 ${width} ${height}`, role: "group",
                              "aria-label": "Accuracy by number of rules revealed" }, canvas);
    canvas.prepend(svg);

    for (const value of [0, 25, 50, 75, 100]) {
      node("line", { class: "ladder-grid", x1: margin.left, x2: width - margin.right,
                     y1: y(value), y2: y(value) }, svg);
      node("text", { class: "ladder-tick", x: margin.left - 6, y: y(value), "text-anchor": "end",
                     "dominant-baseline": "middle" }, svg).textContent = value + "%";
    }
    const split = (x(stages - 1) + x(last)) / 2;
    node("line", { class: "ladder-split", x1: split, x2: split, y1: margin.top,
                   y2: margin.top + plotH }, svg);
    for (const column of columns) {
      const label = column.key === "english" ? (narrow ? "Eng." : "English") : column.key;
      node("text", { class: "ladder-tick", x: x(column.at), y: margin.top + plotH + 16,
                     "text-anchor": "middle" }, svg).textContent = label;
    }
    node("text", { class: "ladder-axis", x: (margin.left + x(stages - 1)) / 2, y: height - 6,
                   "text-anchor": "middle" }, svg).textContent = "Rules revealed";

    const crosshair = node("line", { class: "ladder-cross", y1: margin.top, y2: margin.top + plotH,
                                     visibility: "hidden" }, svg);
    models.forEach((model, i) => {
      const group = node("g", { class: "ladder-series " + slots[i] }, svg);
      const points = model.stageCurve.map((v, stage) => `${x(stage)},${y(v)}`).join(" ");
      node("polyline", { class: "ladder-line", points }, group);
      model.stageCurve.forEach((v, stage) => node("circle", { class: "ladder-dot", cx: x(stage),
                                                             cy: y(v), r: 4.5 }, group));
      const english = model.scores.english;
      const offset = (i - (models.length - 1) / 2) * 12;
      node("rect", { class: "ladder-dot", x: x(last) + offset - 4.5, y: y(english) - 4.5,
                     width: 9, height: 9, rx: 1.5 }, group);
    });

    // Direct labels sit under each line's first point when they cannot collide.
    const starts = models.map(m => y(m.stageCurve[0]));
    const apart = starts.every((a, i) => starts.every((b, j) => i === j || Math.abs(a - b) > 22));
    if (apart) {
      models.forEach((model, i) => {
        node("text", { class: "ladder-label", x: x(0) + 8, y: starts[i] + 17 }, svg)
          .textContent = model.shortName;
      });
    }

    const columnWidth = (x(1) - x(0));
    for (const column of columns) {
      const values = models.map((model, i) => ({ model, slot: slots[i], value: column.value(model) }));
      const summary = values.map(v => `${v.model.shortName} ${v.value.toFixed(1)}%`).join(", ");
      const hit = node("rect", { class: "ladder-hit", x: x(column.at) - columnWidth / 2,
                                 y: margin.top, width: columnWidth, height: plotH, tabindex: 0,
                                 "aria-label": `${column.name}: ${summary}` }, svg);
      const show = () => {
        crosshair.setAttribute("x1", x(column.at));
        crosshair.setAttribute("x2", x(column.at));
        crosshair.setAttribute("visibility", "visible");
        tip.replaceChildren();
        const title = document.createElement("strong");
        title.textContent = column.name;
        tip.append(title);
        for (const v of values.slice().sort((a, b) => b.value - a.value)) {
          const line = document.createElement("span");
          line.className = v.slot;
          line.append(document.createElement("i"), `${v.model.shortName} ${v.value.toFixed(1)}%`);
          tip.append(line);
        }
        tip.hidden = false;
        const left = x(column.at);
        const flip = left > width * 0.6;
        tip.style.left = left + "px";
        tip.style.transform = flip ? "translateX(calc(-100% - 12px))" : "translateX(12px)";
      };
      const hide = () => { crosshair.setAttribute("visibility", "hidden"); tip.hidden = true; };
      hit.addEventListener("pointerenter", show);
      hit.addEventListener("focus", show);
      hit.addEventListener("pointerleave", hide);
      hit.addEventListener("blur", hide);
    }
  }

  const shared = tier5Research.paired.map(m => `${m.shortName} ${m.minimal.toFixed(1)}%`).join(", ");
  const refusals = models.filter(m => m.refused).map(m => `${m.shortName} refused ${m.refused}`);
  let text = `Models ran different numbers of stories. Overall scores on the first ${tier5Research.pairedStories} stories, which every model ran: ${shared}.`;
  if (refusals.length) text += ` Refused responses count as wrong (${refusals.join(", ")}).`;
  ladder.querySelector("#tier5-paired").textContent = text;
  ladder.hidden = false;
  draw();
  if ("ResizeObserver" in window) new ResizeObserver(draw).observe(canvas);
}
