/* GAME 1 — Coordinate Hunter: klik lokasi titik yang hilang. */
(function (SC) {
  'use strict';
  var el = SC.el;
  var found = [];
  SC.Games['coordinate-hunter'] = {
    render: function (ctx, round, index) {
      if (index === 0) found = [];
      var area = ctx.area();
      var banner = el('div', { class: 'machine', html: 'Temukan titik <span style="color:#fff">' + SC.esc(round.label) + '</span>' });
      var holder = el('div', {});
      area.appendChild(banner); area.appendChild(holder);
      var done = false;
      var plane = new SC.Plane(holder, {
        range: round.range, clickable: true,
        onClick: function (w) {
          if (done) return;
          var mark = { x: w.x, y: w.y, label: SC.pt(w.x, w.y), cls: 'ghost' };
          plane.points = found.slice().concat([mark]);
          plane.render();
          ctx.submit([w.x, w.y]).then(function (res) {
            if (!res) return;
            if (res.correct) {
              done = true;
              found.push({ x: round.target[0], y: round.target[1], cls: 'ok glow', label: round.label });
              plane.points = found.slice();
            } else {
              mark.cls = 'bad';
              if (res.done) {
                done = true;
                found.push({ x: round.target[0], y: round.target[1], cls: 'teal', label: round.label });
                plane.points = found.slice().concat([mark]);
              }
            }
            plane.render();
          });
        }
      });
      plane.points = found.slice();
      plane.render();
      return { intro: 'Titik ' + round.label + ' hilang! Klik lokasinya di peta koordinat. Titik yang sudah ditemukan tetap menyala.' };
    }
  };
})(window.SC);
