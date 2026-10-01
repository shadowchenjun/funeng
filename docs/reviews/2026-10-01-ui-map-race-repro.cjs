// Reproduce asynchronous redraw races from the current ColdChain.vue source.
// Run: node docs/reviews/2026-10-01-ui-map-race-repro.cjs
// This is a controlled SDK stub, not a rendered AMap/browser acceptance test.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '../..');
const ts = require(path.join(root, 'frontend/node_modules/typescript'));
const source = fs.readFileSync(path.join(root, 'frontend/src/views/ColdChain.vue'), 'utf8');
const start = source.indexOf('const initTransportMap = () =>');
const end = source.indexOf('// GET /monitoring/temperature', start);
assert(start >= 0 && end > start);
const code = ts.transpileModule(source.slice(start, end) + '\nglobalThis.redraw = initTransportMap;', {compilerOptions: {target: ts.ScriptTarget.ES2020}}).outputText;
const pending = [], jobs = [], maps = [];
class MapStub {
  constructor() { this.overlays = []; maps.push(this); }
  clearMap() { this.overlays = []; }
  add(x) { this.overlays.push(x.options); }
  setFitView() {}
}
class Overlay { constructor(options) { this.options = options; } }
const context = {
  console, Date, transportMap: null,
  document: {getElementById: () => ({})},
  window: {AMap: {Map: MapStub, Marker: Overlay, Icon: Overlay, Polyline: Overlay,
    Geocoder: class {getLocation(city, cb) {pending.push({city, cb});}}}},
  nextTick: cb => {jobs.push(Promise.resolve().then(cb));},
  waitForAMap: async () => {},
  transports: {value: [
    {id: 'A', route: 'A-start-A-end', waypoints: [{name:'A-start',lng:1,lat:1},{name:'A-end',lng:2,lat:2}]},
    {id: 'B', route: 'B-start-B-end', waypoints: [{name:'B-start',lng:3,lat:3},{name:'B-end',lng:4,lat:4}]}
  ]},
  selectedTransportId: {value: 'A'}, transportData: {value: []}
};
// Actual city split uses '-', so use single-token city names.
context.transports.value[0].route = 'Alpha-Omega';
context.transports.value[1].route = 'Beta-Delta';
vm.createContext(context);
vm.runInContext(code, context);
const turn = () => new Promise(resolve => setImmediate(resolve));
async function resolveCity(city) {
  const index = pending.findIndex(x => x.city === city);
  assert(index >= 0, 'Expected geocoder request for ' + city);
  const request = pending.splice(index, 1)[0];
  request.cb('complete', {geocodes: [{location: {lng: 1, lat: 1}}]});
  await turn();
}
(async () => {
  context.redraw(); await turn();
  context.selectedTransportId.value = 'B';
  context.redraw(); await turn();
  await resolveCity('Beta'); await resolveCity('Delta');
  await resolveCity('Alpha'); await resolveCity('Omega');
  await Promise.all(jobs);
  const result = {
    selectedTransport: context.selectedTransportId.value,
    displayedTimeline: Array.from(context.transportData.value, x => x.location),
    renderedMarkers: maps[0].overlays.filter(x => x.title).map(x => x.title),
    mapInstanceCount: maps.length
  };
  assert.equal(result.selectedTransport, 'B');
  assert.deepEqual(result.displayedTimeline, ['A-start','A-end']);
  assert.equal(result.mapInstanceCount, 1);
  console.log(JSON.stringify(result, null, 2));
  console.log('Reproduced: delayed A redraw overwrites selected B timeline and mixes both routes on the reused map.');
})().catch(error => {console.error(error); process.exitCode = 1;});
