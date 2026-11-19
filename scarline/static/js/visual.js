/* Visual Learning Mode — animasi konsep yang bisa diputar, dijeda, digeser, dan dijalankan per langkah.
 * Setiap adegan: draw(plane, t) menggambar keadaan pada waktu t ∈ [0, 1]; steps[] = [batas t, teks]. */
(function (SC) {
  'use strict';
  var el = SC.el;
  var $ = function (id) { return document.getElementById(id); };
  var NS = 'http://www.w3.org/2000/svg';
  function svgEl(tag, a) { var n = document.createElementNS(NS, tag); Object.keys(a).forEach(function (k) { n.setAttribute(k, a[k]); }); return n; }
  function lerp(a, b, k) { return a + (b - a) * Math.max(0, Math.min(1, k)); }
  function seg(t, a, b) { return Math.max(0, Math.min(1, (t - a) / (b - a))); }
  function round(v, d) { var p = Math.pow(10, d || 0); return Math.round(v * p) / p; }
  function rightAngle(x, y, a1, size) {
    // penanda siku di titik (x, y): sisi searah sudut a1 dan a1 + 90°
    var s = size || 0.5, u = [Math.cos(a1) * s, Math.sin(a1) * s], v = [Math.cos(a1 + Math.PI / 2) * s, Math.sin(a1 + Math.PI / 2) * s];
    return svgEl('path', { d: 'M' + (x + u[0]) + ' ' + -(y + u[1]) + ' L' + (x + u[0] + v[0]) + ' ' + -(y + u[1] + v[1]) + ' L' + (x + v[0]) + ' ' + -(y + v[1]), class: 'right-angle' });
  }

  var SCENES = [
    {
      title: 'Titik koordinat', dur: 9000,
      explain: 'Setiap titik dicapai dari O(0, 0): geser mendatar sejauh x (kanan +, kiri −), lalu tegak sejauh y (atas +, bawah −).',
      steps: [[0, 'Mulai dari titik asal O(0, 0).'], [0.25, 'A(3, 2): 3 ke kanan, 2 ke atas → Kuadran I.'], [0.5, 'B(−4, 1): 4 ke kiri, 1 ke atas → Kuadran II.'], [0.75, 'C(−2, −3): 2 ke kiri, 3 ke bawah → Kuadran III.']],
      draw: function (p, t) {
        var pts = [[3, 2, 'A'], [-4, 1, 'B'], [-2, -3, 'C']];
        p.opts.quadrants = true;
        var eq = 'O(0, 0)';
        pts.forEach(function (q, i) {
          var a = 0.25 * (i + 1), k1 = seg(t, a + 0.02, a + 0.13), k2 = seg(t, a + 0.13, a + 0.23);
          if (t < a) return;
          var x = lerp(0, q[0], k1), y = lerp(0, q[1], k2);
          if (k1 > 0) p.addLine({ p1: [0, 0], p2: [x, 0], segment: true, cls: 'dashed teal' });
          if (k2 > 0) p.addLine({ p1: [q[0], 0], p2: [q[0], y], segment: true, cls: 'dashed teal' });
          p.addPoint({ x: x, y: y, label: k2 >= 1 ? q[2] + SC.pt(q[0], q[1]) : '', cls: k2 >= 1 ? 'ok' : 'ghost' });
          if (t >= a) eq = q[2] + '(' + SC.fmt(round(x)) + ', ' + SC.fmt(round(y)) + ')';
        });
        p.addPoint({ x: 0, y: 0, label: 'O', cls: 'navy' });
        return eq;
      }
    },
    {
      title: 'Pembentukan garis', dur: 8000,
      explain: 'Garis y = 2x − 1 adalah kumpulan SEMUA titik (x, y) yang memenuhi persamaannya. Hitung y untuk beberapa x, gambar titiknya, lalu hubungkan.',
      steps: [[0, 'Pilih nilai x: −1, 0, 1, 2, 3.'], [0.12, 'Hitung y = 2x − 1 untuk setiap x.'], [0.6, 'Semua titik ternyata segaris!'], [0.75, 'Hubungkan titik-titiknya → garis y = 2x − 1.']],
      draw: function (p, t) {
        var xs = [-1, 0, 1, 2, 3], eq = 'y = 2x − 1';
        xs.forEach(function (x, i) {
          var a = 0.12 + i * 0.1;
          if (t >= a) { p.addPoint({ x: x, y: 2 * x - 1, label: SC.pt(x, 2 * x - 1), cls: 'ok' }); eq = 'x = ' + SC.fmt(x) + ' → y = 2(' + SC.fmt(x) + ') − 1 = ' + SC.fmt(2 * x - 1); }
        });
        if (t >= 0.75) { var k = seg(t, 0.75, 0.95); p.addLine({ p1: [lerp(-1, -6, k), lerp(-3, -13, k)], p2: [lerp(3, 7, k), lerp(5, 13, k)], segment: true, cls: 'thick' }); eq = 'y = 2x − 1'; }
        return eq;
      }
    },
    {
      title: 'Perubahan gradien', dur: 9000,
      explain: 'Gradien m menentukan kemiringan. m > 0 garis naik, m < 0 garis turun, m = 0 mendatar. Semakin besar |m|, semakin curam.',
      steps: [[0, 'm = −3: garis turun tajam.'], [0.3, 'm mendekati 0: garis makin landai.'], [0.5, 'm = 0: garis mendatar.'], [0.7, 'm > 0: garis naik, makin curam saat m membesar.']],
      draw: function (p, t) {
        var m = round(lerp(-3, 3, t), 2), c = 1;
        p.addLine({ m: m, c: c, cls: 'thick' });
        if (Math.abs(m) > 0.05) p.addTriangle({ from: [0, c], to: [1, c + m] });
        p.addPoint({ x: 0, y: c, label: '(0, 1)', cls: 'navy' });
        return 'y = ' + SC.fmt(round(m, 1)) + 'x + 1   →   m = ' + SC.fmt(round(m, 1)) + (m > 0.05 ? ' (naik)' : m < -0.05 ? ' (turun)' : ' (mendatar)');
      }
    },
    {
      title: 'Gradien positif & negatif', dur: 7000,
      explain: 'Garis bergradien positif naik dari kiri ke kanan (Δy searah Δx). Gradien negatif turun (Δy berlawanan dengan Δx). Segitiga menunjukkan Δx dan Δy.',
      steps: [[0, 'y = 2x: x bertambah 1, y bertambah 2 → m = +2.'], [0.5, 'y = −2x: x bertambah 1, y berkurang 2 → m = −2.']],
      draw: function (p, t) {
        var k1 = seg(t, 0, 0.35), k2 = seg(t, 0.5, 0.85);
        p.addLine({ p1: [-6, -12], p2: [lerp(-6, 6, k1), lerp(-12, 12, k1)], segment: true, cls: 'thick' });
        if (k1 >= 1) p.addTriangle({ from: [1, 2], to: [2, 4] });
        if (t >= 0.5) {
          p.addLine({ p1: [-6, 12], p2: [lerp(-6, 6, k2), lerp(12, -12, k2)], segment: true, cls: 'thick teal' });
          if (k2 >= 1) p.addTriangle({ from: [-2, 4], to: [-1, 2] });
        }
        return t < 0.5 ? 'y = 2x   (m = 2 > 0)' : 'y = 2x  dan  y = −2x';
      }
    },
    {
      title: 'Garis horizontal & vertikal', dur: 7000,
      explain: 'Garis horizontal y = k memiliki gradien 0 (y tidak berubah). Garis vertikal x = k memiliki gradien TIDAK TERDEFINISI karena Δx = 0.',
      steps: [[0, 'y = 3: semua titik punya y = 3 → m = 0.'], [0.5, 'x = −2: semua titik punya x = −2 → m tidak terdefinisi.']],
      draw: function (p, t) {
        var k1 = seg(t, 0, 0.3), k2 = seg(t, 0.5, 0.8);
        p.addLine({ p1: [-6.6, 3], p2: [lerp(-6.6, 6.6, k1), 3], segment: true, cls: 'thick' });
        [-3, 0, 3].forEach(function (x) { if (k1 * 13 - 6.6 > x) p.addPoint({ x: x, y: 3, label: SC.pt(x, 3) }); });
        if (t >= 0.5) {
          p.addLine({ p1: [-2, -6.6], p2: [-2, lerp(-6.6, 6.6, k2)], segment: true, cls: 'thick teal' });
          [-4, 0].forEach(function (y) { if (k2 * 13 - 6.6 > y) p.addPoint({ x: -2, y: y, label: SC.pt(-2, y), cls: 'teal' }); });
        }
        return t < 0.5 ? 'y = 3  →  m = 0' : 'x = −2  →  m tidak terdefinisi';
      }
    },
    {
      title: 'Perubahan nilai c', dur: 8000,
      explain: 'Pada y = mx + c, nilai c adalah titik potong sumbu Y. Mengubah c menggeser garis naik/turun tanpa mengubah kemiringannya.',
      steps: [[0, 'c = −4: garis memotong sumbu Y di (0, −4).'], [0.5, 'c = 0: garis melalui titik asal.'], [0.75, 'c bertambah → garis bergeser ke atas (sejajar).']],
      draw: function (p, t) {
        var c = Math.round(lerp(-4, 4, t) * 2) / 2;
        p.addLine({ m: 1, c: -4, cls: 'faded dashed' });
        p.addLine({ m: 1, c: c, cls: 'thick' });
        p.addPoint({ x: 0, y: c, label: '(0, ' + SC.fmt(c) + ')', cls: 'ok' });
        return 'y = x ' + (c < 0 ? '− ' + SC.fmt(-c) : '+ ' + SC.fmt(c)) + '   →   c = ' + SC.fmt(c);
      }
    },
    {
      title: 'Garis sejajar', dur: 7000,
      explain: 'Dua garis SEJAJAR memiliki gradien yang sama (m₁ = m₂) dan tidak pernah berpotongan. Jaraknya ditentukan oleh perbedaan nilai c.',
      steps: [[0, 'Garis 1: y = (1/2)x + 2.'], [0.3, 'Garis 2 bergradien sama, mulai bergeser.'], [0.7, 'm₁ = m₂ = 1/2 → sejajar, tidak pernah bertemu.']],
      draw: function (p, t) {
        p.addLine({ m: 0.5, c: 2, cls: 'thick', label: 'm₁ = 1/2' });
        var c2 = round(lerp(2, -3, seg(t, 0.3, 0.9)), 1);
        if (t >= 0.3) p.addLine({ m: 0.5, c: c2, cls: 'thick teal', label: 'm₂ = 1/2' });
        return 'y = ½x + 2   ∥   y = ½x ' + (c2 < 0 ? '− ' + SC.fmt(-c2) : '+ ' + SC.fmt(c2));
      }
    },
    {
      title: 'Garis tegak lurus', dur: 9000,
      explain: 'Dua garis TEGAK LURUS berpotongan membentuk sudut siku-siku (90°). Hasil kali gradiennya selalu −1: m₁ × m₂ = −1.',
      steps: [[0, 'Garis 1 berputar di titik (0, 0).'], [0.2, 'Garis 2 selalu membentuk sudut 90° dengan garis 1.'], [0.6, 'Perhatikan: m₁ × m₂ selalu −1.']],
      draw: function (p, t) {
        var ang = lerp(0.25, 1.3, t), m1 = Math.tan(ang), m2 = -1 / m1;
        p.addLine({ m: m1, c: 0, cls: 'thick' });
        if (t >= 0.2) { p.addLine({ m: m2, c: 0, cls: 'thick teal' }); p.extras = [rightAngle(0, 0, ang, 0.7)]; }
        p.addPoint({ x: 0, y: 0, cls: 'navy' });
        return 'm₁ = ' + round(m1, 2).toString().replace('.', ',') + '   m₂ = ' + round(m2, 2).toString().replace('.', ',') + '   m₁ × m₂ = −1';
      }
    },
    {
      title: 'Animasi rumus: gradien & persamaan', dur: 10000,
      explain: 'Langkah lengkap menentukan persamaan garis melalui A(1, 2) dan B(3, 6): hitung Δx dan Δy, bagi untuk mendapat m, lalu gunakan y − y₁ = m(x − x₁).',
      steps: [[0, 'Tandai titik A(1, 2) dan B(3, 6).'], [0.15, 'Δx = 3 − 1 = 2 (geser mendatar).'], [0.3, 'Δy = 6 − 2 = 4 (geser tegak).'], [0.45, 'm = Δy ÷ Δx = 4 ÷ 2 = 2.'], [0.6, 'y − 2 = 2(x − 1).'], [0.75, 'y − 2 = 2x − 2  →  y = 2x.']],
      draw: function (p, t) {
        p.addPoint({ x: 1, y: 2, label: 'A(1, 2)', cls: 'ok' });
        p.addPoint({ x: 3, y: 6, label: 'B(3, 6)', cls: 'ok' });
        if (t >= 0.15) p.addLine({ p1: [1, 2], p2: [lerp(1, 3, seg(t, 0.15, 0.27)), 2], segment: true, cls: 'teal thick' });
        if (t >= 0.3) p.addLine({ p1: [3, 2], p2: [3, lerp(2, 6, seg(t, 0.3, 0.42))], segment: true, cls: 'navy thick' });
        if (t >= 0.45) p.addTriangle({ from: [1, 2], to: [3, 6] });
        if (t >= 0.75) p.addLine({ m: 2, c: 0, cls: 'thick' });
        var lines = ['A(1, 2), B(3, 6)', 'Δx = 3 − 1 = 2', 'Δy = 6 − 2 = 4', 'm = 4 ÷ 2 = 2', 'y − 2 = 2(x − 1)', 'y = 2x'];
        var idx = t >= 0.75 ? 5 : t >= 0.6 ? 4 : t >= 0.45 ? 3 : t >= 0.3 ? 2 : t >= 0.15 ? 1 : 0;
        return lines[idx];
      }
    }
  ];

  var plane = new SC.Plane($('scene-plane'), { range: 6, ariaLabel: 'Animasi bidang koordinat' });
  var cur = 0, t = 0, playing = false, last = 0, raf = null;
  var list = $('scene-list'), scrub = $('sc-scrub'), playBtn = $('sc-play');

  SCENES.forEach(function (s, i) {
    var b = el('button', { type: 'button', class: 'scene-btn', 'aria-current': i === 0 ? 'true' : null }, [el('span', { class: 'n', text: String(i + 1) }), el('span', { text: s.title })]);
    b.addEventListener('click', function () { load(i, true); });
    list.appendChild(b);
  });

  function frame(tt) {
    var s = SCENES[cur];
    plane.clear(); plane.opts.quadrants = false; plane.extras = [];
    var eq = s.draw(plane, tt);
    plane.render();
    $('scene-eq').textContent = eq || ' ';
    var active = 0;
    s.steps.forEach(function (st, i) { if (tt >= st[0]) active = i; });
    Array.prototype.forEach.call($('scene-steps').children, function (li, i) { li.classList.toggle('on', i === active); li.classList.toggle('past', i < active); });
    scrub.value = Math.round(tt * 1000);
  }
  function load(i, autoplay) {
    cur = (i + SCENES.length) % SCENES.length;
    var s = SCENES[cur];
    $('scene-title').textContent = s.title;
    $('scene-no').textContent = (cur + 1) + ' / ' + SCENES.length;
    $('scene-explain').textContent = s.explain;
    var ol = $('scene-steps'); ol.innerHTML = '';
    s.steps.forEach(function (st) { ol.appendChild(el('li', { text: st[1] })); });
    list.querySelectorAll('.scene-btn').forEach(function (b, k) { if (k === cur) b.setAttribute('aria-current', 'true'); else b.removeAttribute('aria-current'); });
    t = 0; frame(0);
    if (autoplay && !SC.reducedMotion()) play(); else pause();
  }
  function tick(now) {
    if (!playing) return;
    var dt = now - (last || now); last = now;
    t = Math.min(1, t + dt / SCENES[cur].dur);
    frame(t);
    if (t >= 1) { pause(); return; }
    raf = requestAnimationFrame(tick);
  }
  function play() { if (t >= 1) t = 0; playing = true; last = 0; playBtn.querySelector('span').textContent = 'Jeda'; raf = requestAnimationFrame(tick); }
  function pause() { playing = false; cancelAnimationFrame(raf); playBtn.querySelector('span').textContent = t >= 1 ? 'Putar lagi' : 'Putar'; }
  playBtn.addEventListener('click', function () { if (playing) pause(); else play(); });
  $('sc-replay').addEventListener('click', function () { t = 0; frame(0); play(); });
  $('sc-step').addEventListener('click', function () {
    pause();
    var steps = SCENES[cur].steps, nxt = steps.filter(function (st) { return st[0] > t + 0.001; })[0];
    t = nxt ? Math.min(1, nxt[0] + 0.12) : 1;
    frame(t);
  });
  scrub.addEventListener('input', function () { pause(); t = scrub.value / 1000; frame(t); });
  $('sc-prev').addEventListener('click', function () { load(cur - 1, true); });
  $('sc-next').addEventListener('click', function () { load(cur + 1, true); });
  load(0, true);
})(window.SC);
