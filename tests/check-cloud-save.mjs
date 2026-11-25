import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import { DatabaseSync } from 'node:sqlite';
import worker from '../worker/index.mjs';

const html = fs.readFileSync(new URL('../dist/index.html', import.meta.url), 'utf8');
const code = html.match(/<script>([\s\S]*)<\/script>/)[1];
const db = new DatabaseSync(':memory:');
db.exec(fs.readFileSync(new URL('../drizzle/0000_kingdom_saves.sql', import.meta.url), 'utf8'));
const DB = {
  prepare: sql => ({
    bind: (...args) => ({
      first: () => db.prepare(sql).get(...args),
      run: () => ({ meta: { changes: db.prepare(sql).run(...args).changes } }),
    }),
  }),
};
const endpoint = 'https://niemeng-happy-kingdom.supplecoast4.chatgpt.site/api/save';
const key = 'niemeng-kingdom-v1';
function fetchFor(userId) {
  return (path, options = {}) => {
    const headers = new Headers(options.headers);
    if(userId==='main-user')headers.set('oai-authenticated-user-email','owner@example.test');
    if (userId) headers.set('oai-authenticated-user-id', userId);
    return worker.fetch(new Request(new URL(path, endpoint), { ...options, headers }), { DB, KINGDOM_OWNER_EMAIL:"owner@example.test" });
  };
}
function device(entries, cloud, id = 'main-user') {
  const storage = new Map(entries);
  const elements = new Map();
  const context = vm.createContext({
    window: { __KINGDOM_CLOUD__: cloud, addEventListener() {} },
    document: {
      getElementById(elementId) {
        if (!elements.has(elementId)) elements.set(elementId, { querySelector: () => null });
        return elements.get(elementId);
      },
      addEventListener() {},
    },
    localStorage: { getItem: id => storage.get(id), setItem: (id, value) => storage.set(id, value) },
    fetch: fetchFor(id), AbortSignal, setTimeout: () => 1, setInterval: () => 1,
  });
  vm.runInContext(code, context);
  return { storage, run: source => vm.runInContext(source, context) };
}
async function settled(device) {
  for (let i = 0; i < 30 && device.run('cloud.busy'); i++) await new Promise(resolve => setImmediate(resolve));
  assert.equal(device.run('cloud.busy'), false);
}

const offline = device([], false);
offline.run("state.stock.gold=300;save()");
assert.equal((await fetchFor(null)('/api/save')).status, 503);
const initial = device(offline.storage, true);
await settled(initial);
assert.equal(initial.run('cloud.revision'), 1);
const second = device([], true,'another-builder');
await settled(second);
assert.equal(second.run('state.stock.gold'), 300);
assert.equal(second.run('cloud.revision'), 1);
assert.equal((await (await fetchFor('different-user')('/api/save')).json()).save.stock.gold, 300);

initial.run("state.stock.gold=350;save()");
await initial.run('syncCloudSave()');
second.run("state.stock.gold=390;save()");
await second.run('syncCloudSave()');
assert.equal(second.run('cloud.conflict.revision'), 2);
assert.equal(second.run('state.stock.gold'), 390);
assert.equal((await (await fetchFor('main-user')('/api/save')).json()).save.stock.gold, 350);
second.run('resolveCloudChoice(false)');
assert.equal(second.run('state.stock.gold'), 350);
assert.equal(JSON.parse(second.storage.get(key+'-conflict-backup')).stock.gold, 390);

second.run("state.stock.gold=400;save()");
await second.run('syncCloudSave()');
await initial.run('syncCloudSave()');
assert.equal(initial.run('state.stock.gold'), 400);
assert.equal(initial.run('cloud.revision'), 3);

const legacyConflict = device(offline.storage, true);
await settled(legacyConflict);
assert.equal(legacyConflict.run('state.stock.gold'),400);
assert.equal((await (await fetchFor(null)('/api/save')).json()).save.stock.gold,400);
assert.equal((await fetchFor(null)('/api/save',{method:'PUT'})).status,401);
const visitor = device([], true, null);
await settled(visitor);
visitor.run("state.actorPositions={hero:10}; state.dayClock-=gameDayLength; refreshDayClock()");
const visitorDay = visitor.run('state.day');
await visitor.run('syncCloudSave()');
assert.equal(visitor.run('state.day'),visitorDay);
second.run("state.stock.gold=410;save()");
await second.run('syncCloudSave()');
await visitor.run('syncCloudSave()');
assert.equal(visitor.run('actorPosition("hero")'),10);
second.run("act('map-time-3')");
await second.run('syncCloudSave()');
await initial.run('syncCloudSave()');
assert.equal(initial.run('localGameTime().phase'),3);
db.prepare("DELETE FROM kingdom_saves WHERE user_id=?").run('shared:kingdom:v1');
db.prepare("INSERT INTO kingdom_saves VALUES (?,7,?,?)").run('main-user',initial.run('JSON.stringify(state)'),new Date().toISOString());
assert.equal((await fetchFor('another-builder')('/api/save')).status,503);
assert.equal((await (await fetchFor('main-user')('/api/save')).json()).save.stock.gold,410);
const reportDevice=device([],true);
await settled(reportDevice);
reportDevice.run("state.castle={...state.castle,report:'西翼防守失利（8 / 10），损失 10 金币。'};save()");
await reportDevice.run('syncCloudSave()');
assert.equal((await (await fetchFor(null)('/api/save')).json()).save.castle.report,'西翼防守失利（8 / 10），损失 10 金币。');
console.log('Owner migration, shared reads, multi-user saves and revision conflict protection passed');
