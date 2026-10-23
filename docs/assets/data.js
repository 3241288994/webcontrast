export const MAX_BYTES = 50 * 1024 * 1024;
function check(condition, message) { if (!condition) throw new Error(message); }
function text(value) { return typeof value === 'string' && value.trim().length > 0; }
export function validatePages(rows) {
  check(Array.isArray(rows) && rows.length > 0 && rows.length <= 5000, 'Expected between 1 and 5,000 page records.');
  const ids = new Set();
  rows.forEach((row, index) => {
    const prefix = `Record ${index + 1}: `;
    check(row && typeof row === 'object', prefix + 'expected an object.');
    check(text(row.id) && !ids.has(row.id), prefix + 'missing or duplicate page ID.'); ids.add(row.id);
    check(text(row.website), prefix + 'missing website.');
    check(text(row.observation), prefix + 'missing observation. Annotation-only files must first be joined to source observations.');
    check(Array.isArray(row.goals) && row.goals.length === 2 && row.goals.every(text) && row.goals[0] !== row.goals[1], prefix + 'expected two distinct goals.');
    check(Array.isArray(row.actions) && row.actions.length === 2 && row.actions.every(a => a && text(a.operation) && ['string','number'].includes(typeof a.target_bid)), prefix + 'expected two valid actions.');
    check(Array.isArray(row.correct_action_indices) && row.correct_action_indices.length === 2 && row.correct_action_indices.every(n => n === 0 || n === 1) && row.correct_action_indices[0] !== row.correct_action_indices[1], prefix + 'goals must require opposite actions.');
    check(Array.isArray(row.notes) && row.notes.length === 2 && row.notes.every((note, a) => note && note.texts && text(note.texts.phrasing1) && text(note.texts.phrasing2) && (note.action_index === undefined || note.action_index === null || note.action_index === a)), prefix + 'missing action-bound explanation versions.');
  });
  return rows;
}
export function parsePages(input) {
  const data = input.replace(/^\uFEFF/, '').trim();
  check(data.length > 0, 'The file is empty.');
  let rows;
  if (data.startsWith('[')) rows = JSON.parse(data);
  else {
    try {
      const object = JSON.parse(data);
      rows = Array.isArray(object.pages) ? object.pages : [object];
    } catch { rows = data.split(/\r?\n/).filter(line => line.trim()).map((line, i) => { try { return JSON.parse(line); } catch { throw new Error(`Invalid JSON on line ${i + 1}.`); } }); }
  }
  return validatePages(rows);
}
export async function readLocalFile(file) {
  check(file.size <= MAX_BYTES, 'File exceeds the 50 MB size limit.');
  let stream = file.stream();
  if (file.name.toLowerCase().endsWith('.gz')) {
    check(typeof DecompressionStream !== 'undefined', 'This browser cannot open gzip files. Decompress the file locally and select the JSONL version.');
    stream = stream.pipeThrough(new DecompressionStream('gzip'));
  }
  const reader = stream.getReader(); const chunks = []; let size = 0;
  try {
    while (true) {
      const {done, value} = await reader.read(); if (done) break;
      size += value.byteLength;
      if (size > MAX_BYTES) { await reader.cancel(); throw new Error('Decompressed file exceeds the 50 MB size limit.'); }
      chunks.push(value);
    }
  } finally { reader.releaseLock(); }
  return parsePages(await new Blob(chunks).text());
}
export function explanationFor(row, action, version) {
  if (version === 'none') return null;
  const key = version === 'v1' ? (action === 0 ? 'phrasing1' : 'phrasing2') : (action === 0 ? 'phrasing2' : 'phrasing1');
  return row.notes[action].texts[key];
}
