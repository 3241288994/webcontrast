import {element} from './common.js';
import {parsePages, readLocalFile, explanationFor} from './data.js';
const $ = query => document.querySelector(query);
let illustrations = [], pages = [], filtered = [], position = 0, goal = 0, revealed = false, isLocal = false;
const status = (message, error = false) => { $('#load-status').textContent = message; $('#load-status').classList.toggle('error', error); };
function initialize(rows, local = false) {
  pages = rows; isLocal = local; position = 0; goal = 0; revealed = false;
  $('#website-filter').replaceChildren(new Option('All collections', ''));
  [...new Set(rows.map(p => p.website))].sort().forEach(name => $('#website-filter').add(new Option(name,name)));
  $('#page-search').value = ''; $('#explanation-view').value = 'none';
  filter();
  status(local ? `${rows.length} pages loaded locally from ${new Set(rows.map(p=>p.website)).size} websites. No file contents have been uploaded. Loading does not certify provenance or quality.` : '3 original illustrations. These examples are not included in the 500-page benchmark.');
}
function filter() {
  const website = $('#website-filter').value; const term = $('#page-search').value.toLowerCase().trim();
  filtered = pages.filter(row => (!website || row.website === website) && (!term || [row.id,row.website,...row.goals].join(' ').toLowerCase().includes(term)));
  position = 0; revealed = false; render();
}
function renderIllustration(row) {
  const container = $('#illustration-view'); container.replaceChildren();
  if (!row.illustration || isLocal || !Array.isArray(row.items)) { container.hidden = true; return; }
  container.hidden = false; container.append(element('p','illustration-title',row.title));
  const grid = element('div','example-items');
  row.items.forEach(item => { const card = element('div','example-item'); card.append(element('div','product-symbol',item.symbol),element('h3','',item.name)); const facts=element('ul'); item.facts.forEach(fact=>facts.append(element('li','',fact))); card.append(facts); grid.append(card); });
  container.append(grid);
}
function render() {
  $('#empty-state').hidden = filtered.length > 0; $('#page-view').hidden = filtered.length === 0;
  $('#page-counter').textContent = filtered.length ? `${position+1} / ${filtered.length}` : '0 / 0';
  $('#prev-page').disabled = position === 0; $('#next-page').disabled = position >= filtered.length-1;
  if (!filtered.length) return;
  const row = filtered[position]; const version = $('#explanation-view').value;
  $('#page-origin').textContent = isLocal ? 'LOCAL FILE' : 'ILLUSTRATION';
  $('#page-id').textContent = row.id; $('#page-category').textContent = `${row.website} · ${row.category || 'Paired goals'}`;
  document.querySelectorAll('[data-goal]').forEach(button => button.setAttribute('aria-pressed', String(Number(button.dataset.goal) === goal)));
  $('#goal-text').textContent = row.goals[goal];
  $('#observation-view').textContent = row.observation;
  renderIllustration(row);
  $('#observation-view').hidden = Boolean(row.illustration && !isLocal);
  $('#version-help').textContent = version === 'none' ? 'Only the page, goal, and actions are shown.' : version === 'v1' ? 'A: phrasing 1 · B: phrasing 2. Each explanation describes its own action.' : 'A: phrasing 2 · B: phrasing 1. The page, goal, actions, and correct answer are unchanged.';
  $('#candidates').replaceChildren();
  row.actions.forEach((action, i) => {
    const card = element('article','candidate-card');
    card.classList.toggle('correct', revealed && row.correct_action_indices[goal] === i);
    const heading = element('h3'); heading.append(element('span','candidate-letter',i===0?'A':'B'),document.createTextNode(action.label || `Candidate ${i===0?'A':'B'}`));
    card.append(heading,element('code','',`${action.operation}(${JSON.stringify(String(action.target_bid))}${action.value === undefined || action.value === null ? '' : ', '+JSON.stringify(action.value)})`));
    const explanation = explanationFor(row,i,version);
    if (explanation !== null) { const p=element('p'); p.append(element('strong','','Explanation'),document.createTextNode(explanation)); card.append(p); }
    $('#candidates').append(card);
  });
  $('#answer-panel').hidden = !revealed; $('#reveal-answer').textContent = revealed ? 'Hide the correct action' : 'Reveal the correct action';
  $('#answer-panel').replaceChildren();
  if (revealed) {
    const correct = row.correct_action_indices[goal] === 0 ? 'A':'B';
    $('#answer-panel').append(element('strong','',`Goal ${goal+1}: action ${correct}`));
    const reason = !isLocal && row.answer_reasons ? row.answer_reasons[goal] : 'This is the dataset label, not a model prediction. Switching only explanation versions leaves it unchanged.';
    $('#answer-panel').append(element('p','',reason));
  }
}
$('#website-filter').addEventListener('change',filter); $('#page-search').addEventListener('input',filter);
$('#prev-page').addEventListener('click',()=>{position--;revealed=false;render();});
$('#next-page').addEventListener('click',()=>{position++;revealed=false;render();});
$('#explanation-view').addEventListener('change',render);
document.querySelectorAll('[data-goal]').forEach(button=>button.addEventListener('click',()=>{goal=Number(button.dataset.goal);render();}));
$('#reveal-answer').addEventListener('click',()=>{revealed=!revealed;render();});
$('#reset-data').addEventListener('click',()=>{ if(illustrations.length) initialize(illustrations); $('#local-file').value=''; });
$('#local-file').addEventListener('change',async event=>{
  const file=event.target.files[0]; if(!file)return;
  status('Reading and checking the file in your browser…');
  try { initialize(await readLocalFile(file),true); } catch(error) { status(`Could not load the file: ${error.message} Your previous data is unchanged.`,true); }
  finally { event.target.value=''; }
});
try { const response=await fetch(new URL('../data/illustrations.json',import.meta.url)); if(!response.ok)throw new Error('Illustration file unavailable.'); illustrations=parsePages(await response.text()); initialize(illustrations); }
catch(error) { status(`Could not load illustrations: ${error.message} Use a local HTTP server or the published website, not a file:// URL.`,true); }
