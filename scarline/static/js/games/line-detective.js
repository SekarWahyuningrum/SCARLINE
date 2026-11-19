/* GAME 6 — Line Detective: baca berkas petunjuk, lalu klik garis pelakunya di grafik. */
(function (SC) {
  'use strict';
  var el = SC.el;
  var LETTERS = 'ABCDE';
  SC.Games['line-detective'] = {
    render: function (ctx, round, index) {
      var area = ctx.area();
      var file = el('div', { class: 'case-file' }, [
        el('span', { class: 'case-tag', text: 'BERKAS KASUS #' + (index + 1) }),
        el('p', { class: 'case-clue', text: round.clue }),
        el('p', { class: 'small muted', style: 'margin:0', text: 'Klik garis tersangka yang cocok langsung pada grafik (atau pakai tombol huruf di bawah).' })
      ]);
      var holder = el('div', { class: 'detective-plane' });
      var lineup = el('div', { class: 'lineup', role: 'group', 'aria-label': 'Daftar tersangka' });
      area.appendChild(file); area.appendChild(holder); area.appendChild(lineup);
      var done = false, eliminated = {};
      var lines = round.lines.map(function (l, i) {
        return { id: i, m: SC.parseNum(l.m), c: SC.parseNum(l.c), cls: 'sus sus-' + i, label: LETTERS[i], labelTone: 'sus-' + i };
      });
      var plane = new SC.Plane(holder, { range: round.range, onLineClick: function (id) { accuse(+id); } });
      plane.lines = lines;
      plane.render();
      var buttons = lines.map(function (l, i) {
        var b = el('button', { type: 'button', class: 'suspect sus-btn-' + i, 'aria-label': 'Tuduh garis ' + LETTERS[i] }, [el('b', { text: LETTERS[i] }), el('span', { text: 'Tersangka ' + LETTERS[i] })]);
        b.addEventListener('click', function () { accuse(i); });
        lineup.appendChild(b);
        return b;
      });
      function accuse(i) {
        if (done || eliminated[i]) return;
        buttons.forEach(function (b) { b.disabled = true; });
        ctx.submit(i).then(function (res) {
          buttons.forEach(function (b, k) { b.disabled = !!eliminated[k] || done; });
          if (!res) return;
          if (res.correct) {
            done = true;
            lines[i].cls += ' thick caught';
            lines.forEach(function (l, k) { if (k !== i) l.cls += ' faded'; });
            buttons[i].classList.add('caught');
          } else {
            eliminated[i] = true;
            lines[i].cls += ' faded';
            if (res.reveal) { lines[i].label = LETTERS[i] + ': ' + res.reveal.label; buttons[i].querySelector('span').textContent = res.reveal.label; }
            buttons[i].classList.add('cleared'); buttons[i].disabled = true;
            if (res.done) {
              done = true;
              buttons.forEach(function (b) { b.disabled = true; });
            }
          }
          plane.render();
        });
      }
      return { intro: 'Kasus ' + (index + 1) + ': baca berkasnya, ubah petunjuk ke bentuk y = mx + c, lalu tunjuk pelakunya!' };
    }
  };
})(window.SC);
