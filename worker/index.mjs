const MAX_SAVE_BYTES = 512 * 1024;

function json(body, status = 200) {
  return Response.json(body, { status, headers: { 'Cache-Control': 'no-store' } });
}

function validSave(save) {
  return save && typeof save === 'object' &&
    Number.isSafeInteger(save.day) && save.day > 0 &&
    Number.isFinite(save.dayClock) && Number.isFinite(save.climateEpoch) &&
    save.tiles && save.stock && save.people?.hero && save.people?.advisor &&
    save.labor && save.total && save.events && save.crops && save.clearedTerrain &&
    Object.values(save.stock).every(amount => Number.isFinite(amount) && amount >= 0);
}

function safeFields(value, depth = 0) {
  if (depth > 24) return false;
  if (typeof value === 'string') return /^[\p{L}\p{N} _.,:！!，。·：；、？（）()/+-]*$/u.test(value);
  if (!value || typeof value !== 'object') return true;
  return Object.entries(value).every(([key, field]) =>
    /^[a-zA-Z0-9_-]+$/.test(key) && !['__proto__','constructor','prototype'].includes(key) && safeFields(field, depth + 1));
}

async function readSave(db, userId) {
  const row = await db.prepare('SELECT revision, payload, updated_at FROM kingdom_saves WHERE user_id = ?').bind(userId).first();
  return row ? { revision: row.revision, save: JSON.parse(row.payload), updatedAt: row.updated_at } :
    { revision: 0, save: null, updatedAt: null };
}

async function saveRequest(request, env) {
  const viewer = request.headers.get('oai-authenticated-user-id');
  const owner = !!viewer && !!env.KINGDOM_OWNER_EMAIL &&
    request.headers.get('oai-authenticated-user-email')?.toLowerCase() === env.KINGDOM_OWNER_EMAIL.toLowerCase();
  const userId = 'shared:kingdom:v1';
  if (!env.DB) return json({ error: 'storage_unavailable' }, 503);
  if (request.method === 'GET') {
    let shared = await readSave(env.DB, userId);
    if (!shared.save && owner) {
      await env.DB.prepare('INSERT OR IGNORE INTO kingdom_saves (user_id, revision, payload, updated_at) SELECT ?, 1, payload, updated_at FROM kingdom_saves WHERE user_id = ?').bind(userId, viewer).run();
      shared = await readSave(env.DB, userId);
    }
    if (!shared.save && !owner) return json({ error: 'awaiting_owner' }, 503);
    return json({ ...shared, canWrite: !!viewer });
  }
  if (!viewer) return json({ error: 'sign_in_required' }, 401);
  if (request.method !== 'PUT') return json({ error: 'method_not_allowed' }, 405);

  const origin = request.headers.get('Origin');
  if (origin && origin !== new URL(request.url).origin &&
      origin !== 'https://niemeng-happy-kingdom.supplecoast4.chatgpt.site') {
    return json({ error: 'invalid_origin' }, 403);
  }
  if (!/^application\/json(?:;|$)/i.test(request.headers.get('Content-Type') || '')) {
    return json({ error: 'json_required' }, 415);
  }
  if (Number(request.headers.get('Content-Length')) > MAX_SAVE_BYTES) {
    return json({ error: 'save_too_large' }, 413);
  }
  const bytes = await request.arrayBuffer();
  if (bytes.byteLength > MAX_SAVE_BYTES) return json({ error: 'save_too_large' }, 413);
  let body;
  try { body = JSON.parse(new TextDecoder().decode(bytes)); }
  catch { return json({ error: 'invalid_json' }, 400); }
  if (body?.world !== 'shared-v1' || !Number.isSafeInteger(body?.revision) || body.revision < 0 || !validSave(body.save)) {
    return json({ error: 'invalid_save' }, 400);
  }

  if (!body.revision && !owner) return json({ error: 'owner_initialization_required' }, 403);
  if (!safeFields(body.save)) return json({ error: 'invalid_fields' }, 400);
  const updatedAt = new Date().toISOString();
  const payload = JSON.stringify(body.save);
  const change = body.revision === 0
    ? await env.DB.prepare('INSERT OR IGNORE INTO kingdom_saves (user_id, revision, payload, updated_at) VALUES (?, 1, ?, ?)').bind(userId, payload, updatedAt).run()
    : await env.DB.prepare('UPDATE kingdom_saves SET revision = revision + 1, payload = ?, updated_at = ? WHERE user_id = ? AND revision = ?').bind(payload, updatedAt, userId, body.revision).run();

  if (change.meta.changes !== 1) return json(await readSave(env.DB, userId), 409);
  return json({ revision: body.revision + 1, updatedAt });
}

export default {
  async fetch(request, env) {
    const path = new URL(request.url).pathname;
    if (path === '/api/save') {
      try { return await saveRequest(request, env); }
      catch { return json({ error: 'storage_unavailable' }, 503); }
    }
    if ((path === '/' || path === '/index.html') && ['GET', 'HEAD'].includes(request.method)) {
      return new Response(request.method === 'HEAD' ? null : GAME_HTML, {
        headers: { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store' },
      });
    }
    return new Response('Not found', { status: 404 });
  },
};
