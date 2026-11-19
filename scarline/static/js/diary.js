/* SCAR's Diary — tab buku, kartu rumus (flip), dan catatan pribadi (tambah/edit/hapus). */
(function (SC) {
  'use strict';
  var el = SC.el;
  var $ = function (id) { return document.getElementById(id); };

  /* tab */
  var tabs = document.querySelectorAll('.diary-tabs [role=tab]');
  function open(btn) {
    tabs.forEach(function (t) { var on = t === btn; t.setAttribute('aria-selected', on ? 'true' : 'false'); $(t.getAttribute('aria-controls')).classList.toggle('hidden', !on); });
    try { localStorage.setItem('scarline-diary-tab', btn.id); } catch (e) { /* abaikan */ }
  }
  tabs.forEach(function (t) {
    t.addEventListener('click', function () { open(t); SC.sfx('click'); });
    t.addEventListener('keydown', function (e) {
      var list = Array.prototype.slice.call(tabs), i = list.indexOf(t);
      if (e.key === 'ArrowRight' || e.key === 'ArrowDown') { e.preventDefault(); list[(i + 1) % list.length].focus(); open(list[(i + 1) % list.length]); }
      if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') { e.preventDefault(); list[(i - 1 + list.length) % list.length].focus(); open(list[(i - 1 + list.length) % list.length]); }
    });
  });
  try { var saved = localStorage.getItem('scarline-diary-tab'); if (saved && $(saved)) open($(saved)); } catch (e) { /* abaikan */ }

  /* kartu rumus */
  document.querySelectorAll('.flip-card').forEach(function (c) {
    c.addEventListener('click', function () { var on = c.classList.toggle('flipped'); c.setAttribute('aria-pressed', on ? 'true' : 'false'); });
  });

  /* catatan */
  var form = $('note-form');
  if (!form) return;
  var list = $('note-list'), empty = $('note-empty'), err = $('note-error'), save = $('note-save'), cancel = $('note-cancel');
  var body = $('note-body'), count = $('note-count');
  var lessonNames = {};
  form.querySelectorAll('#note-lesson option').forEach(function (o) { if (o.value) lessonNames[o.value] = o.textContent.split('· ')[1] || o.textContent; });
  function updateCount() { count.textContent = body.value.length + ' / 4000'; }
  body.addEventListener('input', updateCount);

  function reset() {
    form.reset(); form.elements.id.value = ''; updateCount();
    $('note-form-title').textContent = 'Catatan baru'; cancel.classList.add('hidden'); err.textContent = '';
  }
  cancel.addEventListener('click', reset);

  function renderNote(n) {
    var li = el('li', { class: 'note' });
    li.setAttribute('data-note', JSON.stringify({ id: n.id, title: n.title, body: n.body, lesson_slug: n.lesson_slug || '' }));
    li.appendChild(el('div', { class: 'row between' }, [el('b', { text: n.title }), el('span', { class: 'small muted', text: 'baru saja' })]));
    if (n.lesson_slug) li.appendChild(el('span', { class: 'chip chip-teal', text: lessonNames[n.lesson_slug] || '' }));
    li.appendChild(el('p', { text: n.body }));
    li.appendChild(el('div', { class: 'row' }, [el('button', { class: 'btn btn-sm', type: 'button', 'data-edit': '', text: 'Edit' }), el('button', { class: 'btn btn-sm btn-ghost', type: 'button', 'data-delete': '', text: 'Hapus' })]));
    return li;
  }
  function refreshCount() { var n = list.children.length; $('note-count-chip').textContent = n; empty.classList.toggle('hidden', n > 0); }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var data = { id: form.elements.id.value || null, title: form.elements.title.value.trim(), body: body.value, lesson_slug: form.elements.lesson_slug.value || null };
    if (!data.title) { err.textContent = 'Judul catatan wajib diisi.'; form.elements.title.focus(); return; }
    SC.busy(save, true, 'Menyimpan...');
    SC.api('/api/diary', data).then(function (r) {
      SC.busy(save, false);
      if (!r.ok) { err.textContent = r.data.error || 'Gagal menyimpan catatan.'; return; }
      var node = renderNote(r.data.note);
      var existing = data.id && list.querySelector('[data-note*="' + data.id + '"]');
      if (existing) existing.replaceWith(node); else list.insertBefore(node, list.firstChild);
      node.classList.add('flash-in');
      refreshCount(); reset();
      SC.sfx('correct');
      SC.toast('Catatan tersimpan', 'Tersimpan di akunmu dan bisa dibuka kapan saja.', 'happy');
    });
  });

  list.addEventListener('click', function (e) {
    var li = e.target.closest('.note'); if (!li) return;
    var n = JSON.parse(li.getAttribute('data-note'));
    if (e.target.closest('[data-edit]')) {
      form.elements.id.value = n.id; form.elements.title.value = n.title; body.value = n.body; form.elements.lesson_slug.value = n.lesson_slug || '';
      updateCount(); $('note-form-title').textContent = 'Edit catatan'; cancel.classList.remove('hidden');
      form.elements.title.focus(); form.scrollIntoView({ behavior: SC.reducedMotion() ? 'auto' : 'smooth', block: 'start' });
    }
    if (e.target.closest('[data-delete]')) {
      if (!confirm('Hapus catatan “' + n.title + '”?')) return;
      SC.api('/api/diary', { id: n.id, delete: true }).then(function (r) {
        if (!r.ok) { SC.toast('Gagal menghapus', r.data.error || 'Coba lagi.', 'think'); return; }
        li.remove(); refreshCount();
        if (form.elements.id.value === n.id) reset();
      });
    }
  });
})(window.SC);
