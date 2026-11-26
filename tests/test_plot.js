// Exercise the static plot controls without a browser or network.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

class Element {
  constructor() { this.children = []; this.dataset = {}; this.attrs = {}; this.listeners = {}; this.style = { setProperty() {} }; this.classList = { toggle() {} }; }
  append(child) { this.children.push(child); }
  replaceChildren() { this.children = []; }
  setAttribute(key, value) { this.attrs[key] = value; }
  addEventListener(type, handler) { this.listeners[type] = handler; }
  focus() {}
}
const tabs = ['two', 'four', 'research', 'tier4', 'tier5'].map(tier => Object.assign(new Element(), { dataset: { tier } }));
const checks = ['minimal', 'english'].map(value => Object.assign(new Element(), { value, checked: true }));
const conditions = new Element();
conditions.querySelectorAll = selector => selector === 'input:checked' ? checks.filter(c => c.checked) : checks;
const scale = Object.assign(new Element(), { checked: false });
const grid = new Element();
const detail = new Element();
const note = new Element();
const keyItems = { '.minimal': new Element(), '.english': new Element() };
const key = new Element(); key.querySelector = selector => keyItems[selector];
const modelKey = new Element();
const inner = { '.scatter-grid': grid, '.scatter-detail': detail, '#scatter-note': note,
                '.scatter-key': key, '#scatter-label': new Element(), '#scatter-model-key': modelKey,
                '#condition-description': new Element(), '#research-note': new Element(), '#tier4-note': new Element(), '#tier5-note': new Element() };
const plot = Object.assign(new Element(), { querySelector: selector => inner[selector], hidden: true });
const document = {
  querySelector: selector => ({ '#accuracy-overview': plot, '#plot-conditions': conditions, '#plot-scale': scale })[selector],
  querySelectorAll: () => tabs,
  createElement: () => new Element(),
};
let saved = null;
const localStorage = { getItem: () => saved, setItem: (_, value) => { saved = value; } };
const context = vm.createContext({ document, localStorage, Intl, Date, Math });
vm.runInContext(fs.readFileSync('docs/tier3-results.js', 'utf8'), context);
vm.runInContext(fs.readFileSync('docs/tier4-results.js', 'utf8'), context);
vm.runInContext(fs.readFileSync('docs/tier5-results.js', 'utf8'), context);
vm.runInContext(fs.readFileSync('docs/accuracy-plot.js', 'utf8'), context);
assert.equal(plot.hidden, false);
assert.equal(tabs[4].attrs['aria-selected'], 'true');
let columns = () => grid.children.filter(child => child.className === 'scatter-column');
assert.equal(columns().length, vm.runInContext('tier5Research.models.length', context));
assert.equal(inner['#tier5-note'].hidden, false);
assert.equal(inner['#tier4-note'].hidden, true);
assert.match(note.textContent, /Rules are revealed one at a time/);
const tier5SonnetIndex = vm.runInContext("tier5Research.models.slice().sort(capacityCompare).findIndex(m => m.name === 'Claude Sonnet 5.5 (low)')", context);
assert.match(modelKey.children[0].textContent, /Haiku/);
assert.match(modelKey.children[1].textContent, /Sonnet/);
columns()[tier5SonnetIndex].children.find(child => child.className === 'scatter-point minimal').listeners.click();
assert.match(detail.textContent, /8 stories · 83\.59% \(95% interval 73\.4–93\.0\)/);
assert.match(detail.textContent, /70\.8% with no rules, 83\.3% with all 7/);
assert.match(detail.textContent, /2 refused responses scored as wrong/);
columns()[tier5SonnetIndex].children.find(child => child.className === 'scatter-point english').listeners.click();
assert.doesNotMatch(detail.textContent, /interval/);
tabs[3].listeners.click();
assert.equal(inner['#tier5-note'].hidden, true);
assert.equal(columns().length, vm.runInContext('tier4Research.models.length', context));
assert.equal(columns()[0].children.find(child => child.className === 'scatter-point minimal').children[0].textContent, '1');
assert.match(modelKey.children[0].textContent, /^1 · /);
assert.match(note.textContent, /48 longer stories/);
assert.match(columns()[1].children.find(child => child.className === 'scatter-model').style.bottom, /91\.666/);
const tier4SonnetIndex = vm.runInContext("tier4Research.models.slice().sort(capacityCompare).findIndex(m => m.name === 'Claude Sonnet 5.5 (low)')", context);
const sonnetPoint = columns()[tier4SonnetIndex].children.find(child => child.className === 'scatter-point minimal');
sonnetPoint.listeners.click();
assert.match(detail.textContent, /66\.67%/);
assert.match(detail.textContent, /Original strict score 0\.00%/);
assert.match(detail.textContent, /Complete bare-JSON responses 0\.00%/);
checks[0].checked = false;
conditions.listeners.change();
assert.notEqual(columns()[0].children.find(child => child.className === 'scatter-model').style.bottom,
                columns()[1].children.find(child => child.className === 'scatter-model').style.bottom);
