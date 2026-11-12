/* SCARLINE Plane — bidang koordinat Kartesius interaktif berbasis SVG.
 *
 *   var p = new SC.Plane(el, { range: 6, clickable: true, onClick: fn });
 *   p.addPoint({ x: 2, y: 3, label: 'A(2, 3)' });
 *   p.addLine({ m: 2, c: 1, label: 'y = 2x + 1' });   // atau { x: 3 } (vertikal) / { p1: [..], p2: [..] }
 *   p.render();
 *
 * Koordinat SVG: x apa adanya, y dibalik (svgY = −y).
 */
(function (SC) {
  'use strict';
  var NS = 'http://www.w3.org/2000/svg';
  var ZOOMS = [4, 5, 6, 8, 10, 12, 16, 20];

  function svgEl(tag, attrs) {
    var n = document.createElementNS(NS, tag);
    Object.keys(attrs || {}).forEach(function (k) { if (attrs[k] !== undefined && attrs[k] !== null) n.setAttribute(k, attrs[k]); });
    return n;
  }

  function Plane(container, opts) {
    opts = opts || {};
    this.el = container;
    this.opts = opts;
    this.range = opts.range || 6;
    this.firstQuadrant = !!opts.firstQuadrant;
    this.snap = opts.snap === undefined ? 1 : opts.snap;
    this.points = [];
    this.lines = [];
    this.triangles = [];
    this.extras = [];
    this.selected = null;
    container.classList.add('plane');
    if (opts.clickable || opts.draggable) container.classList.add('clickable');
    this.svg = svgEl('svg', { role: 'img', 'aria-label': opts.ariaLabel || 'Bidang koordinat Kartesius' });
    container.innerHTML = '';
    container.appendChild(this.svg);
    if (opts.showCoords !== false && (opts.clickable || opts.draggable)) {
      this.coordBox = SC.el('div', { class: 'plane-coords', text: '(x, y)' });
      container.appendChild(this.coordBox);
    }
    if (opts.zoom) this._zoomButtons();
    this._bind();
  }

  Plane.prototype.bounds = function () {
    var r = this.range;
    if (this.firstQuadrant) return { xmin: -1, xmax: r, ymin: -1, ymax: r };
    return { xmin: -r, xmax: r, ymin: -r, ymax: r };
  };

  Plane.prototype._zoomButtons = function () {
    var self = this;
    var box = SC.el('div', { class: 'plane-zoom' });
    var zin = SC.el('button', { type: 'button', 'aria-label': 'Perbesar', text: '+' });
    var zout = SC.el('button', { type: 'button', 'aria-label': 'Perkecil', text: '−' });
    zin.addEventListener('click', function () { self.zoom(-1); });
    zout.addEventListener('click', function () { self.zoom(1); });
    box.appendChild(zin); box.appendChild(zout);
    this.el.appendChild(box);
  };

  Plane.prototype.zoom = function (dir) {
    var idx = ZOOMS.indexOf(this.range);
    if (idx < 0) idx = 2;
    idx = Math.max(0, Math.min(ZOOMS.length - 1, idx + dir));
    this.range = ZOOMS[idx];
    this.render();
    if (this.opts.onZoom) this.opts.onZoom(this.range);
  };

  Plane.prototype.setRange = function (r) { this.range = r; this.render(); };

  Plane.prototype.clear = function () { this.points = []; this.lines = []; this.triangles = []; this.extras = []; return this; };

  Plane.prototype.addPoint = function (p) { this.points.push(p); return p; };
  Plane.prototype.addLine = function (l) { this.lines.push(l); return l; };
  Plane.prototype.addTriangle = function (t) { this.triangles.push(t); return t; };
  Plane.prototype.removePoint = function (id) { this.points = this.points.filter(function (p) { return p.id !== id; }); };

  /** Ubah layar → koordinat matematika (dengan snapping). */
  Plane.prototype.toWorld = function (evt, raw) {
    var pt = this.svg.createSVGPoint();
    var src = evt.touches && evt.touches[0] ? evt.touches[0] : evt;
    pt.x = src.clientX; pt.y = src.clientY;
    var ctm = this.svg.getScreenCTM();
    if (!ctm) return { x: 0, y: 0 };
    var p = pt.matrixTransform(ctm.inverse());
    var x = p.x, y = -p.y;
    if (!raw && this.snap) { x = Math.round(x / this.snap) * this.snap; y = Math.round(y / this.snap) * this.snap; }
    var b = this.bounds();
    x = Math.max(b.xmin, Math.min(b.xmax, x));
    y = Math.max(b.ymin, Math.min(b.ymax, y));
    return { x: +x.toFixed(4), y: +y.toFixed(4) };
  };

  Plane.prototype._bind = function () {
    var self = this;
    var dragging = null;
    this.svg.addEventListener('pointermove', function (e) {
      var w = self.toWorld(e);
      if (self.coordBox) self.coordBox.textContent = SC.pt(w.x, w.y);
      if (dragging) {
        dragging.x = w.x; dragging.y = w.y;
        if (dragging.label && dragging.autoLabel) dragging.label = (dragging.name || '') + SC.pt(w.x, w.y);
        self.render();
        if (self.opts.onDrag) self.opts.onDrag(dragging);
      }
      if (self.opts.onHover) self.opts.onHover(w);
    });
    this.svg.addEventListener('pointerdown', function (e) {
      var target = e.target.closest ? e.target.closest('[data-pid]') : null;
      if (target && self.opts.draggable) {
        var pid = target.getAttribute('data-pid');
        dragging = self.points.filter(function (p) { return String(p.id) === pid; })[0] || null;
        if (dragging && dragging.fixed) dragging = null;
        if (dragging) {
          self.svg.setPointerCapture(e.pointerId);
          self.selected = dragging.id;
          if (self.opts.onSelect) self.opts.onSelect(dragging);
          e.preventDefault();
          return;
        }
      }
      var lineHit = e.target.closest ? e.target.closest('[data-lid]') : null;
      if (lineHit && self.opts.onLineClick) { self.opts.onLineClick(lineHit.getAttribute('data-lid')); e.preventDefault(); return; }
      if (self.opts.clickable && self.opts.onClick) {
        var w = self.toWorld(e);
        self.opts.onClick(w, e);
        self.ripple(w.x, w.y);
      }
    });
    function stop(e) {
      if (dragging) {
        try { self.svg.releasePointerCapture(e.pointerId); } catch (err) { /* abaikan */ }
        var d = dragging; dragging = null;
        if (self.opts.onDragEnd) self.opts.onDragEnd(d);
      }
    }
    this.svg.addEventListener('pointerup', stop);
    this.svg.addEventListener('pointercancel', stop);
    this.svg.addEventListener('pointerleave', function () { if (self.coordBox && !dragging) self.coordBox.textContent = '(x, y)'; });
  };

  Plane.prototype.ripple = function (x, y) {
    var c = svgEl('circle', { cx: x, cy: -y, r: 0.2, class: 'ripple' });
    this.svg.appendChild(c);
    setTimeout(function () { c.remove(); }, 900);
  };

  /** Titik ujung garis yang terpotong oleh kotak tampilan. */
  Plane.prototype._lineEnds = function (l) {
    var b = this.bounds();
    var pad = 0.6;
    if (l.p1 && l.p2 && l.segment) return [l.p1, l.p2];
    if (l.x !== undefined && l.x !== null) return [[l.x, b.ymin - pad], [l.x, b.ymax + pad]];
    var m, c;
    if (l.p1 && l.p2) {
      if (l.p1[0] === l.p2[0]) return [[l.p1[0], b.ymin - pad], [l.p1[0], b.ymax + pad]];
      m = (l.p2[1] - l.p1[1]) / (l.p2[0] - l.p1[0]);
      c = l.p1[1] - m * l.p1[0];
    } else { m = l.m; c = l.c; }
    var x1 = b.xmin - pad, x2 = b.xmax + pad;
    return [[x1, m * x1 + c], [x2, m * x2 + c]];
  };

  Plane.prototype._labelPos = function (l) {
    var b = this.bounds();
    var span = b.xmax - b.xmin;
    if (l.x !== undefined && l.x !== null) return [l.x + span * 0.02, b.ymax - span * 0.08, l.x > (b.xmin + b.xmax) / 2 ? 'end' : 'start'];
    var m, c;
    if (l.p1 && l.p2) {
      if (l.p1[0] === l.p2[0]) return [l.p1[0] + 0.2, b.ymax - span * 0.08, 'start'];
      m = (l.p2[1] - l.p1[1]) / (l.p2[0] - l.p1[0]); c = l.p1[1] - m * l.p1[0];
    } else { m = l.m; c = l.c; }
    var x = b.xmax - span * 0.06;
    var y = m * x + c;
    var lim = b.ymax - span * 0.06, low = b.ymin + span * 0.06;
    if (y > lim && m !== 0) { y = lim; x = (y - c) / m; }
    if (y < low && m !== 0) { y = low; x = (y - c) / m; }
    // label rata kanan agar teks tidak terpotong tepi bidang
    return [Math.max(b.xmin + span * 0.3, x - span * 0.02), y + span * 0.035, 'end'];
  };

  Plane.prototype.render = function () {
    var svg = this.svg;
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    var b = this.bounds();
    var span = b.xmax - b.xmin;
    var pad = span * 0.04;
    svg.setAttribute('viewBox', (b.xmin - pad) + ' ' + (-(b.ymax + pad)) + ' ' + (span + 2 * pad) + ' ' + (b.ymax - b.ymin + 2 * pad));
    var fs = span / 26;
    var step = span > 24 ? 4 : span > 14 ? 2 : 1;

    // grid
    var g = svgEl('g', {});
    for (var gx = Math.ceil(b.xmin); gx <= b.xmax; gx++) g.appendChild(svgEl('line', { x1: gx, x2: gx, y1: -b.ymin, y2: -b.ymax, class: gx % (step * 5) === 0 ? 'g-major' : 'g-minor' }));
    for (var gy = Math.ceil(b.ymin); gy <= b.ymax; gy++) g.appendChild(svgEl('line', { x1: b.xmin, x2: b.xmax, y1: -gy, y2: -gy, class: gy % (step * 5) === 0 ? 'g-major' : 'g-minor' }));
    svg.appendChild(g);

    if (this.opts.quadrants) {
      var q = svgEl('g', {});
      var qr = this.range / 2;
      [['I', qr, qr], ['II', -qr, qr], ['III', -qr, -qr], ['IV', qr, -qr]].forEach(function (d) {
        var t = svgEl('text', { x: d[1], y: -d[2] + fs, 'text-anchor': 'middle', class: 'quad-label', 'font-size': fs * 3.2 });
        t.textContent = d[0];
        q.appendChild(t);
      });
      svg.appendChild(q);
    }

    // sumbu
    var ax = svgEl('g', {});
    ax.appendChild(svgEl('line', { x1: b.xmin, x2: b.xmax, y1: 0, y2: 0, class: 'axis' }));
    ax.appendChild(svgEl('line', { x1: 0, x2: 0, y1: -b.ymin, y2: -b.ymax, class: 'axis' }));
    var ah = fs * 0.7;
    ax.appendChild(svgEl('path', { d: 'M' + b.xmax + ' 0 l' + (-ah) + ' ' + (-ah / 2) + ' v' + ah + 'z', fill: '#25334A' }));
    ax.appendChild(svgEl('path', { d: 'M0 ' + (-b.ymax) + ' l' + (-ah / 2) + ' ' + ah + ' h' + ah + 'z', fill: '#25334A' }));
    var xn = svgEl('text', { x: b.xmax - fs * 0.6, y: -fs * 0.7, class: 'axis-name', 'font-size': fs * 1.4, 'text-anchor': 'end' }); xn.textContent = 'x';
    var yn = svgEl('text', { x: fs * 0.6, y: -b.ymax + fs * 1.3, class: 'axis-name', 'font-size': fs * 1.4 }); yn.textContent = 'y';
    ax.appendChild(xn); ax.appendChild(yn);
    for (var tx = Math.ceil(b.xmin / step) * step; tx < b.xmax; tx += step) {
      if (tx === 0) continue;
      ax.appendChild(svgEl('line', { x1: tx, x2: tx, y1: -fs * 0.25, y2: fs * 0.25, class: 'axis' }));
      var tl = svgEl('text', { x: tx, y: fs * 1.15, 'text-anchor': 'middle', class: 'tick-label', 'font-size': fs * 0.8 }); tl.textContent = tx < 0 ? '−' + (-tx) : tx;
      ax.appendChild(tl);
    }
    for (var ty = Math.ceil(b.ymin / step) * step; ty < b.ymax; ty += step) {
      if (ty === 0) continue;
      ax.appendChild(svgEl('line', { x1: -fs * 0.25, x2: fs * 0.25, y1: -ty, y2: -ty, class: 'axis' }));
      var tyl = svgEl('text', { x: -fs * 0.45, y: -ty + fs * 0.3, 'text-anchor': 'end', class: 'tick-label', 'font-size': fs * 0.8 }); tyl.textContent = ty < 0 ? '−' + (-ty) : ty;
      ax.appendChild(tyl);
    }
    var o = svgEl('text', { x: -fs * 0.45, y: fs * 1.15, 'text-anchor': 'end', class: 'tick-label', 'font-size': fs * 0.8 }); o.textContent = 'O';
    ax.appendChild(o);
    svg.appendChild(ax);

    var self = this;
    // segitiga kemiringan
    this.triangles.forEach(function (t) {
      var a = t.from, z = t.to;
      svg.appendChild(svgEl('path', { d: 'M' + a[0] + ' ' + (-a[1]) + ' H' + z[0] + ' V' + (-z[1]) + 'Z', class: 'tri' }));
      var dx = z[0] - a[0], dy = z[1] - a[1];
      var lx = svgEl('text', { x: (a[0] + z[0]) / 2, y: -a[1] + (dy >= 0 ? fs * 1.1 : -fs * 0.5), 'text-anchor': 'middle', class: 'tri-label', 'font-size': fs * 0.85 });
      lx.textContent = 'Δx = ' + SC.fmt(dx);
      var ly = svgEl('text', { x: z[0] + fs * 0.4 * (dx >= 0 ? 1 : -1), y: -(a[1] + z[1]) / 2, 'text-anchor': dx >= 0 ? 'start' : 'end', class: 'tri-label', 'font-size': fs * 0.85 });
      ly.textContent = 'Δy = ' + SC.fmt(dy);
      svg.appendChild(lx); svg.appendChild(ly);
    });

    // garis
    this.lines.forEach(function (l, i) {
      var ends = self._lineEnds(l);
      var cls = 'ln ' + (l.cls || '') + (l.animate ? ' draw' : '');
      var attrs = { x1: ends[0][0], y1: -ends[0][1], x2: ends[1][0], y2: -ends[1][1], class: cls };
      if (l.color === 'teal') attrs.class += ' teal';
      svg.appendChild(svgEl('line', attrs));
      if (l.id !== undefined && self.opts.onLineClick) {
        var hit = svgEl('line', { x1: attrs.x1, y1: attrs.y1, x2: attrs.x2, y2: attrs.y2, class: 'ln-hit', 'data-lid': l.id });
        svg.appendChild(hit);
      }
      if (l.label) {
        var pos = self._labelPos(l);
        var t = svgEl('text', { x: pos[0], y: -pos[1], 'text-anchor': pos[2] || 'start', class: 'ln-label', 'font-size': fs * 0.9, fill: l.color === 'teal' || (l.cls || '').indexOf('teal') >= 0 ? '#4C6F68' : (l.cls || '').indexOf('navy') >= 0 ? '#25334A' : '#A65F31' });
        t.textContent = l.label;
        svg.appendChild(t);
      }
    });

    // ekstra (mis. jalur game)
    this.extras.forEach(function (node) { svg.appendChild(node); });

    // titik
    this.points.forEach(function (p) {
      var r = (p.r || 0.22) * (span / 12);
      var grp = svgEl('g', { 'data-pid': p.id !== undefined ? p.id : null, style: self.opts.draggable && !p.fixed ? 'cursor:grab' : null });
      if (self.selected !== null && p.id === self.selected) grp.appendChild(svgEl('circle', { cx: p.x, cy: -p.y, r: r * 2, class: 'cursor' }));
      grp.appendChild(svgEl('circle', { cx: p.x, cy: -p.y, r: r, class: 'pt ' + (p.cls || '') }));
      if (p.label) {
        var anchorRight = p.x < b.xmax - span * 0.22;
        var t = svgEl('text', { x: p.x + (anchorRight ? r * 1.6 : -r * 1.6), y: -p.y - r * 1.4, 'text-anchor': anchorRight ? 'start' : 'end', class: 'pt-label', 'font-size': fs * 0.85 });
        t.textContent = p.label;
        grp.appendChild(t);
      }
      svg.appendChild(grp);
    });
    return this;
  };

  /* ---------------------------------------------------------- spesifikasi statis */
  Plane.fromSpec = function (el, spec) {
    var p = new Plane(el, { range: spec.range || 6, firstQuadrant: !!spec.first_quadrant, quadrants: !!spec.quadrants, ariaLabel: spec.aria });
    (spec.lines || []).forEach(function (l) {
      var line = { label: l.label, color: l.color, cls: l.color === 'teal' ? 'teal' : '' };
      if (l.p1) { line.p1 = l.p1; line.p2 = l.p2; } else if (l.x !== undefined) { line.x = l.x; } else { line.m = +l.m; line.c = +l.c; }
      p.addLine(line);
    });
    (spec.triangles || []).forEach(function (t) { p.addTriangle(t); });
    (spec.points || []).forEach(function (pt) { p.addPoint({ x: +pt.x, y: +pt.y, label: pt.label }); });
    p.render();
    return p;
  };

  SC.Plane = Plane;

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-plane]').forEach(function (el) {
      try { Plane.fromSpec(el, JSON.parse(el.getAttribute('data-plane'))); } catch (err) { el.textContent = 'Grafik gagal dimuat.'; }
    });
  });
})(window.SC);
