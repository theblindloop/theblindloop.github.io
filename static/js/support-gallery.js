(() => {
  const buttons = [...document.querySelectorAll('[data-support-category]')];
  function select(key) {
    if (!buttons.some(b => b.dataset.supportCategory === key)) key = buttons[0].dataset.supportCategory;
    buttons.forEach(b => b.setAttribute('aria-pressed', String(b.dataset.supportCategory === key)));
    document.querySelectorAll('.support-panel').forEach(p => p.hidden = p.id !== `support-${key}`);
  }
  buttons.forEach(b => b.addEventListener('click', () => {
    history.replaceState(null, '', '#' + b.dataset.supportCategory);
    select(b.dataset.supportCategory);
    document.querySelector('.support-panel:not([hidden])').scrollIntoView({block: 'start'});
  }));
  window.addEventListener('hashchange', () => select(location.hash.slice(1)));
  select(location.hash.slice(1));
})();
