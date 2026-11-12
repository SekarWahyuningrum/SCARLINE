/* SCARLINE Lesson — aktivitas interaktif tiap misi, contoh bertahap, mini quiz, dan penyelesaian misi. */
(function (SC) {
  'use strict';
  var el = SC.el;
  var scarWrap = function () { return document.getElementById('mission-scar'); };
  function say(mood, text, tone) { SC.scarSay(scarWrap(), mood, text, tone); }
  function feedback(box, ok, text) {
    box.innerHTML = '';
    var s = el('div', { class: 'scar-say ' + (ok ? 'ok' : 'bad') }, [SC.scarSvg(ok ? 'happy' : 'hint', 64), el('div', { class: 'bubble', html: text })]);
    box.appendChild(s);
  }

  /* ---------------------------------------------------------------- aktivitas */
  var Activities = {};

  Activities['place-points'] = function (body, a) {
    var idx = 0, tries = 0;
    var grid = el('div', { class: 'activity-grid' });
    var holder = el('div', {});
    var side = el('div', {});
    var list = el('div', { class: 'target-list' });
    var fb = el('div', { 'aria-live': 'polite' });
    side.appendChild(el('b', { text: 'Daftar lampu yang harus dipasang:' }));
    side.appendChild(list); side.appendChild(fb);
    grid.appendChild(holder); grid.appendChild(side); body.appendChild(grid);
    var plane = new SC.Plane(holder, { range: a.range, clickable: true, quadrants: true, onClick: onClick });
    function chips() {
      list.innerHTML = '';
      a.targets.forEach(function (t, i) { list.appendChild(el('span', { class: 'chip ' + (i < idx ? 'done' : i === idx ? 'now' : ''), text: SC.pt(t[0], t[1]) })); });
    }
    function onClick(w) {
      if (idx >= a.targets.length) return;
      var t = a.targets[idx];
      if (w.x === t[0] && w.y === t[1]) {
        plane.addPoint({ x: t[0], y: t[1], label: SC.pt(t[0], t[1]), cls: 'ok glow' });
        idx++; tries = 0;
        feedback(fb, true, 'Tepat! Titik ' + SC.pt(t[0], t[1]) + ' berada di <b>' + SC.quadrant(t[0], t[1]) + '</b>.');
        if (idx === a.targets.length) { say('celebrate', 'Semua lampu kota menyala! Kamu sudah jago membaca koordinat.', 'ok'); feedback(fb, true, 'Misi aktivitas selesai! Lanjutkan ke mini quiz.'); }
      } else {
        tries++;
        var hint = w.x === t[1] && w.y === t[0] ? 'x dan y tertukar! Geser mendatar dulu (x), baru tegak (y).' :
          w.x !== t[0] ? 'Periksa x: seharusnya ' + Math.abs(t[0]) + ' langkah ke ' + (t[0] > 0 ? 'kanan' : t[0] < 0 ? 'kiri' : 'tidak bergeser (tetap di sumbu Y)') + '.' :
          'x sudah benar! Sekarang y: ' + Math.abs(t[1]) + ' langkah ke ' + (t[1] > 0 ? 'atas' : 'bawah') + '.';
        feedback(fb, false, 'Kamu memilih ' + SC.pt(w.x, w.y) + '. ' + hint);
        if (tries >= 3) { plane.addPoint({ x: t[0], y: t[1], cls: 'ghost', label: '?' }); }
      }
      chips(); plane.render();
    }
    chips(); plane.render();
  };

  Activities['two-points'] = function (body, a) {
    var grid = el('div', { class: 'activity-grid' });
    var holder = el('div', {}), side = el('div', {});
    var info = el('div', { class: 'sheet', html: '<b>Klik titik pertama.</b>' });
    var reset = el('button', { class: 'btn btn-sm', type: 'button', text: 'Ulangi', style: 'margin-top:12px' });
    side.appendChild(info); side.appendChild(reset);
    grid.appendChild(holder); grid.appendChild(side); body.appendChild(grid);
    var pts = [];
    var plane = new SC.Plane(holder, { range: a.range, clickable: true, onClick: function (w) {
      if (pts.length >= 2) pts = [];
      if (pts.length === 1 && pts[0].x === w.x && pts[0].y === w.y) { info.innerHTML = '<b>Pilih titik yang berbeda!</b> Dua titik yang sama tidak bisa membentuk garis.'; return; }
      pts.push(w); draw();
    } });
    function draw() {
      plane.clear();
      pts.forEach(function (p, i) { plane.addPoint({ x: p.x, y: p.y, label: (i ? 'B' : 'A') + SC.pt(p.x, p.y) }); });
      if (pts.length === 1) info.innerHTML = '<b>Titik A' + SC.pt(pts[0].x, pts[0].y) + '</b> dipilih. Sekarang klik titik kedua.';
      if (pts.length === 2) {
        var A = pts[0], B = pts[1];
        plane.addLine({ p1: [A.x, A.y], p2: [B.x, B.y], animate: true, cls: 'thick' });
        var html;
        if (A.x === B.x) {
          html = '<b>Garis vertikal: x = ' + SC.fmt(A.x) + '</b><br>Kedua titik punya x yang sama, jadi garisnya tegak. Gradiennya tidak terdefinisi.';
        } else {
          var m = (B.y - A.y) / (B.x - A.x), c = A.y - m * A.x;
          plane.addTriangle({ from: [A.x, A.y], to: [B.x, B.y] });
          var others = [];
          for (var x = -a.range; x <= a.range; x++) { var y = m * x + c; if (Math.abs(y - Math.round(y)) < 1e-9 && Math.abs(y) <= a.range && !(x === A.x) && !(x === B.x)) others.push(SC.pt(x, y)); }
          html = '<b>' + SC.eq(m, c) + '</b><br>Garis ' + (m === 0 ? 'mendatar (horizontal)' : m > 0 ? 'naik dari kiri ke kanan' : 'turun dari kiri ke kanan') +
            '. Hanya ada <b>satu</b> garis lurus yang melalui A dan B.<br>Titik bulat lain pada garis ini: ' + (others.slice(0, 4).join(', ') || 'tidak ada di layar') + '. Semua titik itu memenuhi persamaannya!';
        }
        info.innerHTML = html;
        say('explain', 'Lihat? Cukup dua titik untuk menentukan satu garis lurus. Coba pasangan titik lain!');
      }
      plane.render();
    }
    reset.addEventListener('click', function () { pts = []; draw(); info.innerHTML = '<b>Klik titik pertama.</b>'; });
    draw(); info.innerHTML = '<b>Klik titik pertama.</b>';
  };

  Activities['gradient-lines'] = function (body, a) {
    var grid = el('div', { class: 'activity-grid' });
    var holder = el('div', {}), side = el('div', {});
    grid.appendChild(holder); grid.appendChild(side); body.appendChild(grid);
    var active = 0, solved = {};
    var colors = ['', 'teal', 'navy', 'yellow'];
    var plane = new SC.Plane(holder, { range: a.range, onLineClick: function (id) { active = +id; draw(); } });
    var rows = a.lines.map(function (l, i) {
      var inp = el('input', { class: 'num-input', inputmode: 'decimal', 'aria-label': 'Gradien ' + l.name });
      var btn = el('button', { class: 'btn btn-sm', type: 'button', text: 'Cek' });
      var msg = el('div', { class: 'small', style: 'min-height:1.3em' });
      var row = el('div', { class: 'sheet', style: 'padding:10px 12px;margin-bottom:10px;cursor:pointer' }, [el('div', { class: 'row' }, [el('b', { text: l.name, style: 'min-width:80px' }), el('span', { text: 'm =' }), inp, btn]), msg]);
      row.addEventListener('click', function (e) { if (e.target === inp || e.target === btn) return; active = i; draw(); });
      inp.addEventListener('focus', function () { active = i; draw(); });
      btn.addEventListener('click', function () {
        var dx = l.p2[0] - l.p1[0], dy = l.p2[1] - l.p1[1];
        var m = dy / dx, v = SC.parseNum(inp.value);
        if (!isFinite(v)) { msg.textContent = 'Tulis angka atau pecahan, mis. 2 atau -1/2.'; return; }
        if (Math.abs(v - m) < 1e-9) { solved[i] = true; msg.innerHTML = '<b style="color:var(--green)">Benar!</b> Δy/Δx = ' + SC.fmt(dy) + '/' + SC.fmt(dx) + ' = ' + SC.fmt(m) + ' → ' + (m > 0 ? 'naik' : m < 0 ? 'turun' : 'mendatar') + '.'; }
        else if (Math.abs(v + m) < 1e-9 && m !== 0) msg.innerHTML = '<b style="color:var(--red)">Tandanya terbalik.</b> Garis ini ' + (m > 0 ? 'naik' : 'turun') + ' dari kiri ke kanan.';
        else if (m !== 0 && Math.abs(v - 1 / m) < 1e-9) msg.innerHTML = '<b style="color:var(--red)">Δx dan Δy tertukar.</b> Gradien = Δy ÷ Δx.';
        else msg.innerHTML = '<b style="color:var(--red)">Belum tepat.</b> Lihat segitiga kuning: hitung Δy lalu bagi dengan Δx.';
        if (Object.keys(solved).length === a.lines.length) say('celebrate', 'Semua lereng terukur! Ingat: semakin besar nilai mutlak gradien, semakin curam garisnya.', 'ok');
      });
      side.appendChild(row);
      return row;
    });
    function draw() {
      plane.clear();
      a.lines.forEach(function (l, i) {
        plane.addLine({ id: i, p1: l.p1, p2: l.p2, cls: colors[i % 4] + (i === active ? ' thick' : ' faded'), label: l.name });
        if (i === active) {
          plane.addPoint({ x: l.p1[0], y: l.p1[1], label: SC.pt(l.p1[0], l.p1[1]) });
          plane.addPoint({ x: l.p2[0], y: l.p2[1], label: SC.pt(l.p2[0], l.p2[1]) });
          if (l.p1[1] !== l.p2[1]) plane.addTriangle({ from: l.p1, to: l.p2 });
        }
      });
      rows.forEach(function (r, i) { r.style.borderColor = i === active ? 'var(--orange)' : ''; });
      plane.render();
    }
    draw();
  };

  Activities['equation-sliders'] = function (body, a) {
    var grid = el('div', { class: 'activity-grid' });
    var holder = el('div', {}), side = el('div', {});
    grid.appendChild(holder); grid.appendChild(side); body.appendChild(grid);
    var eq = el('div', { class: 'eq-display' });
    var mS = el('input', { type: 'range', min: -5, max: 5, step: 0.5, value: 1, 'aria-label': 'Gradien m' });
    var cS = el('input', { type: 'range', min: -6, max: 6, step: 1, value: 0, 'aria-label': 'Konstanta c' });
    var mO = el('output', {}), cO = el('output', {});
    var info = el('dl', { class: 'readout' });
    var goal = el('div', { class: 'notice', html: 'Tantangan: buat garis yang melewati titik <b>(0, ' + a.target.c + ')</b> dan <b>(' + 2 + ', ' + (a.target.m * 2 + a.target.c) + ')</b>.' });
    side.appendChild(eq);
    side.appendChild(el('div', { class: 'slider-row' }, [el('span', { text: 'm' }), mS, mO]));
    side.appendChild(el('div', { class: 'slider-row' }, [el('span', { text: 'c' }), cS, cO]));
    side.appendChild(goal); side.appendChild(info);
    var plane = new SC.Plane(holder, { range: a.range });
    var won = false;
    function upd() {
      var m = +mS.value, c = +cS.value;
      mO.textContent = SC.fmt(m); cO.textContent = SC.fmt(c);
      eq.innerHTML = SC.esc(SC.eq(m, c)).replace(/^y = /, 'y = ');
      plane.clear();
      plane.addPoint({ x: 0, y: a.target.c, cls: 'teal', label: 'target' });
      plane.addPoint({ x: 2, y: a.target.m * 2 + a.target.c, cls: 'teal' });
      plane.addLine({ m: m, c: c, label: SC.eq(m, c), cls: 'thick' });
      plane.addPoint({ x: 0, y: c, label: '(0, ' + SC.fmt(c) + ')' });
      plane.render();
      var xi = m !== 0 ? SC.pt(-c / m, 0) : (c === 0 ? 'seluruh sumbu X' : 'tidak ada');
      info.innerHTML = '<dt>Gradien (m)</dt><dd>' + SC.fmt(m) + ' — ' + (m > 0 ? 'naik' : m < 0 ? 'turun' : 'mendatar') + '</dd><dt>Titik potong Y</dt><dd>(0, ' + SC.fmt(c) + ')</dd><dt>Titik potong X</dt><dd>' + xi + '</dd>';
      if (!won && m === a.target.m && c === a.target.c) { won = true; goal.className = 'notice ok'; goal.innerHTML = '<b>Berhasil!</b> ' + SC.eq(m, c) + ' melewati kedua titik target.'; say('happy', 'YEAY! Mesin garis menyala! m mengatur kemiringan, c menggeser garis naik-turun.', 'ok'); }
    }
    mS.addEventListener('input', upd); cS.addEventListener('input', upd);
    upd();
  };

  Activities['construct'] = function (body, a) {
    var grid = el('div', { class: 'activity-grid' });
    var holder = el('div', {}), side = el('div', {});
    grid.appendChild(holder); grid.appendChild(side); body.appendChild(grid);
    var plane = new SC.Plane(holder, { range: a.range });
    var cur = 0;
    var clue = el('div', { class: 'index-card' });
    var mI = el('input', { class: 'num-input', inputmode: 'decimal', 'aria-label': 'm' });
    var cI = el('input', { class: 'num-input', inputmode: 'decimal', 'aria-label': 'c' });
    var build = el('button', { class: 'btn btn-primary btn-sm', type: 'button', text: 'Bangun' });
    var next = el('button', { class: 'btn btn-sm hidden', type: 'button', text: 'Petunjuk berikutnya →' });
    var fb = el('div', { 'aria-live': 'polite' });
    side.appendChild(clue);
    side.appendChild(el('div', { class: 'line-input', style: 'margin:14px 0' }, ['y =', mI, 'x +', cI]));
    side.appendChild(el('div', { class: 'row' }, [build, next]));
    side.appendChild(fb);
    function load() {
      var ch = a.challenges[cur];
      clue.innerHTML = '<span class="eyebrow">Petunjuk ' + (cur + 1) + ' / ' + a.challenges.length + '</span><p style="margin:0;font-weight:800">' + SC.esc(ch.clue) + '</p>';
      mI.value = ''; cI.value = ''; fb.innerHTML = ''; next.classList.add('hidden');
      plane.clear();
      ch.show.forEach(function (p) { plane.addPoint({ x: p[0], y: p[1], label: SC.pt(p[0], p[1]), cls: 'teal' }); });
      plane.render();
    }
    build.addEventListener('click', function () {
      var ch = a.challenges[cur];
      var m = SC.parseNum(mI.value), c = SC.parseNum(cI.value);
      if (!isFinite(m) || !isFinite(c)) { feedback(fb, false, 'Isi m dan c dengan angka (boleh pecahan seperti 1/2).'); return; }
      var tm = SC.parseNum(ch.m), tc = SC.parseNum(ch.c);
      plane.lines = [{ m: m, c: c, label: SC.eq(m, c), animate: true, cls: 'thick' }];
      plane.render();
      if (Math.abs(m - tm) < 1e-9 && Math.abs(c - tc) < 1e-9) {
        feedback(fb, true, 'Garismu berimpit dengan garis rahasia: <b>' + SC.eq(tm, tc) + '</b>!');
        if (cur < a.challenges.length - 1) next.classList.remove('hidden');
        else say('celebrate', 'Semua garis berhasil dibangun. Kamu arsitek garis sejati!', 'ok');
      } else if (Math.abs(m - tm) < 1e-9) feedback(fb, false, 'Gradien sudah tepat! Cari c: substitusikan titik yang diketahui ke y = mx + c.');
      else if (Math.abs(c - tc) < 1e-9) feedback(fb, false, 'Nilai c sudah benar. Periksa lagi gradiennya.');
      else feedback(fb, false, 'Belum berimpit. Tentukan m dulu, lalu gunakan y − y₁ = m(x − x₁).');
    });
    next.addEventListener('click', function () { cur++; load(); });
    load();
  };

  Activities['pair-lines'] = function (body, a) {
    var grid = el('div', { class: 'activity-grid' });
    var holder = el('div', {}), side = el('div', {});
    grid.appendChild(holder); grid.appendChild(side); body.appendChild(grid);
    var lines = a.lines.map(function (l) { return { id: l.id, m: SC.parseNum(l.m), c: SC.parseNum(l.c) }; });
    var sel = [], found = { parallel: false, perpendicular: false };
    var plane = new SC.Plane(holder, { range: a.range, onLineClick: function (id) { toggle(id); } });
    var list = el('div', { class: 'match-grid', style: 'grid-template-columns:repeat(2,minmax(0,1fr))' });
    var btns = {};
    lines.forEach(function (l) {
      var b = el('button', { type: 'button', class: 'match-item', text: l.id + ': ' + SC.eq(l.m, l.c) });
      b.addEventListener('click', function () { toggle(l.id); });
      btns[l.id] = b; list.appendChild(b);
    });
    var check = el('button', { class: 'btn btn-primary btn-sm', type: 'button', text: 'Periksa pasangan' });
    var status = el('p', { class: 'small', html: '☐ Pasangan sejajar &nbsp; ☐ Pasangan tegak lurus' });
    var fb = el('div', {});
    side.appendChild(list); side.appendChild(el('div', { class: 'row', style: 'margin-top:12px' }, [check])); side.appendChild(status); side.appendChild(fb);
    function toggle(id) {
      var i = sel.indexOf(id);
      if (i >= 0) sel.splice(i, 1); else { if (sel.length === 2) sel.shift(); sel.push(id); }
      draw();
    }
    function draw() {
      plane.clear();
      lines.forEach(function (l, i) { plane.addLine({ id: l.id, m: l.m, c: l.c, label: l.id, cls: sel.indexOf(l.id) >= 0 ? 'thick' : (i % 2 ? 'teal faded' : 'navy faded') }); });
      Object.keys(btns).forEach(function (k) { btns[k].classList.toggle('sel', sel.indexOf(k) >= 0); });
      plane.render();
    }
    function same(p, q) { return p.indexOf(q[0]) >= 0 && p.indexOf(q[1]) >= 0; }
    check.addEventListener('click', function () {
      if (sel.length < 2) { feedback(fb, false, 'Pilih dua garis dulu.'); return; }
      var A = lines.filter(function (l) { return l.id === sel[0]; })[0], B = lines.filter(function (l) { return l.id === sel[1]; })[0];
      var prod = A.m * B.m;
      if (same(a.parallel, sel)) { found.parallel = true; feedback(fb, true, 'Sejajar! m₁ = m₂ = ' + SC.fmt(A.m) + ', tetapi c berbeda, jadi tidak pernah bertemu.'); }
      else if (same(a.perpendicular, sel)) { found.perpendicular = true; feedback(fb, true, 'Tegak lurus! m₁ × m₂ = ' + SC.fmt(A.m) + ' × ' + SC.fmt(B.m) + ' = −1.'); }
      else feedback(fb, false, 'Garis ' + sel.join(' dan ') + ' hanya berpotongan biasa: gradiennya berbeda (' + SC.fmt(A.m) + ' dan ' + SC.fmt(B.m) + ') dan hasil kalinya ' + SC.fmt(prod) + ', bukan −1.');
      status.innerHTML = (found.parallel ? '☑' : '☐') + ' Pasangan sejajar &nbsp; ' + (found.perpendicular ? '☑' : '☐') + ' Pasangan tegak lurus';
      if (found.parallel && found.perpendicular) say('celebrate', 'Detektif Paralel beraksi! Kamu menemukan kedua pasangan rahasia.', 'ok');
    });
    draw();
  };

  Activities['real-life'] = function (body) {
    var grid = el('div', { class: 'activity-grid' });
    var holder = el('div', {}), side = el('div', {});
    grid.appendChild(holder); grid.appendChild(side); body.appendChild(grid);
    side.appendChild(el('p', { html: '<b>Bandingkan dua rental sepeda.</b> A: Rp10.000 + Rp5.000/jam. B: Rp20.000 + Rp3.000/jam. Geser lama sewa:' }));
    var s = el('input', { type: 'range', min: 0, max: 10, step: 1, value: 2, 'aria-label': 'Lama sewa (jam)' });
    var o = el('output', {});
    side.appendChild(el('div', { class: 'slider-row' }, [el('span', { text: 'jam' }), s, o]));
    var info = el('div', { class: 'sheet' });
    side.appendChild(info);
    var plane = new SC.Plane(holder, { range: 10, firstQuadrant: true });
    function rp(v) { return 'Rp' + v.toLocaleString('id-ID'); }
    function upd() {
      var x = +s.value; o.textContent = x;
      var A = 5000 * x + 10000, B = 3000 * x + 20000;
      plane.clear();
      plane.addLine({ m: 0.5, c: 1, label: 'A', cls: 'thick' });
      plane.addLine({ m: 0.3, c: 2, label: 'B', cls: 'teal thick' });
      plane.addPoint({ x: x, y: A / 10000 });
      plane.addPoint({ x: x, y: B / 10000, cls: 'teal' });
      plane.render();
      var verdict = A < B ? 'Rental <b>A</b> lebih murah.' : A > B ? 'Rental <b>B</b> lebih murah.' : '<b>Biayanya sama!</b> Inilah titik potong kedua garis.';
      info.innerHTML = '<p style="margin:0">Sumbu Y dalam satuan Rp10.000.</p><p style="margin:6px 0 0">A: ' + rp(A) + ' · B: ' + rp(B) + '<br>' + verdict + '</p>';
      if (A === B) say('happy', 'Tepat di 5 jam kedua garis berpotongan. Setelah itu B lebih murah karena gradiennya lebih kecil!', 'ok');
    }
    s.addEventListener('input', upd); upd();
  };

  /* ---------------------------------------------------------------- init */
  SC.initMission = function (cfg) {
    // contoh soal bertahap
    document.querySelectorAll('.example').forEach(function (ex) {
      var items = ex.querySelectorAll('[data-steps] li');
      var ans = ex.querySelector('[data-answer]');
      var shown = 0;
      function reveal(n) {
        shown = Math.min(items.length, n);
        items.forEach(function (li, i) { li.classList.toggle('show', i < shown); });
        if (shown >= items.length) { ans.classList.remove('hidden'); ex.querySelector('[data-next-step]').disabled = true; }
      }
      ex.querySelector('[data-next-step]').addEventListener('click', function () { reveal(shown + 1); });
      ex.querySelector('[data-all-steps]').addEventListener('click', function () { reveal(items.length); });
    });
    // kasus kehidupan nyata
    document.querySelectorAll('[data-case]').forEach(function (cs) {
      var input = cs.querySelector('[data-case-input]'), msg = cs.querySelector('[data-case-msg]'), sol = cs.querySelector('[data-case-solution]');
      cs.querySelector('[data-case-check]').addEventListener('click', function () {
        var v = SC.parseNum(input.value.replace(/\./g, '').replace(/^rp/i, ''));
        if (!isFinite(v)) { msg.textContent = 'Tulis jawabanmu sebagai angka (tanpa titik ribuan), mis. 23000.'; return; }
        var ok = Math.abs(v - (+cs.getAttribute('data-answer'))) < 1e-9;
        msg.innerHTML = ok ? '<b style="color:var(--green)">Benar!</b> Bandingkan caramu dengan penyelesaian berikut.' : '<b style="color:var(--red)">Belum tepat.</b> Coba susun dulu modelnya y = mx + c, atau buka penyelesaian.';
        if (ok) sol.classList.remove('hidden');
        say(ok ? 'happy' : 'encourage', ok ? 'Hebat! Matematika di dunia nyata pun bisa kamu taklukkan!' : 'Jangan menyerah! Tentukan dulu nilai awal (c) dan laju perubahannya (m).', ok ? 'ok' : 'bad');
      });
      cs.querySelector('[data-case-show]').addEventListener('click', function () { sol.classList.remove('hidden'); });
    });
    // aktivitas
    var act = document.getElementById('activity');
    if (act) {
      var data = JSON.parse(act.getAttribute('data-activity'));
      var fn = Activities[data.type];
      if (fn) fn(act.querySelector('.activity-body'), data);
    }
    // mini quiz
    var mount = document.getElementById('mini-quiz');
    var completeBtn = document.getElementById('complete-btn');
    var status = document.getElementById('complete-status');
    var runner = SC.QuizRunner(mount, {
      kind: 'lesson', ref: cfg.slug,
      noXpText: function () { return 'XP misi diberikan saat kamu menekan “Selesaikan Misi”.'; },
      onFinish: function (res) {
        if (res.passed && !cfg.completed) {
          completeBtn.disabled = false;
          status.textContent = 'Mini quiz lulus! Klik “Selesaikan Misi” untuk membuka wilayah baru.';
          say('happy', 'Mini quiz lulus! Tinggal satu klik lagi untuk menyelesaikan misi ini.', 'ok');
          document.getElementById('complete-bar').scrollIntoView({ behavior: 'smooth', block: 'center' });
        } else if (!res.passed) {
          say('encourage', 'Belum lulus, tapi tidak apa-apa! Baca lagi bagian konsep dan contoh, lalu ulangi mini quiz.', 'bad');
        }
      }
    });
    document.getElementById('start-quiz').addEventListener('click', function () { runner.start(); });

    completeBtn.addEventListener('click', function () {
      SC.busy(completeBtn, true, 'Menyimpan...');
      SC.api(cfg.completeUrl, {}).then(function (r) {
        if (!r.ok) { SC.busy(completeBtn, false); status.textContent = r.data.error || 'Gagal menyimpan.'; return; }
        completeBtn.innerHTML = 'Misi Selesai';
        completeBtn.disabled = true;
        var next = document.getElementById('next-btn');
        if (next) { next.classList.remove('is-disabled'); next.removeAttribute('aria-disabled'); }
        status.textContent = r.data.already ? 'Misi ini sudah selesai sebelumnya.' : 'LUAR BIASA! +' + r.data.xp_awarded + ' XP. Wilayah berikutnya terbuka!';
        say('celebrate', r.data.scar || 'LUAR BIASA! Kamu berhasil membuka wilayah koordinat baru!', 'ok');
        SC.updateHeaderXP(r.data.stats);
        if (!r.data.already) SC.toast('Misi selesai!', '+' + r.data.xp_awarded + ' XP — wilayah baru terbuka.', 'celebrate');
        SC.celebrateAchievements(r.data.new_achievements);
        cfg.completed = true;
      });
    });
    document.querySelectorAll('a.is-disabled').forEach(function (a) {
      a.addEventListener('click', function (e) { if (a.classList.contains('is-disabled')) { e.preventDefault(); say('hint', 'Selesaikan misi ini dulu, ya! Lulus mini quiz lalu tekan “Selesaikan Misi”.'); } });
    });
  };
})(window.SC);
