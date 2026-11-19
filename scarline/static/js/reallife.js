/* Real-Life Challenge — grafik model linear dengan slider + crosshair (geser atau arahkan kursor). */
(function (SC) {
  'use strict';
  var host = document.getElementById('rl-chart');
  if (!host) return;
  var M = JSON.parse(host.getAttribute('data-model'));
  var NS = 'http://www.w3.org/2000/svg';
  var slider = document.getElementById('rl-x'), out = document.getElementById('rl-xo'), readout = document.getElementById('rl-readout');
  var eqs = document.getElementById('model-eqs');

  function svg(tag, a) { var n = document.createElementNS(NS, tag); Object.keys(a || {}).forEach(function (k) { n.setAttribute(k, a[k]); }); return n; }
  function num(v) {
    if (M.unit_y === 'Rp') return 'Rp' + Math.round(v).toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    return (Math.round(v * 100) / 100).toString().replace('.', ',') + ' ' + M.unit_y;
  }
  function coef(v) { return M.unit_y === 'Rp' ? Math.round(v).toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.') : String(v).replace('.', ','); }
  function niceStep(max) {
    var raw = max / 5, p = Math.pow(10, Math.floor(Math.log10(raw))), m = raw / p;
    return (m <= 1 ? 1 : m <= 2 ? 2 : m <= 2.5 ? 2.5 : m <= 5 ? 5 : 10) * p;
  }
  var yMaxRaw = Math.max.apply(null, M.lines.map(function (l) { return l.m * M.x_max + l.c; }));
  var yStep = niceStep(yMaxRaw), yMax = Math.ceil(yMaxRaw * 1.05 / yStep) * yStep;
  var W = 560, H = 300, L = 70, R = 18, T = 26, B = 40;
  var pw = W - L - R, ph = H - T - B;
  var X = function (x) { return L + pw * x / M.x_max; }, Y = function (y) { return T + ph * (1 - y / yMax); };

  M.lines.forEach(function (l, i) {
    eqs.appendChild(SC.el('li', { html: '<i class="sw rl-s' + i + '"></i> ' + SC.esc(l.name) + ': <span class="math">y = ' + coef(l.m) + 'x + ' + coef(l.c) + '</span>' }));
  });

  var s = svg('svg', { viewBox: '0 0 ' + W + ' ' + H, class: 'rl-svg', role: 'img', 'aria-label': 'Grafik ' + M.y_label + ' terhadap ' + M.x_label });
  for (var gy = 0; gy <= yMax + 1e-9; gy += yStep) {
    s.appendChild(svg('line', { x1: L, x2: W - R, y1: Y(gy), y2: Y(gy), class: 'cg-grid' }));
    var ty = svg('text', { x: L - 8, y: Y(gy) + 4, class: 'cg-axis', 'text-anchor': 'end' });
    ty.textContent = M.unit_y === 'Rp' ? (gy >= 1000 ? (gy / 1000).toString().replace('.', ',') + 'rb' : gy) : String(gy).replace('.', ',');
    s.appendChild(ty);
  }
  var xStep = M.x_max > 15 ? 4 : 2;
  for (var gx = 0; gx <= M.x_max; gx += xStep) {
    var tx = svg('text', { x: X(gx), y: H - B + 18, class: 'cg-axis', 'text-anchor': 'middle' }); tx.textContent = gx; s.appendChild(tx);
  }
  s.appendChild(svg('line', { x1: L, x2: W - R, y1: Y(0), y2: Y(0), class: 'cg-base' }));
  s.appendChild(svg('line', { x1: L, x2: L, y1: T, y2: Y(0), class: 'cg-base' }));
  var xl = svg('text', { x: L + pw / 2, y: H - 4, class: 'cg-axis-title', 'text-anchor': 'middle' }); xl.textContent = M.x_label; s.appendChild(xl);
  var yl = svg('text', { x: 12, y: T - 10, class: 'cg-axis-title' }); yl.textContent = M.y_label; s.appendChild(yl);

  M.lines.forEach(function (l, i) {
    var path = svg('line', { x1: X(0), y1: Y(l.c), x2: X(M.x_max), y2: Y(l.m * M.x_max + l.c), class: 'rl-line rl-s' + i + (SC.reducedMotion() ? '' : ' rl-draw') });
    s.appendChild(path);
    var lab = svg('text', { x: X(M.x_max) - 4, y: Y(l.m * M.x_max + l.c) - 8, class: 'cg-label', 'text-anchor': 'end' }); lab.textContent = l.name; s.appendChild(lab);
    var c0 = svg('circle', { cx: X(0), cy: Y(l.c), r: 4.5, class: 'rl-dot rl-s' + i }); s.appendChild(c0);
  });
  if (M.lines.length === 2) {
    var a = M.lines[0], b = M.lines[1];
    if (a.m !== b.m) {
      var ix = (b.c - a.c) / (a.m - b.m);
      if (ix >= 0 && ix <= M.x_max) {
        s.appendChild(svg('circle', { cx: X(ix), cy: Y(a.m * ix + a.c), r: 7, class: 'rl-cross' }));
        var ct = svg('text', { x: X(ix) + 10, y: Y(a.m * ix + a.c) + 18, class: 'cg-label' }); ct.textContent = 'titik potong (' + coef(ix) + ' ' + M.unit_x + ')'; s.appendChild(ct);
      }
    }
  }
  var guide = svg('line', { y1: T, y2: Y(0), class: 'rl-guide' });
  s.appendChild(guide);
  var markers = M.lines.map(function (l, i) { var c = svg('circle', { r: 6, class: 'rl-marker rl-s' + i }); s.appendChild(c); return c; });
  var hit = svg('rect', { x: L, y: T, width: pw, height: ph, class: 'cg-hit' });
  s.appendChild(hit);
  host.appendChild(s);
  if (M.lines.length > 1) {
    var lg = SC.el('div', { class: 'chart-legend' });
    M.lines.forEach(function (l, i) { lg.appendChild(SC.el('span', {}, [SC.el('i', { class: 'sw rl-s' + i }), l.name])); });
    host.insertBefore(lg, s);
  }

  function update(x) {
    x = Math.max(0, Math.min(M.x_max, x));
    slider.value = x; out.textContent = x;
    guide.setAttribute('x1', X(x)); guide.setAttribute('x2', X(x));
    var parts = [];
    M.lines.forEach(function (l, i) {
      var y = l.m * x + l.c;
      markers[i].setAttribute('cx', X(x)); markers[i].setAttribute('cy', Y(y));
      parts.push('<span><i class="sw rl-s' + i + '"></i> ' + SC.esc(l.name) + ': <b>' + num(y) + '</b> <small class="muted">(' + coef(l.m) + ' × ' + x + ' + ' + coef(l.c) + ')</small></span>');
    });
    readout.innerHTML = '<b>' + SC.esc(M.x_label) + ' = ' + x + '</b>' + parts.join('');
  }
  slider.addEventListener('input', function () { update(+slider.value); });
  function fromPointer(e) {
    var r = s.getBoundingClientRect();
    var px = (e.clientX - r.left) * W / r.width;
    update(Math.round((px - L) / pw * M.x_max / (+slider.step || 1)) * (+slider.step || 1));
  }
  hit.addEventListener('pointermove', fromPointer);
  hit.addEventListener('pointerdown', fromPointer);
  update(+slider.value);
})(window.SC);
