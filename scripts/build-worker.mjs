import { mkdir, readFile, writeFile } from 'node:fs/promises';

const root = new URL('../', import.meta.url);
const html = await readFile(new URL('dist/index.html', root), 'utf8');
const browser = html.replace('<script>', '<script>window.__KINGDOM_CLOUD__=true;\n');
const worker = await readFile(new URL('worker/index.mjs', root), 'utf8');
await mkdir(new URL('dist/server/', root), { recursive: true });
await writeFile(new URL('dist/server/index.js', root), 'const GAME_HTML = ' + JSON.stringify(browser) + ';\n' + worker);
