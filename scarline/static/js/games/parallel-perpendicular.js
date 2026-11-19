/* GAME 7 — Parallel or Perpendicular?: seret kartu pasangan garis ke portal yang benar. */
(function (SC) {
  'use strict';
  var el = SC.el;
  SC.Games['parallel-perpendicular'] = {
    render: function (ctx, round, index) {
      var area = ctx.area();
      var card = el('div', { class: 'pair-card', draggable: 'true', tabindex: '0', 'aria-label': 'Kartu pasangan garis: ' + round.eq1 + ' dan ' + round.eq2 + '. Pilih portal dengan tombol di bawah.' }, [
        el('span', { class: 'pc-tag', text: 'KARTU ' + (index + 1) + ' / ' + ctx.total() }),
        el('div', { class: 'pc-eq' }, [el('span', { class: 'l1', text: round.eq1 })]),
        el('div', { class: 'pc-and', text: 'dan' }),
        el('div', { class: 'pc-eq' }, [el('span', { class: 'l2', text: round.eq2 })])
      ]);
      var dock = el('div', { class: 'pair-dock' }, [card]);
      var portals = el('div', { class: 'portals portals-' + round.portals.length });
      var graph = el('div', { class: 'pair-graph hidden' });
      area.appendChild(dock); area.appendChild(portals); area.appendChild(graph);
      var done = false;
      var buttons = round.portals.map(function (p) {
        var b = el('button', { type: 'button', class: 'portal portal-' + p.key, 'data-key': p.key }, [el('span', { class: 'portal-ring', 'aria-hidden': 'true' }), el('b', { text: p.label })]);
        b.addEventListener('click', function () { choose(p.key, b); });
        b.addEventListener('dragover', function (e) { if (!done) { e.preventDefault(); b.classList.add('over'); } });
        b.addEventListener('dragleave', function () { b.classList.remove('over'); });
        b.addEventListener('drop', function (e) { e.preventDefault(); b.classList.remove('over'); choose(p.key, b); });
        portals.appendChild(b);
        return b;
      });
      card.addEventListener('dragstart', function (e) { if (done) { e.preventDefault(); return; } e.dataTransfer.setData('text/plain', 'card'); card.classList.add('dragging'); });
      card.addEventListener('dragend', function () { card.classList.remove('dragging'); });
      // Sentuh (ponsel): geser kartu lalu lepaskan di atas portal.
      var touch = null;
      card.addEventListener('touchstart', function (e) { if (done) return; var t = e.touches[0]; touch = { x: t.clientX, y: t.clientY }; card.classList.add('dragging'); }, { passive: true });
      card.addEventListener('touchmove', function (e) {
        if (!touch) return; var t = e.touches[0];
        card.style.transform = 'translate(' + (t.clientX - touch.x) + 'px,' + (t.clientY - touch.y) + 'px) rotate(-3deg)';
        e.preventDefault();
      }, { passive: false });
      card.addEventListener('touchend', function (e) {
        if (!touch) return;
        var t = e.changedTouches[0]; touch = null;
        card.classList.remove('dragging'); card.style.transform = '';
        var target = document.elementFromPoint(t.clientX, t.clientY);
        var p = target && target.closest('.portal');
        if (p) choose(p.getAttribute('data-key'), p);
      });
      function choose(key, btn) {
        if (done) return;
        done = true;
        buttons.forEach(function (b) { b.disabled = true; });
        card.classList.add('sent');
        ctx.submit(key).then(function (res) {
          if (!res) { done = false; card.classList.remove('sent'); buttons.forEach(function (b) { b.disabled = false; }); return; }
          btn.classList.add(res.correct ? 'right' : 'wrong');
          if (!res.correct) {
            var good = buttons.filter(function (b) { return res.answer_display && res.answer_display.indexOf(b.querySelector('b').textContent) === 0; })[0];
            if (good) good.classList.add('right');
          }
          graph.classList.remove('hidden');
          var p = new SC.Plane(graph, { range: round.range });
          p.addLine({ m: SC.parseNum(round.lines[0].m), c: SC.parseNum(round.lines[0].c), cls: 'thick', label: round.eq1, animate: !SC.reducedMotion() });
          p.addLine({ m: SC.parseNum(round.lines[1].m), c: SC.parseNum(round.lines[1].c), cls: 'teal thick' + (key === 'berimpit' || round.lines[0].m === round.lines[1].m && round.lines[0].c === round.lines[1].c ? ' dashed' : ''), label: round.eq2, animate: !SC.reducedMotion() });
          p.render();
        });
      }
      return { intro: 'Kartu ' + (index + 1) + ': bandingkan gradien kedua garis, lalu seret kartunya ke portal yang tepat. Semakin cepat, semakin besar bonusnya!' };
    }
  };
})(window.SC);
