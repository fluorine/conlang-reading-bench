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
const tabs = ['two', 'four', 'research'].map(tier => Object.assign(new Element(), { dataset: { tier } }));
const checks = ['minimal', 'english'].map(value => Object.assign(new Element(), { value, checked: true }));
const conditions = new Element();
conditions.querySelectorAll = selector => selector === 'input:checked' ? checks.filter(c => c.checked) : checks;
const scale = Object.assign(new Element(), { checked: false });
const grid = new Element();
const detail = new Element();
const note = new Element();
const keyItems = { '.minimal': new Element(), '.english': new Element() };
const key = new Element(); key.querySelector = selector => keyItems[selector];
const inner = { '.scatter-grid': grid, '.scatter-detail': detail, '#scatter-note': note,
                '.scatter-key': key, '#scatter-label': new Element(),
                '#condition-description': new Element(), '#research-note': new Element() };
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
vm.runInContext(fs.readFileSync('docs/accuracy-plot.js', 'utf8'), context);
assert.equal(plot.hidden, false);
assert.equal(tabs[2].attrs['aria-selected'], 'true');
let columns = () => grid.children.filter(child => child.className === 'scatter-column');
const researchModelCount = vm.runInContext('tier3Research.models.length', context);
assert.equal(columns().length, researchModelCount);
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
vm.runInContext(fs.readFileSync('docs/accuracy-plot.js', 'utf8'), reloaded);
assert.equal(tabs[0].attrs['aria-selected'], 'true');
assert.equal(scale.checked, true);
assert.equal(checks[1].checked, false);
console.log('Plot tabs, conditions, scale, and saved settings passed.');
