/* GAME 5 — SCAR's Line Rescue: peta petualangan; setiap pos berisi tantangan. */
(function (SC) {
  'use strict';
  var el = SC.el;
  var NS = 'http://www.w3.org/2000/svg';
  function s(tag, attrs) { var n = document.createElementNS(NS, tag); Object.keys(attrs).forEach(function (k) { n.setAttribute(k, attrs[k]); }); return n; }

  var mapState = null;

  function nodePos(i, total) {
    var x = 70 + i * (820 / Math.max(1, total));
    var y = 220 + Math.sin(i * 1.3) * 120;
    return [x, y];
  }

  function buildMap(total) {
    var wrap = el('div', { class: 'adventure' });
    var svg = s('svg', { viewBox: '0 0 1000 440', 'aria-label': 'Peta petualangan SCAR' });
    wrap.appendChild(svg);
    var pts = [];
    for (var i = 0; i < total; i++) pts.push(nodePos(i, total));
    var goal = [930, 120];
    var d = 'M' + pts.map(function (p) { return p[0] + ' ' + p[1]; }).join(' L') + ' L' + goal[0] + ' ' + goal[1];
    // dekorasi: sungai sumbu X & pohon
    svg.appendChild(s('path', { d: 'M0 400 C200 370 380 430 560 395 S880 380 1000 405 V440 H0Z', fill: '#7FA9C9', opacity: .55 }));
    [[150, 80], [420, 60], [640, 380], [300, 390], [800, 300]].forEach(function (t) {
      svg.appendChild(s('path', { d: 'M' + t[0] + ' ' + (t[1] + 30) + ' l-18 0 l18 -34 l18 34z', fill: '#648B83', stroke: '#25334A', 'stroke-width': 3 }));
    });
    svg.appendChild(s('path', { d: d, class: 'path-bg' }));
    var done = s('path', { d: d, class: 'path-done' });
    svg.appendChild(done);
    var stops = pts.map(function (p, i) {
      var c = s('circle', { cx: p[0], cy: p[1], r: 26, class: 'stop' });
      svg.appendChild(c);
      var t = s('text', { x: p[0], y: p[1] + 6, 'text-anchor': 'middle', class: 'stop-n' }); t.textContent = i + 1;
      svg.appendChild(t);
      return c;
    });
    svg.appendChild(s('path', { d: 'M' + (goal[0] - 34) + ' ' + (goal[1] + 30) + ' V' + (goal[1] - 4) + ' L' + goal[0] + ' ' + (goal[1] - 34) + ' L' + (goal[0] + 34) + ' ' + (goal[1] - 4) + ' V' + (goal[1] + 30) + 'Z', class: 'goal' }));
    var gt = s('text', { x: goal[0], y: goal[1] + 60, 'text-anchor': 'middle', class: 'stop-n' }); gt.textContent = 'MARKAS';
    svg.appendChild(gt);
    var walker = s('g', { class: 'walker' });
    var scar = SC.scarSvg('think', 70);
    scar.setAttribute('x', -35); scar.setAttribute('y', -95);
    walker.appendChild(scar);
    svg.appendChild(walker);
    var len = 0;
    setTimeout(function () { len = done.getTotalLength(); done.style.strokeDasharray = len; done.style.strokeDashoffset = len; }, 0);
    return { wrap: wrap, svg: svg, pts: pts, goal: goal, stops: stops, walker: walker, scar: scar, done: done, total: total,
      progress: function (i, finished) {
        stops.forEach(function (c, k) { c.setAttribute('class', 'stop' + (k < i ? ' done' : k === i ? ' now' : '')); });
        var target = finished ? goal : pts[Math.min(i, pts.length - 1)];
        walker.setAttribute('transform', 'translate(' + target[0] + ',' + target[1] + ')');
        if (!len) len = done.getTotalLength();
        var frac = finished ? 1 : i / (pts.length);
        done.style.strokeDasharray = len;
        done.style.strokeDashoffset = len * (1 - frac);
        scar.setAttribute('data-mood', finished ? 'celebrate' : 'think');
      } };
  }

  SC.Games['line-rescue'] = {
    render: function (ctx, round, index) {
      var area = ctx.area();
      var total = ctx.total();
      if (index === 0 || !mapState || mapState.total !== total) mapState = buildMap(total);
      area.appendChild(mapState.wrap);
      setTimeout(function () { mapState.progress(index, false); }, 30);
      var panel = el('div', { class: 'sheet', style: 'margin-top:16px' });
      area.appendChild(panel);
      var q = { type: round.input === 'point' ? 'point' : round.input, prompt: round.prompt, options: round.options, range: round.range, graph: round.graph };
      var locked = false;
      function mount() {
        panel.innerHTML = '';
        panel.appendChild(el('span', { class: 'eyebrow', text: 'Pos ' + round.n + ' · ' + round.title }));
        var view = SC.renderQuestion(q, { onEnter: function () { btn.click(); } });
        panel.appendChild(view.el);
        var btn = el('button', { class: 'btn btn-primary', type: 'button', text: 'Buka Jalur!' });
        panel.appendChild(btn);
        btn.addEventListener('click', function () {
          if (locked) return;
          var a = view.getAnswer();
          if (a === null || a === undefined || a === '') { ctx.say('hint', 'Isi jawabanmu dulu!', 'bad'); return; }
          ctx.submit(a).then(function (res) {
            if (!res) return;
            if (res.correct) {
              locked = true; view.lock(); view.mark(true); btn.disabled = true;
              var last = index === total - 1;
              mapState.progress(index + 1, last);
            } else if (res.game_over) { locked = true; btn.disabled = true; mapState.scar.setAttribute('data-mood', 'encourage'); }
            else { setTimeout(mount, 1200); }
          });
        });
      }
      mount();
      return { intro: 'Pos ' + round.n + ': ' + round.title + '. Jawab benar untuk membuka jembatan berikutnya! Hati-hati, nyawamu terbatas.' };
    }
  };
})(window.SC);
