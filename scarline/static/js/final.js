/* SCARLINE Final Line Challenge — navigasi soal, timer opsional, tinjau sebelum kirim, pembahasan. */
(function (SC) {
  'use strict';
  var el = SC.el;
  var start = document.getElementById('final-start');
  if (!start) return;
  var setup = document.getElementById('final-setup');
  var mount = document.getElementById('final-run');
  var S = null;

  start.addEventListener('click', function () {
    SC.busy(start, true, 'Menyiapkan soal...');
    SC.api('/api/runs', { kind: 'final', count: +document.getElementById('final-count').value, timer: document.getElementById('final-timer').checked }).then(function (r) {
      SC.busy(start, false);
      if (!r.ok) { document.getElementById('final-error').textContent = r.data.error || 'Gagal memulai.'; return; }
      S = { run: r.data, i: 0, views: [], answers: {}, flags: {}, deadline: r.data.timer ? Date.now() + r.data.timer * 1000 : null, submitted: false };
      setup.classList.add('hidden');
      mount.classList.remove('hidden');
      build();
      window.addEventListener('beforeunload', guard);
    });
  });

  function guard(e) { if (S && !S.submitted) { e.preventDefault(); e.returnValue = ''; } }

  var top, dots, card, nav, timerEl, tId;
  function build() {
    mount.innerHTML = '';
    top = el('div', { class: 'quiz-top' });
    timerEl = el('span', { class: 'chip chip-orange', 'aria-live': 'off' });
    var prog = el('span', { class: 'chip chip-navy', id: 'final-prog' });
    top.appendChild(prog);
    if (S.deadline) top.appendChild(timerEl);
    dots = el('div', { class: 'dots', role: 'navigation', 'aria-label': 'Navigasi nomor soal' });
    card = el('div', { class: 'sheet qcard' });
    nav = el('div', { class: 'row between', style: 'margin-top:16px' });
    mount.appendChild(top);
    mount.appendChild(el('div', { class: 'ruler teal', style: 'margin-bottom:12px' }, [el('div', { class: 'fill', id: 'final-bar', style: 'width:0%' })]));
    mount.appendChild(dots);
    mount.appendChild(el('div', { style: 'height:14px' }));
    mount.appendChild(card);
    mount.appendChild(nav);
    S.run.items.forEach(function (q, i) {
      S.views[i] = SC.renderQuestion(q, { onChange: function (v) { if (v === null || v === undefined || v === '') delete S.answers[i]; else S.answers[i] = v; updateDots(); } });
    });
    show(0);
    if (S.deadline) { tick(); tId = setInterval(tick, 1000); }
  }

  function tick() {
    var left = Math.max(0, Math.round((S.deadline - Date.now()) / 1000));
    timerEl.textContent = '⏱ ' + Math.floor(left / 60) + ':' + ('0' + left % 60).slice(-2);
    if (left <= 60) timerEl.style.background = 'var(--red)';
    if (left === 0 && !S.submitted) { clearInterval(tId); SC.toast('Waktu habis!', 'Jawabanmu dikirim otomatis.', 'think'); submit(); }
  }

  function updateDots() {
    dots.innerHTML = '';
    S.run.items.forEach(function (q, i) {
      var b = el('button', { type: 'button', text: String(i + 1), class: (i === S.i ? 'now ' : '') + (S.answers[i] !== undefined ? 'ans ' : '') + (S.flags[i] ? 'flagged' : ''), 'aria-label': 'Soal ' + (i + 1) + (S.answers[i] !== undefined ? ', sudah dijawab' : ', belum dijawab') + (S.flags[i] ? ', ditandai' : '') });
      b.addEventListener('click', function () { show(i); });
      dots.appendChild(b);
    });
    var n = Object.keys(S.answers).length;
    document.getElementById('final-prog').textContent = 'Terjawab ' + n + ' / ' + S.run.total;
    document.getElementById('final-bar').style.width = (n * 100 / S.run.total) + '%';
  }

  function show(i) {
    S.i = i;
    card.innerHTML = '';
    card.appendChild(el('div', { class: 'row between' }, [el('b', { text: 'Soal ' + (i + 1) + ' dari ' + S.run.total }), flagBtn(i)]));
    card.appendChild(S.views[i].el);
    nav.innerHTML = '';
    var prev = el('button', { class: 'btn btn-sm', type: 'button', text: '← Sebelumnya', disabled: i === 0 });
    prev.addEventListener('click', function () { show(i - 1); });
    var next = el('button', { class: 'btn btn-sm btn-teal', type: 'button', text: i === S.run.total - 1 ? 'Tinjau Jawaban' : 'Berikutnya →' });
    next.addEventListener('click', function () { if (i === S.run.total - 1) review(); else show(i + 1); });
    var rev = el('button', { class: 'btn btn-sm btn-ghost', type: 'button', text: 'Periksa semua jawaban' });
    rev.addEventListener('click', review);
    nav.appendChild(prev); nav.appendChild(rev); nav.appendChild(next);
    updateDots();
  }

  function flagBtn(i) {
    var b = el('button', { class: 'btn btn-sm btn-ghost', type: 'button', text: S.flags[i] ? '★ Ditandai' : '☆ Tandai ragu-ragu' });
    b.addEventListener('click', function () { S.flags[i] = !S.flags[i]; show(i); });
    return b;
  }

  function review() {
    card.innerHTML = '';
    nav.innerHTML = '';
    var unanswered = S.run.items.map(function (q, i) { return i; }).filter(function (i) { return S.answers[i] === undefined; });
    var flagged = Object.keys(S.flags).filter(function (k) { return S.flags[k]; }).map(function (k) { return +k + 1; });
    card.appendChild(el('h3', { text: 'Tinjau sebelum mengirim' }));
    card.appendChild(el('p', { text: 'Terjawab: ' + (S.run.total - unanswered.length) + ' dari ' + S.run.total + ' soal.' }));
    if (unanswered.length) card.appendChild(el('div', { class: 'notice', text: 'Belum dijawab: nomor ' + unanswered.map(function (i) { return i + 1; }).join(', ') + '. Soal kosong dihitung salah.' }));
    if (flagged.length) card.appendChild(el('div', { class: 'notice', text: 'Ditandai ragu-ragu: nomor ' + flagged.join(', ') + '.' }));
    card.appendChild(el('p', { class: 'muted', text: 'Klik nomor soal di atas untuk kembali memeriksa. Setelah dikirim, jawaban tidak bisa diubah.' }));
    var back = el('button', { class: 'btn', type: 'button', text: 'Kembali ke soal' });
    back.addEventListener('click', function () { show(unanswered.length ? unanswered[0] : 0); });
    var send = el('button', { class: 'btn btn-primary', type: 'button', text: 'Kirim Jawaban' });
    send.addEventListener('click', function () { if (unanswered.length && !confirm('Masih ada ' + unanswered.length + ' soal kosong. Tetap kirim?')) return; submit(send); });
    nav.appendChild(back); nav.appendChild(send);
  }

  function submit(btn) {
    if (S.submitted) return;
    S.submitted = true;
    clearInterval(tId);
    if (btn) SC.busy(btn, true, 'Menilai...');
    var answers = {};
    Object.keys(S.answers).forEach(function (k) { answers[k] = S.answers[k]; });
    SC.api('/api/runs/' + S.run.run_id + '/finish', { answers: answers }).then(function (r) {
      window.removeEventListener('beforeunload', guard);
      if (!r.ok) { S.submitted = false; if (btn) SC.busy(btn, false); SC.toast('Gagal mengirim', r.data.error || 'Coba lagi.', 'think'); return; }
      result(r.data);
    });
  }

  function result(d) {
    mount.innerHTML = '';
    var again = el('a', { class: 'btn btn-primary', href: '/final', text: 'Kembali ke Final' });
    var home = el('a', { class: 'btn', href: '/dashboard', text: 'Ke Markas' });
    var panel = SC.resultPanel(d, { actions: [again, home], noXpText: 'XP evaluasi = 2 × kenaikan nilai terbaikmu. Nilai ini tidak melampaui rekor.' });
    panel.insertBefore(el('h2', { text: d.passed ? 'SELAMAT! Kamu lulus Final Line Challenge!' : 'Belum lulus — nilai minimal 70. Pelajari pembahasan di bawah, ya!' }), panel.firstChild);
    mount.appendChild(el('div', { class: 'paper' }, [panel]));
    mount.appendChild(el('h2', { text: 'Pembahasan', style: 'margin-top:28px' }));
    (d.review || []).forEach(function (rv) {
      var item = el('div', { class: 'sheet review-item ' + (rv.correct ? '' : 'no'), style: 'margin-bottom:12px' });
      item.appendChild(el('div', { class: 'row between' }, [el('b', { text: 'Soal ' + (rv.index + 1) }), el('span', { class: 'status ' + (rv.correct ? 'lulus' : 'belum-lulus'), text: rv.correct ? 'Benar' : 'Salah' })]));
      item.appendChild(el('p', { style: 'font-weight:700;margin:8px 0', text: rv.prompt }));
      if (rv.graph) { var g = el('div', { style: 'max-width:260px' }); item.appendChild(g); SC.Plane.fromSpec(g, rv.graph); }
      item.appendChild(el('p', { class: 'small', html: 'Jawabanmu: <b>' + SC.esc(rv.your_answer) + '</b> · Kunci: <b>' + SC.esc(rv.answer_display) + '</b>' }));
      item.appendChild(el('div', { class: 'explain feedback', html: '<div class="explain"><b>Pembahasan:</b> ' + SC.esc(rv.explain) + '</div>' }));
      mount.appendChild(item);
    });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
})(window.SC);
