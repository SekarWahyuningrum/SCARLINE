/* SCAR AI Tutor — panel melayang (tombol "Tanya SCAR") dan halaman penuh /tutor.
 * Pertanyaan dikirim ke server (/api/tutor); kunci API tidak pernah ada di browser. */
(function (SC) {
  'use strict';
  var el = SC.el;
  var KEY = 'scarline-tutor-chat';
  var MODES = [
    { key: 'tanya', label: 'Tanya konsep', icon: '💬' },
    { key: 'petunjuk', label: 'Minta petunjuk', icon: '💡' },
    { key: 'koreksi', label: 'Koreksi jawabanku', icon: '✔' },
    { key: 'latihan', label: 'Latihan tambahan', icon: '✎' },
    { key: 'ulang', label: 'Ulang materi', icon: '↻' },
    { key: 'motivasi', label: 'Motivasi', icon: '★' }
  ];
  var STARTERS = ['Apa itu gradien?', 'Persamaan garis melalui (1, 2) dan (3, 6)', 'Apa syarat dua garis tegak lurus?', 'y = 2x − 4, di mana titik potongnya?'];

  function load() { try { return JSON.parse(sessionStorage.getItem(KEY) || '[]'); } catch (e) { return []; } }
  function save(h) { try { sessionStorage.setItem(KEY, JSON.stringify(h.slice(-20))); } catch (e) { /* abaikan */ } }

  /** Ubah teks jawaban menjadi HTML aman: paragraf, daftar bernomor, **tebal**. */
  function format(text) {
    var safe = SC.esc(text).replace(/\*\*(.+?)\*\*/g, '<b>$1</b>');
    var lines = safe.split(/\n/), out = [], list = null;
    lines.forEach(function (ln) {
      var m = ln.match(/^\s*(\d+)[.)]\s+(.*)$/), b = ln.match(/^\s*[-•]\s+(.*)$/);
      if (m || b) {
        var tag = m ? 'ol' : 'ul';
        if (!list || list.tag !== tag) { if (list) out.push('</' + list.tag + '>'); list = { tag: tag }; out.push('<' + tag + '>'); }
        out.push('<li>' + (m ? m[2] : b[1]) + '</li>');
      } else {
        if (list) { out.push('</' + list.tag + '>'); list = null; }
        if (ln.trim()) out.push('<p>' + ln + '</p>');
      }
    });
    if (list) out.push('</' + list.tag + '>');
    return out.join('');
  }

  function Chat(host, opts) {
    opts = opts || {};
    var history = load();
    var mode = 'tanya';
    var context = opts.context || '';
    host.classList.add('tutor');
    var head = el('div', { class: 'tutor-head' }, [SC.scarSvg('explain', 46), el('div', {}, [el('b', { text: 'SCAR AI Tutor' }), el('small', { text: 'Tutor persamaan garis lurus' })])]);
    var clear = el('button', { class: 'icon-link', type: 'button', title: 'Mulai percakapan baru', 'aria-label': 'Mulai percakapan baru', text: '↺' });
    head.appendChild(clear);
    if (opts.onClose) { var x = el('button', { class: 'icon-link', type: 'button', 'aria-label': 'Tutup tutor', text: '×' }); x.addEventListener('click', opts.onClose); head.appendChild(x); }
    var log = el('div', { class: 'tutor-log', 'aria-live': 'polite' });
    var modes = el('div', { class: 'tutor-modes', role: 'radiogroup', 'aria-label': 'Jenis bantuan' });
    MODES.forEach(function (m) {
      var b = el('button', { type: 'button', role: 'radio', 'aria-checked': m.key === mode ? 'true' : 'false', class: 'mode-chip' + (m.key === mode ? ' on' : ''), text: m.icon + ' ' + m.label });
      b.addEventListener('click', function () {
        mode = m.key;
        modes.querySelectorAll('button').forEach(function (o) { o.classList.remove('on'); o.setAttribute('aria-checked', 'false'); });
        b.classList.add('on'); b.setAttribute('aria-checked', 'true');
        if (m.key === 'latihan' || m.key === 'motivasi') send(m.key === 'latihan' ? 'Beri aku latihan soal tambahan' + (context ? ' tentang ' + context : '') : 'Aku butuh semangat belajar');
        else input.focus();
      });
      modes.appendChild(b);
    });
    var form = el('form', { class: 'tutor-form' });
    var input = el('textarea', { rows: '2', maxlength: '1500', placeholder: 'Tulis pertanyaan atau jawabanmu… (Enter untuk kirim)', 'aria-label': 'Pertanyaan untuk SCAR' });
    var sendBtn = el('button', { class: 'btn btn-primary', type: 'submit', 'aria-label': 'Kirim', html: '➤' });
    form.appendChild(input); form.appendChild(sendBtn);
    host.appendChild(head); host.appendChild(log); host.appendChild(modes); host.appendChild(form);

    function bubble(role, text, extra) {
      var row = el('div', { class: 'msg ' + role });
      if (role === 'assistant') row.appendChild(SC.scarSvg('happy', 34));
      var b = el('div', { class: 'msg-b', html: role === 'assistant' ? format(text) : SC.esc(text).replace(/\n/g, '<br>') });
      if (extra && extra.practice) {
        var p = extra.practice;
        b.appendChild(el('details', { class: 'practice' }, [el('summary', { text: 'Lihat petunjuk & pembahasan' }),
          p.hint ? el('p', { html: '<b>Petunjuk:</b> ' + SC.esc(p.hint) }) : null,
          el('p', { html: '<b>Jawaban:</b> ' + SC.esc(p.answer) }), el('p', { html: '<b>Pembahasan:</b> ' + SC.esc(p.explain) })]));
      }
      if (extra && extra.notice) b.appendChild(el('p', { class: 'small muted', text: extra.notice }));
      if (extra && extra.engine === 'basic' && !extra.notice) b.appendChild(el('p', { class: 'engine-tag', text: 'Mode tutor dasar' }));
      row.appendChild(b);
      log.appendChild(row);
      log.scrollTop = log.scrollHeight;
      return row;
    }
    function welcome() {
      log.innerHTML = '';
      bubble('assistant', 'Halo! Aku SCAR, tutor matematikamu. Tanyakan apa saja tentang persamaan garis lurus — konsep, rumus, contoh soal, atau kirim jawabanmu untuk kukoreksi.' + (context ? '\n\nKamu sedang mempelajari: ' + context + '.' : ''));
      var sug = el('div', { class: 'starters' });
      STARTERS.forEach(function (s) { var b = el('button', { type: 'button', class: 'starter', text: s }); b.addEventListener('click', function () { send(s); }); sug.appendChild(b); });
      log.appendChild(sug);
    }
    function restore() {
      if (!history.length) return welcome();
      log.innerHTML = '';
      history.forEach(function (m) { bubble(m.role, m.content, m.extra); });
    }
    var busy = false;
    function send(text) {
      text = (text || input.value).trim();
      if (!text || busy) return;
      busy = true;
      var starters = log.querySelector('.starters'); if (starters) starters.remove();
      bubble('user', text);
      input.value = '';
      var wait = el('div', { class: 'msg assistant typing-dots' }, [SC.scarSvg('think', 34), el('div', { class: 'msg-b', html: '<span></span><span></span><span></span>' })]);
      log.appendChild(wait); log.scrollTop = log.scrollHeight;
      SC.api('/api/tutor', { message: text, mode: mode, context: context, history: history.map(function (m) { return { role: m.role, content: m.content }; }) }).then(function (r) {
        wait.remove(); busy = false;
        if (!r.ok) { bubble('assistant', r.data.error || 'Maaf, SCAR sedang tidak bisa menjawab. Coba lagi sebentar lagi, ya!'); return; }
        history.push({ role: 'user', content: text });
        history.push({ role: 'assistant', content: r.data.reply, extra: { practice: r.data.practice, engine: r.data.engine, notice: r.data.notice } });
        save(history);
        bubble('assistant', r.data.reply, { practice: r.data.practice, engine: r.data.engine, notice: r.data.notice });
        SC.sfx('click');
      });
    }
    form.addEventListener('submit', function (e) { e.preventDefault(); send(); });
    input.addEventListener('keydown', function (e) { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } });
    clear.addEventListener('click', function () { history = []; save(history); welcome(); });
    restore();
    return { focus: function () { input.focus(); }, setContext: function (c) { context = c || context; }, ask: send };
  }
  SC.TutorChat = Chat;

  // Halaman penuh /tutor
  var page = document.getElementById('tutor-page');
  if (page) { var chat = Chat(page, { context: page.getAttribute('data-context') || '' }); chat.focus(); }

  // Panel melayang
  var drawer = null, chatD = null;
  function openDrawer(ctx) {
    if (!drawer) {
      drawer = el('aside', { class: 'tutor-drawer', role: 'dialog', 'aria-label': 'SCAR AI Tutor' });
      document.body.appendChild(drawer);
      chatD = Chat(drawer, { context: ctx, onClose: closeDrawer });
    } else if (ctx) chatD.setContext(ctx);
    drawer.classList.add('open');
    document.body.classList.add('tutor-open');
    setTimeout(function () { chatD.focus(); }, 60);
  }
  function closeDrawer() { if (drawer) drawer.classList.remove('open'); document.body.classList.remove('tutor-open'); var f = document.querySelector('.fab'); if (f) f.focus(); }
  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-open-tutor]');
    if (!b) return;
    var ctx = b.getAttribute('data-tutor-context') || (document.querySelector('h1') ? document.querySelector('h1').textContent.trim().slice(0, 120) : '');
    if (drawer && drawer.classList.contains('open') && b.classList.contains('fab')) closeDrawer(); else openDrawer(ctx);
  });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && drawer && drawer.classList.contains('open')) closeDrawer(); });
})(window.SC);
