/* GAME 3 — Line Builder: pilih tuas m dan c agar mesin menggambar garis target. */
(function (SC) {
  'use strict';
  var el = SC.el;
  SC.Games['line-builder'] = {
    render: function (ctx, round) {
      var area = ctx.area();
      var pick = { m: null, c: null };
      var machine = el('div', { class: 'machine', 'aria-live': 'polite' });
      var holder = el('div', {});
      area.appendChild(machine);
      area.appendChild(holder);
      var plane = new SC.Plane(holder, { range: round.range });
      var p1 = round.points[0], p2 = round.points[1];
      var locked = false;
      function draw(state) {
        plane.clear();
        plane.addLine({ p1: p1, p2: p2, cls: 'navy dashed thick', label: 'target' });
        plane.addPoint({ x: p1[0], y: p1[1], label: SC.pt(p1[0], p1[1]), cls: 'teal' });
        plane.addPoint({ x: p2[0], y: p2[1], label: SC.pt(p2[0], p2[1]), cls: 'teal' });
        var m = SC.parseNum(pick.m), c = SC.parseNum(pick.c);
        if (isFinite(m) && isFinite(c)) plane.addLine({ m: m, c: c, cls: 'thick' + (state === 'ok' ? ' teal' : ''), animate: true });
        plane.render();
        machine.innerHTML = 'y = <span style="color:#fff">' + (pick.m === null ? '[m]' : SC.esc(SC.fmt(m))) + '</span>x + <span style="color:#fff">' + (pick.c === null ? '[c]' : SC.esc(SC.fmt(c))) + '</span>';
      }
      function group(label, key, opts) {
        var g = el('div', { class: 'lever-group' }, [el('h4', { text: label })]);
        var row = el('div', { class: 'levers' });
        var levers = opts.map(function (v) {
          var b = el('button', { type: 'button', class: 'lever', text: SC.fmt(SC.parseNum(v)) });
          b.addEventListener('click', function () {
            if (locked) return;
            pick[key] = v;
            levers.forEach(function (x) { x.classList.toggle('on', x === b); });
            draw();
          });
          row.appendChild(b);
          return b;
        });
        g.appendChild(row);
        return g;
      }
      var controls = el('div', { style: 'margin-top:14px' });
      controls.appendChild(group('Tuas gradien (m)', 'm', round.m_options));
      controls.appendChild(group('Tuas konstanta (c)', 'c', round.c_options));
      var test = el('button', { class: 'btn btn-primary', type: 'button', text: 'UJI MESIN' });
      controls.appendChild(test);
      area.appendChild(controls);
      test.addEventListener('click', function () {
        if (locked) return;
        if (pick.m === null || pick.c === null) { ctx.say('hint', 'Pilih satu tuas m dan satu tuas c dulu!', 'bad'); return; }
        ctx.submit({ m: pick.m, c: pick.c }).then(function (res) {
          if (!res) return;
          if (res.correct) { locked = true; draw('ok'); }
          else if (res.done) { locked = true; }
        });
      });
      draw();
      return { intro: 'Mesin rusak! Garis putus-putus adalah target. Pilih m dan c yang tepat, lalu UJI MESIN.' };
    }
  };
})(window.SC);