checks[0].checked = true;
conditions.listeners.change();
tabs[2].listeners.click();
assert.equal(tabs[2].attrs['aria-selected'], 'true');
const researchModelCount = vm.runInContext('tier3Research.models.length', context);
assert.equal(columns().length, researchModelCount);
const lefts = columns().map(column => parseFloat(column.style.left));
const gaps = lefts.slice(1).map((left, k) => left - lefts[k]);
assert.ok(gaps.every(gap => Math.abs(gap - gaps[0]) < 1e-9));
assert.deepEqual(columns().map(column => column.children[0].textContent), Array.from({length: researchModelCount}, (_, i) => String(i + 1)));
assert.equal(modelKey.hidden, false);
assert.equal(modelKey.children.length, researchModelCount);
assert.match(modelKey.children[0].textContent, /Conlang score .*%/);
modelKey.children[0].listeners.click();
assert.match(detail.textContent, /Conlang score/);
const sonnetHighIndex = vm.runInContext("tier3Research.models.slice().sort(capacityCompare).findIndex(m => m.name === 'Claude Sonnet 5.5 (high)')", context);
const sonnetHigh = columns()[sonnetHighIndex].children.find(child => child.className === 'scatter-point minimal');
sonnetHigh.listeners.click();
assert.match(detail.textContent, /30 responses hit the output cap/);
if (researchModelCount === 3) {
  assert.equal(columns()[0].style.transform, 'translateX(-2.5rem)');
  assert.equal(columns()[1].style.transform, 'translateX(2.5rem)');
}
if (researchModelCount === 4) {
  assert.equal(columns()[0].style.transform, 'translateX(-3.3rem)');
  assert.equal(columns()[1].style.transform, 'translateX(0rem)');
  assert.equal(columns()[2].style.transform, 'translateX(3.3rem)');
}
assert.equal(columns()[0].children.filter(child => child.className?.startsWith('scatter-point')).length, 2);
checks[1].checked = false;
conditions.listeners.change();
assert.equal(columns()[0].children.filter(child => child.className?.startsWith('scatter-point')).length, 1);
scale.checked = true;
scale.listeners.change();
assert.equal(JSON.parse(saved).scale, 'log');
assert.deepEqual(JSON.parse(saved).conditions, ['minimal']);
tabs[0].listeners.click();
assert.equal(tabs[0].attrs['aria-selected'], 'true');
assert.equal(columns().length, 4);
assert.equal(JSON.parse(saved).tier, 'two');
checks.forEach(check => { check.checked = true; });
scale.checked = false;
const reloaded = vm.createContext({ document, localStorage, Intl, Date, Math });
vm.runInContext(fs.readFileSync('docs/tier3-results.js', 'utf8'), reloaded);
vm.runInContext(fs.readFileSync('docs/tier4-results.js', 'utf8'), reloaded);
vm.runInContext(fs.readFileSync('docs/tier5-results.js', 'utf8'), reloaded);
vm.runInContext(fs.readFileSync('docs/accuracy-plot.js', 'utf8'), reloaded);
assert.equal(tabs[0].attrs['aria-selected'], 'true');
assert.equal(scale.checked, true);
assert.equal(checks[1].checked, false);
console.log('Plot tabs, conditions, scale, and saved settings passed.');
