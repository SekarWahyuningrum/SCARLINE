/* SCARLINE Coordinate Laboratory */
(function (SC) {
  'use strict';
  var el = SC.el;
  var $ = function (id) { return document.getElementById(id); };
  var scar = $('lab-scar');

  /* ------------------------------------------------------------ tabs */
  var tabs = document.querySelectorAll('[role=tab]');
  var inited = {};
  function openTab(btn) {
    tabs.forEach(function (t) {
      var on = t === btn;
      t.setAttribute('aria-selected', on ? 'true' : 'false');
      $(t.getAttribute('aria-controls')).classList.toggle('hidden', !on);
    });
    var id = btn.getAttribute('aria-controls');
    if (!inited[id]) { inited[id] = true; INIT[id](); }
    try { localStorage.setItem('scarline-lab-tab', btn.id); } catch (e) { /* abaikan */ }
  }
  tabs.forEach(function (t) { t.addEventListener('click', function () { openTab(t); }); });

  /* ------------------------------------------------------------ A. bidang interaktif */
  function initPlane() {
    var tool = 'add', nextId = 1, connectBuf = [];
    var lines = [];
    var names = 'ABCDEFGHIJKLMNPQRSTUVWXYZ';
    var plane = new SC.Plane($('lab-plane'), {
      range: 8, zoom: true, draggable: true, clickable: true,
      onClick: function (w) {
        if (tool !== 'add') return;
        if (plane.points.some(function (p) { return p.x === w.x && p.y === w.y; })) return;
        var id = nextId++;
        var name = names[(id - 1) % names.length] + (id > names.length ? Math.ceil(id / names.length) : '');
        plane.addPoint({ id: id, name: name, x: w.x, y: w.y, label: name + SC.pt(w.x, w.y), autoLabel: true });
        plane.selected = id; refresh();
      },
      onSelect: function (p) {
        if (tool === 'delete') { plane.removePoint(p.id); lines = lines.filter(function (l) { return l.a !== p.id && l.b !== p.id; }); plane.selected = null; refresh(); return; }
        if (tool === 'connect') {
          if (connectBuf.indexOf(p.id) < 0) connectBuf.push(p.id);
          if (connectBuf.length === 2) {
            var a = connectBuf[0], b = connectBuf[1];
            if (!lines.some(function (l) { return (l.a === a && l.b === b) || (l.a === b && l.b === a); })) lines.push({ a: a, b: b });
            connectBuf = [];
          }
        }
        refresh();
      },
      onDrag: function () { syncLines(); showSel(); },
      onDragEnd: function () { refresh(); }
    });
    var helps = {
      add: 'Klik di bidang untuk menambah titik (menempel ke grid).',
      move: 'Seret titik untuk menggesernya. Koordinat diperbarui langsung.',
      connect: 'Klik dua titik untuk menghubungkannya dengan garis lurus.',
      delete: 'Klik titik yang ingin dihapus.'
    };
    document.querySelectorAll('[data-tool]').forEach(function (b) {
      b.addEventListener('click', function () {
        tool = b.getAttribute('data-tool'); connectBuf = [];
        document.querySelectorAll('[data-tool]').forEach(function (x) { x.classList.toggle('on', x === b); });
        $('tool-help').textContent = helps[tool];
      });
    });
    $('snap-half').addEventListener('change', function () { plane.snap = this.checked ? 0.5 : 1; });
    $('clear-all').addEventListener('click', function () { plane.points = []; lines = []; plane.selected = null; refresh(); });
    function byId(id) { return plane.points.filter(function (p) { return p.id === id; })[0]; }
    function syncLines() {
      plane.lines = lines.map(function (l) {
        var A = byId(l.a), B = byId(l.b);
        if (!A || !B) return null;
        if (A.x === B.x && A.y === B.y) return null;
        return { p1: [A.x, A.y], p2: [B.x, B.y], cls: 'thick', label: lineName(A, B) };
      }).filter(Boolean);
      plane.render();
    }
    function lineName(A, B) {
      if (A.x === B.x) return 'x = ' + SC.fmt(A.x);
      var m = (B.y - A.y) / (B.x - A.x);
      return SC.eq(m, A.y - m * A.x);
    }
    function showSel() {
      var p = byId(plane.selected);
      if (!p) { $('sel-info').innerHTML = '<dt>Koordinat</dt><dd>—</dd>'; return; }
      $('sel-info').innerHTML = '<dt>Nama</dt><dd>' + p.name + '</dd><dt>Koordinat</dt><dd>' + SC.pt(p.x, p.y) + '</dd><dt>Absis (x)</dt><dd>' + SC.fmt(p.x) + '</dd><dt>Ordinat (y)</dt><dd>' + SC.fmt(p.y) + '</dd><dt>Letak</dt><dd>' + SC.quadrant(p.x, p.y) + '</dd>';
    }
    function refresh() {
      syncLines(); showSel();
      var pl = $('point-list'); pl.innerHTML = '';
      if (!plane.points.length) pl.appendChild(el('li', { text: 'Belum ada titik.' }));
      plane.points.forEach(function (p) {
        var del = el('button', { class: 'btn btn-sm btn-ghost', type: 'button', text: 'Hapus', 'aria-label': 'Hapus titik ' + p.name });
        del.addEventListener('click', function () { plane.removePoint(p.id); lines = lines.filter(function (l) { return l.a !== p.id && l.b !== p.id; }); refresh(); });
        var li = el('li', { class: p.id === plane.selected ? 'sel' : '' }, [el('span', { text: p.name + SC.pt(p.x, p.y) + ' · ' + SC.quadrant(p.x, p.y) }), del]);
        li.addEventListener('click', function (e) { if (e.target !== del) { plane.selected = p.id; refresh(); } });
        pl.appendChild(li);
      });
      var ll = $('line-list'); ll.innerHTML = '';
      if (!lines.length) ll.appendChild(el('li', { text: tool === 'connect' && connectBuf.length ? 'Pilih titik kedua...' : 'Gunakan alat “Hubungkan”.' }));
      lines.forEach(function (l, i) {
        var A = byId(l.a), B = byId(l.b);
        if (!A || !B) return;
        var m = A.x === B.x ? null : (B.y - A.y) / (B.x - A.x);
        var del = el('button', { class: 'btn btn-sm btn-ghost', type: 'button', text: 'Hapus' });
        del.addEventListener('click', function () { lines.splice(i, 1); refresh(); });
        ll.appendChild(el('li', {}, [el('span', { text: A.name + B.name + ': ' + lineName(A, B) + ' · m = ' + (m === null ? 'tidak terdefinisi' : SC.fmt(m)) }), del]));
      });
    }
    [[2, 3], [-3, 1]].forEach(function (p) { plane.addPoint({ id: nextId, name: names[nextId - 1], x: p[0], y: p[1], label: names[nextId - 1] + SC.pt(p[0], p[1]), autoLabel: true }); nextId++; });
    lines.push({ a: 1, b: 2 });
    plane.selected = 1;
    refresh();
  }

  /* ------------------------------------------------------------ B. gradient simulator */
  function initGradient() {
    var plane = new SC.Plane($('grad-plane'), { range: 6 });
    var slider = $('grad-m'), vertical = false;
    function draw() {
      var m = +slider.value;
      plane.clear();
      var info, explain;
      if (vertical) {
        plane.addLine({ x: 0, cls: 'thick navy', label: 'x = 0' });
        $('grad-eq').textContent = 'x = 0';
        $('grad-out').textContent = '—';
        info = '<dt>Gradien</dt><dd>tidak terdefinisi</dd><dt>Arah</dt><dd>tegak (vertikal)</dd><dt>Δx</dt><dd>0</dd>';
        explain = 'Garis vertikal tidak bergeser ke kanan sama sekali (Δx = 0). Karena m = Δy ÷ 0 tidak bisa dihitung, gradiennya <b>tidak terdefinisi</b>.';
        SC.scarSay(scar, 'think', 'Hmm... dibagi nol? Itu tidak bisa! Makanya gradien garis vertikal tidak terdefinisi.');
      } else {
        var run = Math.abs(m) > 3 ? 1 : 2;
        plane.addLine({ m: m, c: 0, cls: 'thick', label: SC.eq(m, 0) });
        if (m !== 0) plane.addTriangle({ from: [0, 0], to: [run, m * run] });
        plane.addPoint({ x: 0, y: 0 }); plane.addPoint({ x: run, y: m * run });
        $('grad-eq').textContent = SC.eq(m, 0);
        $('grad-out').textContent = SC.fmt(m);
        var dir = m > 0 ? 'naik dari kiri ke kanan' : m < 0 ? 'turun dari kiri ke kanan' : 'mendatar (horizontal)';
        var steep = Math.abs(m) >= 3 ? 'sangat curam' : Math.abs(m) >= 1 ? 'cukup curam' : m === 0 ? 'datar' : 'landai';
        var deg = Math.round(Math.atan(m) * 180 / Math.PI);
        info = '<dt>Gradien</dt><dd>' + SC.fmt(m) + '</dd><dt>Arah</dt><dd>' + dir + '</dd><dt>Kecuraman</dt><dd>' + steep + ' (sudut ≈ ' + deg + '°)</dd><dt>Δy per Δx = 1</dt><dd>' + SC.fmt(m) + '</dd>';
        explain = m === 0 ? 'Gradien <b>nol</b>: berapa pun x bertambah, y tetap. Garisnya mendatar.' :
          'Setiap x bertambah 1, y ' + (m > 0 ? 'bertambah ' : 'berkurang ') + SC.fmt(Math.abs(m)) + '. Semakin besar |m|, semakin curam garisnya.';
        SC.scarSay(scar, m === 0 ? 'explain' : 'happy', m > 0 ? 'Gradien positif: garis mendaki seperti naik gunung!' : m < 0 ? 'Gradien negatif: garis menurun seperti perosotan!' : 'Gradien nol: jalan datar, tidak naik tidak turun.');
      }
      $('grad-info').innerHTML = info;
      $('grad-explain').innerHTML = explain;
      plane.render();
    }
    slider.addEventListener('input', function () { vertical = false; draw(); });
    document.querySelectorAll('[data-grad]').forEach(function (b) {
      b.addEventListener('click', function () {
        var v = b.getAttribute('data-grad');
        if (v === 'v') vertical = true; else { vertical = false; slider.value = v; }
        draw();
      });
    });
    draw();
  }

  /* ------------------------------------------------------------ C. equation to graph */
  function initEq() {
    var plane = new SC.Plane($('eq-plane'), { range: 8, zoom: true });
    var prev = null;
    function draw(fromSlider) {
      if (fromSlider) { $('eq-m').value = $('eq-ms').value; $('eq-c').value = $('eq-cs').value; }
      var m = SC.parseNum($('eq-m').value), c = SC.parseNum($('eq-c').value);
      if (!isFinite(m) || !isFinite(c) || Math.abs(m) > 1000 || Math.abs(c) > 1000) {
        $('eq-error').textContent = 'Masukkan m dan c berupa angka yang valid (mis. 2, -0.5, atau 3/4).';
        return;
      }
      $('eq-error').textContent = '';
      $('eq-mo').textContent = SC.fmt(m); $('eq-co').textContent = SC.fmt(c);
      plane.clear();
      if (prev) plane.addLine({ m: prev.m, c: prev.c, cls: 'dashed faded navy' });
      plane.addLine({ m: m, c: c, cls: 'thick', label: SC.eq(m, c) });
      plane.addPoint({ x: 0, y: c, label: '(0, ' + SC.fmt(c) + ')' });
      var xi = m !== 0 ? -c / m : null;
      if (xi !== null && xi !== 0) plane.addPoint({ x: xi, y: 0, cls: 'teal', label: SC.pt(xi, 0) });
      [-2, -1, 1, 2].forEach(function (x) { plane.addPoint({ x: x, y: m * x + c, r: 0.14, cls: 'teal' }); });
      plane.render();
      var rows = [-2, -1, 0, 1, 2].map(function (x) { return SC.pt(x, m * x + c); }).join(', ');
      // bentuk umum dengan koefisien bulat
      var den = 1; for (var d = 1; d <= 12; d++) { if (Math.abs(m * d - Math.round(m * d)) < 1e-9 && Math.abs(c * d - Math.round(c * d)) < 1e-9) { den = d; break; } }
      var A = Math.round(m * den), B = -den, C = Math.round(c * den);
      if (A < 0 || (A === 0 && B < 0)) { A = -A; B = -B; C = -C; }
      var g = SC.gcd(SC.gcd(A, B), C); A /= g; B /= g; C /= g;
      var gen = (A ? (A === 1 ? 'x' : A === -1 ? '−x' : SC.fmt(A) + 'x') : '') + (B ? (A ? (B > 0 ? ' + ' : ' − ') : (B < 0 ? '−' : '')) + (Math.abs(B) === 1 ? 'y' : Math.abs(B) + 'y') : '') + (C ? (C > 0 ? ' + ' : ' − ') + Math.abs(C) : '') + ' = 0';
      $('eq-info').innerHTML = '<dt>Persamaan</dt><dd>' + SC.eq(m, c) + '</dd><dt>Bentuk umum</dt><dd>' + gen + '</dd><dt>Gradien</dt><dd>' + SC.fmt(m) + '</dd><dt>Titik potong Y</dt><dd>(0, ' + SC.fmt(c) + ')</dd><dt>Titik potong X</dt><dd>' + (xi !== null ? SC.pt(xi, 0) : (c === 0 ? 'seluruh sumbu X' : 'tidak ada')) + '</dd><dt>Titik pada garis</dt><dd style="white-space:normal">' + rows + '</dd>';
      var change = 'Garis putus-putus = garis sebelumnya.';
      if (prev) {
        if (prev.m !== m && prev.c === c) change = 'm berubah dari ' + SC.fmt(prev.m) + ' ke ' + SC.fmt(m) + ': garis berputar di titik (0, ' + SC.fmt(c) + ') dan menjadi ' + (Math.abs(m) > Math.abs(prev.m) ? 'lebih curam.' : 'lebih landai.');
        else if (prev.c !== c && prev.m === m) change = 'c berubah dari ' + SC.fmt(prev.c) + ' ke ' + SC.fmt(c) + ': garis bergeser ' + (c > prev.c ? 'ke atas' : 'ke bawah') + ' sejauh ' + SC.fmt(Math.abs(c - prev.c)) + ' satuan, kemiringannya tetap (sejajar garis lama).';
        else if (prev.c !== c || prev.m !== m) change = 'm dan c sama-sama berubah: kemiringan dan titik potong sumbu Y ikut berubah.';
      }
      $('eq-change').textContent = change;
      prev = { m: m, c: c };
      if (isFinite(+$('eq-m').value)) $('eq-ms').value = m;
      $('eq-cs').value = c;
    }
    ['eq-m', 'eq-c'].forEach(function (id) { $(id).addEventListener('change', function () { draw(false); }); $(id).addEventListener('keyup', function (e) { if (e.key === 'Enter') draw(false); }); });
    ['eq-ms', 'eq-cs'].forEach(function (id) { $(id).addEventListener('input', function () { draw(true); }); });
    draw(false);
  }

  /* ------------------------------------------------------------ hasil kalkulator */
  function renderResult(box, plane, r) {
    box.innerHTML = '';
    box.appendChild(el('h3', { text: r.equation }));
    box.appendChild(el('ol', { class: 'steps-list' }, r.steps.map(function (s) { return el('li', { text: s }); })));
    box.appendChild(el('div', { class: 'answer-line', html: 'Persamaan: <b>' + SC.esc(r.equation) + '</b> · Bentuk umum: <b>' + SC.esc(r.general) + '</b>' }));
    box.appendChild(el('dl', { class: 'readout', style: 'margin-top:10px', html:
      '<dt>Gradien</dt><dd>' + SC.esc(r.gradient) + '</dd><dt>Arah</dt><dd style="white-space:normal">' + SC.esc(r.direction) + '</dd><dt>Titik potong Y</dt><dd>' + SC.esc(r.y_intercept) + '</dd><dt>Titik potong X</dt><dd style="white-space:normal">' + SC.esc(r.x_intercept) + '</dd><dt>Contoh titik</dt><dd style="white-space:normal">' + SC.esc(r.sample_points.join(', ')) + '</dd>' }));
    plane.clear();
    if (r.vertical) plane.addLine({ x: r.x_value, cls: 'thick', label: r.equation, animate: true });
    else plane.addLine({ m: r.m_value, c: r.c_value, cls: 'thick', label: r.equation, animate: true });
    (r.points || []).forEach(function (p, i) { plane.addPoint({ x: p[0], y: p[1], label: (i ? 'B' : 'A') + SC.pt(p[0], p[1]) }); });
    if (r.points && r.points.length === 2 && !r.vertical && r.points[0][1] !== r.points[1][1]) plane.addTriangle({ from: r.points[0], to: r.points[1] });
    var maxAbs = 6;
    (r.points || []).forEach(function (p) { maxAbs = Math.max(maxAbs, Math.abs(p[0]) + 1, Math.abs(p[1]) + 1); });
    plane.range = [6, 8, 10, 12, 16, 20].filter(function (z) { return z >= maxAbs; })[0] || 20;
    plane.render();
  }

  /* ------------------------------------------------------------ D. dua titik */
  function initTwo() {
    var plane = new SC.Plane($('two-plane'), { range: 8, clickable: true, zoom: true, onClick: function (w) {
      var f = $('two-form');
      var target = clickNext === 0 ? ['x1', 'y1'] : ['x2', 'y2'];
      f.elements[target[0]].value = w.x; f.elements[target[1]].value = w.y;
      clickNext = 1 - clickNext;
      if (clickNext === 0) submit();
      else { plane.clear(); plane.addPoint({ x: w.x, y: w.y, label: 'A' + SC.pt(w.x, w.y) }); plane.render(); }
    } });
    var clickNext = 0;
    plane.render();
    function submit(e) {
      if (e) e.preventDefault();
      var f = $('two-form');
      var data = { method: 'two-points', x1: f.elements.x1.value, y1: f.elements.y1.value, x2: f.elements.x2.value, y2: f.elements.y2.value };
      var box = $('two-result');
      SC.api('/api/lab/calc', data).then(function (r) {
        if (!r.ok) { box.innerHTML = '<p class="notice error">' + SC.esc(r.data.error) + '</p>'; return; }
        renderResult(box, plane, r.data);
        if (r.data.vertical) {
          box.insertBefore(el('div', { class: 'notice', html: '<b>Perhatian:</b> kedua titik memiliki x yang sama, sehingga garisnya <b>vertikal</b> dan gradiennya <b>tidak terdefinisi</b>.' }), box.firstChild);
          SC.scarSay(scar, 'think', 'x₁ = x₂, jadi Δx = 0. Garisnya tegak dan gradiennya tidak terdefinisi!');
        } else SC.scarSay(scar, 'happy', 'Dua titik → satu garis lurus: ' + SC.esc(r.data.equation) + '!');
      });
    }
    $('two-form').addEventListener('submit', submit);
    submit();
  }

  /* ------------------------------------------------------------ E. kalkulator */
  function initCalc() {
    var plane = new SC.Plane($('calc-plane'), { range: 8, zoom: true });
    plane.render();
    var FIELDS = {
      'point-slope': { f: 'y − y₁ = m(x − x₁)', inputs: [['m', 'm', '2'], ['x1', 'x₁', '1'], ['y1', 'y₁', '4']] },
      'two-points': { f: 'm = (y₂ − y₁)/(x₂ − x₁), lalu y − y₁ = m(x − x₁)', inputs: [['x1', 'x₁', '-1'], ['y1', 'y₁', '5'], ['x2', 'x₂', '3'], ['y2', 'y₂', '-3']] },
      'slope-intercept': { f: 'y = mx + c', inputs: [['m', 'm', '-2'], ['c', 'c', '4']] },
      'gradient': { f: 'm = Δy/Δx = (y₂ − y₁)/(x₂ − x₁)', inputs: [['x1', 'x₁', '-2'], ['y1', 'y₁', '4'], ['x2', 'x₂', '2'], ['y2', 'y₂', '-4']] },
      'origin': { f: 'y = mx  (c = 0)', inputs: [['m', 'm', '3/2']] }
    };
    var method = $('calc-method');
    function build() {
      var cfg = FIELDS[method.value];
      $('calc-formula').textContent = cfg.f;
      var box = $('calc-inputs'); box.innerHTML = '';
      cfg.inputs.forEach(function (i) {
        box.appendChild(el('label', {}, [i[1] + ' =', el('input', { class: 'num-input', name: i[0], value: i[2], inputmode: 'decimal', 'aria-label': i[1] })]));
      });
      $('calc-error').textContent = '';
    }
    method.addEventListener('change', build);
    $('calc-form').addEventListener('submit', function (e) {
      e.preventDefault();
      var data = { method: method.value };
      var empty = false;
      $('calc-inputs').querySelectorAll('input').forEach(function (i) { data[i.name] = i.value; if (!i.value.trim()) empty = true; i.classList.toggle('invalid', !i.value.trim()); });
      if (empty) { $('calc-error').textContent = 'Semua kolom angka wajib diisi.'; return; }
      var btn = this.querySelector('button[type=submit]');
      SC.busy(btn, true, 'Menghitung...');
      SC.api('/api/lab/calc', data).then(function (r) {
        SC.busy(btn, false);
        if (!r.ok) { $('calc-error').textContent = r.data.error; return; }
        $('calc-error').textContent = '';
        renderResult($('calc-result'), plane, r.data);
        SC.scarSay(scar, 'explain', 'Ini langkah-langkahnya. Coba hitung sendiri dulu, lalu cocokkan dengan hasilku!');
      });
    });
    build();
  }

  var INIT = { 'tab-plane': initPlane, 'tab-gradient': initGradient, 'tab-eq': initEq, 'tab-two': initTwo, 'tab-calc': initCalc };
  var saved = null;
  try { saved = localStorage.getItem('scarline-lab-tab'); } catch (e) { /* abaikan */ }
  openTab((saved && $(saved)) || tabs[0]);
})(window.SC);
