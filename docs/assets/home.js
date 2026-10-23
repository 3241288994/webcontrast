const controls = [...document.querySelectorAll('[data-hero-goal]')];
function selectGoal(goal) {
  controls.forEach(button => button.setAttribute('aria-pressed', String(Number(button.dataset.heroGoal) === goal)));
  document.querySelectorAll('[data-hero-action]').forEach(card => card.classList.toggle('active', Number(card.dataset.heroAction) === goal));
  document.querySelector('#hero-outcome').textContent = goal === 0
    ? 'The 420 g daypack is lighter. Action A fits this goal.'
    : 'The 24 L trail pack is larger. The same page now calls for action B.';
}
controls.forEach(button => button.addEventListener('click', () => selectGoal(Number(button.dataset.heroGoal))));
selectGoal(0);
