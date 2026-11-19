/* SCARLINE Pre-Test & Post-Test — indikator nomor soal, progres, tinjau sebelum kirim,
 * nilai + benar/salah + pembahasan, dan grafik perbandingan pre-test vs post-test. */
(function (SC) {
  'use strict';
  var el = SC.el;

  /* ------------------------------------------------------------ grafik perbandingan */
  var NS = 'http://www.w3.org/2000/svg';
  function svg(tag, attrs, kids) {
    var n = document.createElementNS(NS, tag);
    Object.keys(attrs || {}).forEach(function (k) { n.setAttribute(k, attrs[k]); });
    (kids || []).forEach(function (c) { n.appendChild(c); });
    return n;
  }
  function tipFor(host) {
    var tip = host.querySelector('.chart-tip');
    if (!tip) { tip = el('div', { class: 'chart-tip', role: 'tooltip' }); host.appendChild(tip); }
    return tip;
  }
  function bindTip(host, node, html) {
    function show(e) {
      var tip = tipFor(host);
      tip.innerHTML = html;
      tip.classList.add('on');
      var r = host.getBoundingClientRect();
      var b = (e && e.clientX !== undefined && e.type !== 'focus') ? { x: e.clientX, y: e.clientY } : (function () { var bb = node.getBoundingClientRect(); return { x: bb.left + bb.width / 2, y: bb.top }; })();
      tip.style.left = Math.min(r.width - 170, Math.max(4, b.x - r.left + 12)) + 'px';
      tip.style.top = Math.max(0, b.y - r.top - 46) + 'px';
    }
    function hide() { var tip = host.querySelector('.chart-tip'); if (tip) tip.classList.remove('on'); }
    node.setAttribute('tabindex', '0');
    node.addEventListener('mousemove', show);
    node.addEventListener('focus', show);
    node.addEventListener('mouseleave', hide);
    node.addEventListener('blur', hide);
  }
  /** Batang membulat 4px di ujung data, berpangkal di garis dasar (kiri). */
  function hbar(x, y, w, h, cls) {
    w = Math.max(0, w);
    var r = Math.min(4, w, h / 2);
    var d = 'M' + x + ' ' + y + 'H' + (x + w - r) + 'Q' + (x + w) + ' ' + y + ' ' + (x + w) + ' ' + (y + r) + 'V' + (y + h - r) +
      'Q' + (x + w) + ' ' + (y + h) + ' ' + (x + w - r) + ' ' + (y + h) + 'H' + x + 'Z';
    return svg('path', { d: d, class: cls });
  }

  /** Grafik pre vs post: dua batang skor + batang per topik. data = comparison dari server. */
  SC.compareChart = function (host, data) {
    host.innerHTML = '';
    host.classList.add('chart-host');
    var legend = el('div', { class: 'chart-legend' }, [
      el('span', {}, [el('i', { class: 'sw sw-pre' }), 'Pre-test']),
      el('span', {}, [el('i', { class: 'sw sw-post' }), 'Post-test'])
    ]);
    host.appendChild(legend);
    var rows = [{ label: 'Nilai total', pre: data.pre, post: data.post, total: true }].concat((data.topics || []).map(function (t) {
      return { label: t.label, pre: t.pre, post: t.post };
    }));
    var LW = 150, W = 560, BH = 12, GAP = 2, ROW = 2 * BH + GAP + 16, H = rows.length * ROW + 26;
    var plotW = W - LW - 46;
    var s = svg('svg', { viewBox: '0 0 ' + W + ' ' + H, class: 'cmp-chart', role: 'img',
      'aria-label': 'Perbandingan nilai pre-test ' + data.pre + ' dan post-test ' + data.post + ' per topik' });
    [0, 25, 50, 75, 100].forEach(function (v) {
      var x = LW + plotW * v / 100;
      s.appendChild(svg('line', { x1: x, x2: x, y1: 4, y2: H - 20, class: 'cg-grid' }));
      var t = svg('text', { x: x, y: H - 6, class: 'cg-axis', 'text-anchor': 'middle' }); t.textContent = v; s.appendChild(t);
    });
    rows.forEach(function (r, i) {
      var y = 8 + i * ROW;
      var lab = svg('text', { x: LW - 10, y: y + BH + 4, class: 'cg-label' + (r.total ? ' strong' : ''), 'text-anchor': 'end' });
      lab.textContent = r.label; s.appendChild(lab);
      [['pre', r.pre, y], ['post', r.post, y + BH + GAP]].forEach(function (b) {
        var g = svg('g', { class: 'cg-mark' });
        var hit = svg('rect', { x: LW, y: b[2] - 1, width: plotW + 40, height: BH + 2, class: 'cg-hit' });
        if (b[1] === null || b[1] === undefined) {
          var na = svg('text', { x: LW + 4, y: b[2] + BH - 2, class: 'cg-na' }); na.textContent = 'tidak diuji'; g.appendChild(na);
        } else {
          g.appendChild(hbar(LW, b[2], plotW * b[1] / 100, BH, 'cg-bar cg-' + b[0]));
          if (r.total || i === 0) {
            var v = svg('text', { x: LW + plotW * b[1] / 100 + 6, y: b[2] + BH - 2, class: 'cg-value' }); v.textContent = b[1]; g.appendChild(v);
          }
        }
        g.appendChild(hit);
        s.appendChild(g);
        bindTip(host, g, '<b>' + SC.esc(r.label) + '</b><br>' + (b[0] === 'pre' ? 'Pre-test' : 'Post-test') + ': ' + (b[1] === null || b[1] === undefined ? 'tidak diuji' : b[1] + (r.total ? ' / 100' : '% benar')));
      });
    });
    host.appendChild(s);
    // tampilan tabel (alternatif aksesibel)
    var det = el('details', { class: 'chart-table' }, [el('summary', { text: 'Lihat sebagai tabel' })]);
    var tb = el('table', { class: 'data' });
    tb.appendChild(el('thead', {}, [el('tr', {}, [el('th', { text: 'Bagian' }), el('th', { text: 'Pre-test' }), el('th', { text: 'Post-test' }), el('th', { text: 'Status' })])]));
    var body = el('tbody');
    rows.forEach(function (r) {
      var st = r.total ? (r.post > r.pre ? 'Naik' : r.post === r.pre ? 'Tetap' : 'Turun') : (r.post === null || r.post === undefined ? '—' : (r.post >= 70 ? 'Dikuasai' : 'Perlu ditingkatkan'));
      body.appendChild(el('tr', {}, [el('td', { text: r.label }), el('td', { text: r.pre === null || r.pre === undefined ? '—' : String(r.pre) }), el('td', { text: r.post === null || r.post === undefined ? '—' : String(r.post) }), el('td', { text: st })]));
    });
    tb.appendChild(body);
    det.appendChild(el('div', { class: 'table-wrap' }, [tb]));
    host.appendChild(det);
  };

  /** Ringkasan perbandingan: nilai awal, akhir, selisih, persentase, dikuasai & perlu ditingkatkan. */
  SC.compareSummary = function (data) {
    var wrap = el('div', { class: 'cmp-summary' });
    var diffTxt = (data.diff > 0 ? '+' : '') + data.diff;
    var tiles = el('div', { class: 'cmp-tiles' }, [
      el('div', { class: 'cmp-tile' }, [el('span', { text: 'Nilai awal' }), el('b', { text: String(data.pre) })]),
      el('div', { class: 'cmp-tile' }, [el('span', { text: 'Nilai akhir' }), el('b', { text: String(data.post) })]),
      el('div', { class: 'cmp-tile ' + (data.diff > 0 ? 'up' : data.diff < 0 ? 'down' : '') }, [el('span', { text: 'Selisih' }), el('b', { text: diffTxt })]),
      el('div', { class: 'cmp-tile' }, [el('span', { text: 'Perubahan' }), el('b', { text: data.percent_change === null || data.percent_change === undefined ? '—' : (data.percent_change > 0 ? '+' : '') + String(data.percent_change).replace('.', ',') + '%' })])
    ]);
    wrap.appendChild(tiles);
    wrap.appendChild(el('p', { class: 'cmp-verdict', text: data.verdict }));
    if (data.percent_change === null || data.percent_change === undefined) wrap.appendChild(el('p', { class: 'small muted', text: 'Persentase perubahan tidak dihitung karena nilai pre-test 0.' }));
    var cols = el('div', { class: 'grid cols-2' });
    function list(title, items, empty, cls) {
      var box = el('div', { class: 'sheet ' + cls }, [el('h4', { text: title })]);
      if (!items.length) box.appendChild(el('p', { class: 'small muted', text: empty }));
      else {
        var ul = el('ul', { class: 'topic-list' });
        items.forEach(function (t) {
          var li = el('li', {}, [el('span', { text: t.label }), el('b', { text: t.post + '%' })]);
          if (cls === 'needs' && t.lesson && t.lesson.slug) li.appendChild(el('a', { href: '/mission/' + t.lesson.slug, class: 'small', text: 'Ulangi ' + t.lesson.region + ' →' }));
          ul.appendChild(li);
        });
        box.appendChild(ul);
      }
      return box;
    }
    cols.appendChild(list('Materi yang sudah dikuasai (≥ 70%)', data.mastered || [], 'Belum ada topik yang mencapai 70%.', 'mastered'));
    cols.appendChild(list('Materi yang perlu ditingkatkan', data.needs || [], 'Semua topik sudah dikuasai — hebat!', 'needs'));
    wrap.appendChild(cols);
    return wrap;
  };

  /* ------------------------------------------------------------ runner */
  function Exam(host) {
    var kind = host.getAttribute('data-exam-kind');
    var title = host.getAttribute('data-exam-title') || 'Tes';
    var intro = host.querySelector('.exam-intro');
    var mount = host.querySelector('[data-exam-run]');
    var startBtn = host.querySelector('[data-exam-start]');
    var errEl = host.querySelector('[data-exam-error]');
    var S = null;

    startBtn.addEventListener('click', function () {
      SC.busy(startBtn, true, 'Menyiapkan soal...');
      SC.api('/api/runs', { kind: kind }).then(function (r) {
        SC.busy(startBtn, false);
        if (!r.ok) { errEl.textContent = r.data.error || 'Gagal memulai.'; return; }
        S = { run: r.data, i: 0, views: [], answers: {}, submitted: false, dir: 1 };
        intro.classList.add('hidden');
        mount.classList.remove('hidden');
        SC.sfx('start');
        build();
        window.addEventListener('beforeunload', guard);
      });
    });
    function guard(e) { if (S && !S.submitted && Object.keys(S.answers).length) { e.preventDefault(); e.returnValue = ''; } }

    var dots, card, nav, prog, bar;
    function build() {
      mount.innerHTML = '';
      prog = el('span', { class: 'chip chip-navy' });
      var top = el('div', { class: 'quiz-top' }, [el('span', { class: 'chip chip-orange', text: title }), prog]);
      bar = el('div', { class: 'fill', style: 'width:0%' });
      dots = el('div', { class: 'dots', role: 'navigation', 'aria-label': 'Indikator nomor soal' });
      card = el('div', { class: 'sheet qcard exam-card' });
      nav = el('div', { class: 'row between', style: 'margin-top:16px' });
      mount.appendChild(top);
      mount.appendChild(el('div', { class: 'ruler teal', style: 'margin-bottom:12px' }, [bar]));
      mount.appendChild(dots);
      mount.appendChild(el('div', { style: 'height:14px' }));
      mount.appendChild(card);
      mount.appendChild(nav);
      S.run.items.forEach(function (q, i) {
        S.views[i] = SC.renderQuestion(q, { onChange: function (v) { if (v === null || v === undefined || v === '') delete S.answers[i]; else { S.answers[i] = v; SC.sfx('click'); } updateDots(); } });
      });
      show(0);
    }
    function updateDots() {
      dots.innerHTML = '';
      S.run.items.forEach(function (q, i) {
        var b = el('button', { type: 'button', text: String(i + 1), class: (i === S.i ? 'now ' : '') + (S.answers[i] !== undefined ? 'ans' : ''), 'aria-label': 'Soal ' + (i + 1) + (S.answers[i] !== undefined ? ', sudah dijawab' : ', belum dijawab'), 'aria-current': i === S.i ? 'step' : null });
        b.addEventListener('click', function () { S.dir = i >= S.i ? 1 : -1; show(i); });
        dots.appendChild(b);
      });
      var n = Object.keys(S.answers).length;
      prog.textContent = 'Terjawab ' + n + ' / ' + S.run.total;
      bar.style.width = (n * 100 / S.run.total) + '%';
    }
    function show(i) {
      S.i = i;
      card.innerHTML = '';
      card.classList.remove('slide-in-l', 'slide-in-r'); void card.offsetWidth; card.classList.add(S.dir > 0 ? 'slide-in-r' : 'slide-in-l');
      var q = S.run.items[i];
      card.appendChild(el('div', { class: 'row between' }, [el('b', { text: 'Soal ' + (i + 1) + ' dari ' + S.run.total }), q.level ? el('span', { class: 'chip lvl-' + q.level, text: q.level }) : null]));
      card.appendChild(S.views[i].el);
      nav.innerHTML = '';
      var prev = el('button', { class: 'btn btn-sm', type: 'button', text: '← Sebelumnya', disabled: i === 0 });
      prev.addEventListener('click', function () { S.dir = -1; show(i - 1); });
      var last = i === S.run.total - 1;
      var next = el('button', { class: 'btn btn-sm btn-teal', type: 'button', text: last ? 'Tinjau Jawaban' : 'Berikutnya →' });
      next.addEventListener('click', function () { if (last) review(); else { S.dir = 1; show(i + 1); } });
      nav.appendChild(prev); nav.appendChild(next);
      updateDots();
    }
    function review() {
      card.innerHTML = ''; nav.innerHTML = '';
      var empty = S.run.items.map(function (q, i) { return i; }).filter(function (i) { return S.answers[i] === undefined; });
      card.appendChild(el('h3', { text: 'Tinjau sebelum mengirim' }));
      card.appendChild(el('p', { text: 'Terjawab ' + (S.run.total - empty.length) + ' dari ' + S.run.total + ' soal.' }));
      if (empty.length) card.appendChild(el('div', { class: 'notice', text: 'Belum dijawab: nomor ' + empty.map(function (i) { return i + 1; }).join(', ') + '. Soal kosong dihitung salah.' }));
      card.appendChild(el('p', { class: 'muted small', text: 'Klik nomor soal di atas untuk memeriksa kembali. Setelah dikirim, kamu bisa melihat jawaban benar dan pembahasan setiap soal.' }));
      var back = el('button', { class: 'btn', type: 'button', text: 'Kembali ke soal' });
      back.addEventListener('click', function () { show(empty.length ? empty[0] : 0); });
      var send = el('button', { class: 'btn btn-primary', type: 'button', text: 'Kirim Jawaban' });
      send.addEventListener('click', function () { if (empty.length && !confirm('Masih ada ' + empty.length + ' soal kosong. Tetap kirim?')) return; submit(send); });
      nav.appendChild(back); nav.appendChild(send);
    }
    function submit(btn) {
      if (S.submitted) return;
      S.submitted = true;
      SC.busy(btn, true, 'Menilai...');
      var answers = {};
      Object.keys(S.answers).forEach(function (k) { answers[k] = S.answers[k]; });
      SC.api('/api/runs/' + S.run.run_id + '/finish', { answers: answers }).then(function (r) {
        window.removeEventListener('beforeunload', guard);
        if (!r.ok) { S.submitted = false; SC.busy(btn, false); SC.toast('Gagal mengirim', r.data.error || 'Coba lagi.', 'think'); return; }
        result(r.data);
      });
    }
    function result(d) {
      mount.innerHTML = '';
      var wrong = d.total - d.correct;
      var good = d.score >= 70;
      SC.sfx(good ? 'win' : 'done');
      if (good) SC.confetti();
      var panel = el('div', { class: 'result-panel' }, [
        SC.scarSvg(good ? 'celebrate' : 'encourage', 140),
        el('h2', { text: title + ' selesai!' }),
        el('div', { class: 'big-score', text: String(d.score) }),
        el('div', { class: 'row', style: 'justify-content:center' }, [
          el('span', { class: 'chip chip-teal', text: '✔ ' + d.correct + ' benar' }),
          el('span', { class: 'chip chip-orange', text: '✘ ' + wrong + ' salah' })
        ]),
        el('p', { style: 'font-weight:800;margin-top:10px', text: kind === 'pretest' ? 'Terima kasih! Nilai ini menjadi titik awal perjalananmu — tidak ada materi yang terkunci karena nilai pre-test.' : (d.scar || '') }),
        el('p', { class: 'chip ' + (d.xp_awarded > 0 ? 'chip-yellow' : ''), text: d.xp_awarded > 0 ? '+' + d.xp_awarded + ' XP diperoleh!' : 'XP hanya diberikan saat pertama kali mengerjakan.' })
      ]);
      if (d.stats) SC.updateHeaderXP(d.stats);
      SC.celebrateAchievements(d.new_achievements);
      var actions = el('div', { class: 'row', style: 'justify-content:center;margin-top:16px' });
      var backUrl = host.getAttribute('data-exam-back') || '/dashboard';
      actions.appendChild(el('a', { class: 'btn btn-primary', href: backUrl, text: host.getAttribute('data-exam-back-label') || 'Lanjutkan' }));
      actions.appendChild(el('a', { class: 'btn', href: '#exam-review', text: 'Lihat pembahasan' }));
      if (kind === 'posttest') actions.appendChild(el('a', { class: 'btn btn-ghost', href: '/progress', text: 'Grafik perkembangan' }));
      panel.appendChild(actions);
      mount.appendChild(el('div', { class: 'paper' }, [panel]));

      if (d.comparison) {
        var cmp = el('section', { class: 'sheet', style: 'margin-top:22px' }, [el('h2', { text: 'Perbandingan Pre-Test & Post-Test' })]);
        cmp.appendChild(SC.compareSummary(d.comparison));
        var ch = el('div', { style: 'margin-top:16px' });
        cmp.appendChild(ch);
        mount.appendChild(cmp);
        SC.compareChart(ch, d.comparison);
      } else if (kind === 'posttest') {
        mount.appendChild(el('div', { class: 'notice', style: 'margin-top:18px', text: 'Kerjakan pre-test terlebih dahulu agar perbandingan nilai bisa ditampilkan.' }));
      }

      mount.appendChild(el('h2', { id: 'exam-review', text: 'Jawaban & Pembahasan', style: 'margin-top:28px' }));
      (d.review || []).forEach(function (rv) {
        var item = el('div', { class: 'sheet review-item ' + (rv.correct ? '' : 'no'), style: 'margin-bottom:12px' });
        item.appendChild(el('div', { class: 'row between' }, [el('b', { text: 'Soal ' + (rv.index + 1) }), el('span', { class: 'status ' + (rv.correct ? 'lulus' : 'belum-lulus'), text: rv.correct ? 'Benar' : 'Salah' })]));
        item.appendChild(el('p', { style: 'font-weight:700;margin:8px 0', text: rv.prompt }));
        if (rv.options) {
          var ol = el('ol', { class: 'review-opts', type: 'A' });
          rv.options.forEach(function (o) {
            var isKey = o === rv.answer_display, isMine = o === rv.your_answer;
            ol.appendChild(el('li', { class: (isKey ? 'key ' : '') + (isMine && !isKey ? 'mine' : '') }, [o, isKey ? el('span', { class: 'tag', text: 'kunci' }) : null, isMine ? el('span', { class: 'tag', text: 'jawabanmu' }) : null]));
          });
          item.appendChild(ol);
        } else {
          item.appendChild(el('p', { class: 'small', html: 'Jawabanmu: <b>' + SC.esc(rv.your_answer) + '</b> · Kunci: <b>' + SC.esc(rv.answer_display) + '</b>' }));
        }
        item.appendChild(el('div', { class: 'explain', html: '<b>Pembahasan:</b> ' + SC.esc(rv.explain) }));
        mount.appendChild(item);
      });
      host.scrollIntoView({ behavior: SC.reducedMotion() ? 'auto' : 'smooth', block: 'start' });
    }
  }

  document.querySelectorAll('[data-exam-kind]').forEach(function (h) { Exam(h); });
})(window.SC);
