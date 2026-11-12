/* GAME 2 — Gradient Rush: atur kemiringan jembatan atau pilih garis bergradien tepat. */
(function (SC) {
  'use strict';
  var el = SC.el;
  var NS = 'http://www.w3.org/2000/svg';
  function s(tag, attrs) { var n = document.createElementNS(NS, tag); Object.keys(attrs).forEach(function (k) { n.setAttribute(k, attrs[k]); }); return n; }

  function bridgeMode(ctx, round) {
    var area = ctx.area();
    area.appendChild(el('div', { class: 'machine', html: 'Target gradien: <span style="color:#fff">m = ' + SC.esc(round.target) + '</span>' }));
    var scene = el('div', { class: 'bridge-scene' });
    var svg = s('svg', { viewBox: '0 0 160 100', 'aria-label': 'Jembatan SCAR' });
    scene.appendChild(svg);
    area.appendChild(scene);
    var rise = el('input', { type: 'range', min: round.rise[0], max: round.rise[1], step: 1, value: 1, 'aria-label': 'Perubahan tegak Δy' });
    var run = el('input', { type: 'range', min: round.run[0], max: round.run[1], step: 1, value: 2, 'aria-label': 'Perubahan mendatar Δx' });
    var ro = el('output', {}), uo = el('output', {});
    var readout = el('p', { class: 'center mono', style: 'font-weight:700;font-size:1.1rem;margin:8px 0' });
    var go = el('button', { class: 'btn btn-primary', type: 'button', text: 'Bangun Jembatan!' });
    area.appendChild(el('div', { class: 'slider-row', style: 'margin-top:14px' }, [el('span', { text: 'Δy' }), rise, ro]));
    area.appendChild(el('div', { class: 'slider-row' }, [el('span', { text: 'Δx' }), run, uo]));
    area.appendChild(readout);
    area.appendChild(el('div', { class: 'center' }, [go]));
    var locked = false;
    function draw(success) {
      var dy = +rise.value, dx = +run.value;
      ro.textContent = dy; uo.textContent = dx;
      readout.textContent = 'Gradien jembatan = Δy/Δx = ' + dy + '/' + dx + ' = ' + SC.fmt(dy / dx);
      while (svg.firstChild) svg.removeChild(svg.firstChild);
      var u = 6, ox = 34, oy = round.target_value < 0 ? 30 : 62;
      // grid
      for (var gx = 0; gx <= 160; gx += u) svg.appendChild(s('line', { x1: gx, y1: 0, x2: gx, y2: 100, stroke: 'rgba(100,139,131,.18)', 'stroke-width': .4 }));
      for (var gy = 4; gy <= 100; gy += u) svg.appendChild(s('line', { x1: 0, y1: gy, x2: 160, y2: gy, stroke: 'rgba(100,139,131,.18)', 'stroke-width': .4 }));
      svg.appendChild(s('path', { d: 'M0 ' + oy + ' H' + ox + ' V100 H0Z', fill: '#A58A70', stroke: '#25334A', 'stroke-width': 1.2 }));
      var tm = round.target_value;
      var H = tm === 0 ? 72 : Math.min(72, 46 / Math.abs(tm));
      var tx = ox + H, ty = oy - tm * H;
      svg.appendChild(s('path', { d: 'M' + tx + ' ' + Math.max(4, Math.min(96, ty)) + ' H160 V100 H' + tx + 'Z', fill: '#648B83', stroke: '#25334A', 'stroke-width': 1.2, opacity: .9 }));
      svg.appendChild(s('circle', { cx: tx, cy: Math.max(4, Math.min(96, ty)), r: 2.4, fill: '#E6C878', stroke: '#25334A', 'stroke-width': .8 }));
      svg.appendChild(s('path', { d: 'M0 100 Q80 86 160 100Z', fill: '#7FA9C9', opacity: .5 }));
      // jembatan: panjang mendatar H, skala x dan y sama agar kemiringan jujur
      var m = dy / dx;
      var ex = ox + H, ey = oy - m * H;
      var tu = Math.min(u, 40 / Math.max(Math.abs(dy), 1), 60 / dx);
      svg.appendChild(s('line', { x1: ox, y1: oy, x2: ex, y2: ey, stroke: success ? '#5E8B5A' : '#C87945', 'stroke-width': 3, 'stroke-linecap': 'round' }));
      // segitiga Δx Δy
      svg.appendChild(s('path', { d: 'M' + ox + ' ' + oy + ' H' + (ox + dx * tu) + ' V' + (oy - dy * tu), fill: 'rgba(230,200,120,.35)', stroke: '#9C7C2C', 'stroke-width': .7, 'stroke-dasharray': '1.5 1' }));
      var t1 = s('text', { x: ox + dx * tu / 2, y: oy + (dy >= 0 ? 6 : -2), 'font-size': 4.5, 'text-anchor': 'middle', fill: '#6E5518', 'font-family': 'JetBrains Mono', 'font-weight': 700 }); t1.textContent = 'Δx=' + dx;
      var t2 = s('text', { x: ox + dx * tu + 2, y: oy - dy * tu / 2, 'font-size': 4.5, fill: '#6E5518', 'font-family': 'JetBrains Mono', 'font-weight': 700 }); t2.textContent = 'Δy=' + dy;
      svg.appendChild(t1); svg.appendChild(t2);
      var g = SC.scarSvg(success ? 'celebrate' : 'think', 20);
      g.setAttribute('x', success ? ex - 9 : ox - 18); g.setAttribute('y', (success ? ey : oy) - 22);
      svg.appendChild(g);
    }
    [rise, run].forEach(function (i) { i.addEventListener('input', function () { if (!locked) draw(false); }); });
    go.addEventListener('click', function () {
      if (locked) return;
      ctx.submit({ rise: +rise.value, run: +run.value }).then(function (res) {
        if (!res) return;
        if (res.correct) { locked = true; draw(true); go.disabled = true; }
        else if (res.done) { locked = true; go.disabled = true; }
      });
    });
    draw(false);
    return { intro: 'Atur Δy dan Δx agar kemiringan jembatan tepat ' + round.target + '. Jembatan yang pas akan menyentuh bintang di tebing seberang. Cepat = bonus!' };
  }

  function pickMode(ctx, round) {
    var area = ctx.area();
    area.appendChild(el('div', { class: 'machine', html: 'Pilih garis dengan gradien <span style="color:#fff">m = ' + SC.esc(round.target) + '</span>' }));
    var grid = el('div', { class: 'pick-grid' });
    area.appendChild(grid);
    var locked = false;
    var btns = round.options.map(function (o, i) {
      var b = el('button', { type: 'button', 'aria-label': 'Garis ' + 'ABCD'[i] }, [el('span', { class: 'tag', text: 'ABCD'[i] })]);
      var h = el('div', {});
      b.appendChild(h);
      grid.appendChild(b);
      var p = new SC.Plane(h, { range: 6 });
      p.addLine({ p1: o[0], p2: o[1], cls: 'thick' });
      p.addPoint({ x: o[0][0], y: o[0][1], label: SC.pt(o[0][0], o[0][1]) });
      p.addPoint({ x: o[1][0], y: o[1][1], label: SC.pt(o[1][0], o[1][1]) });
      p.render();
      b.addEventListener('click', function () {
        if (locked) return;
        btns.forEach(function (x) { x.classList.remove('sel'); });
        b.classList.add('sel');
        ctx.submit(i).then(function (res) {
          if (!res) return;
          if (res.correct) { locked = true; b.style.borderColor = 'var(--green)'; }
          else { b.style.opacity = '.45'; if (res.done) locked = true; }
        });
      });
      return b;
    });
    return { intro: 'Hitung Δy ÷ Δx dari dua titik di setiap garis. Klik garis yang gradiennya ' + round.target + '!' };
  }

  SC.Games['gradient-rush'] = {
    render: function (ctx, round) { return round.mode === 'set' ? bridgeMode(ctx, round) : pickMode(ctx, round); }
  };
})(window.SC);
