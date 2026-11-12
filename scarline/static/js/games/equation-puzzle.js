/* GAME 4 — Equation Puzzle: drag & drop (atau ketuk) potongan rumus ke slot. */
(function (SC) {
  'use strict';
  var el = SC.el;
  SC.Games['equation-puzzle'] = {
    render: function (ctx, round) {
      var area = ctx.area();
      area.appendChild(el('div', { class: 'index-card', style: 'margin-bottom:14px' }, [el('span', { class: 'eyebrow', text: 'Teka-teki' }), el('p', { style: 'margin:0;font-weight:800', text: round.prompt })]));
      var slotsBox = el('div', { class: 'slots', 'aria-label': 'Slot persamaan' });
      var tray = el('div', { class: 'tiles', 'aria-label': 'Potongan rumus' });
      area.appendChild(slotsBox);
      area.appendChild(el('p', { class: 'small muted', style: 'margin:10px 0 6px', text: 'Potongan tersedia (seret ke slot, atau ketuk potongan lalu ketuk slot):' }));
      area.appendChild(tray);
      var check = el('button', { class: 'btn btn-primary', type: 'button', text: 'PERIKSA SUSUNAN' });
      var reset = el('button', { class: 'btn btn-ghost', type: 'button', text: 'Kosongkan' });
      area.appendChild(el('div', { class: 'row', style: 'margin-top:14px' }, [check, reset]));

      var slots = [];
      for (var i = 0; i < round.slots; i++) { var sl = el('div', { class: 'slot', 'data-slot': i }); slots.push(sl); slotsBox.appendChild(sl); }
      var tiles = {};
      var picked = null, locked = false;
      round.tiles.forEach(function (t) {
        var node = el('div', { class: 'tile', tabindex: 0, role: 'button', 'data-id': t.id, text: t.text });
        tiles[t.id] = node;
        tray.appendChild(node);
        node.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); tap(node); } });
        enableDrag(node);
      });
      function tap(node) {
        if (locked) return;
        if (node.parentNode.classList.contains('slot')) { tray.appendChild(node); picked = null; mark(); return; }
        picked = picked === node ? null : node;
        mark();
      }
      function mark() { Object.keys(tiles).forEach(function (k) { tiles[k].classList.toggle('picked', tiles[k] === picked); }); }
      slots.forEach(function (sl) {
        sl.addEventListener('click', function () {
          if (locked || !picked) return;
          place(picked, sl); picked = null; mark();
        });
      });
      function place(node, sl) {
        var existing = sl.querySelector('.tile');
        if (existing && existing !== node) tray.appendChild(existing);
        sl.appendChild(node);
        slots.forEach(function (x) { x.classList.remove('ok'); });
      }
      function enableDrag(node) {
        var start = null, ghost = null, moved = false;
        node.addEventListener('pointerdown', function (e) {
          if (locked) return;
          start = { x: e.clientX, y: e.clientY }; moved = false;
          node.setPointerCapture(e.pointerId);
        });
        node.addEventListener('pointermove', function (e) {
          if (!start) return;
          if (!moved && Math.abs(e.clientX - start.x) + Math.abs(e.clientY - start.y) < 6) return;
          moved = true;
          if (!ghost) { ghost = node.cloneNode(true); ghost.classList.add('dragging'); document.body.appendChild(ghost); node.style.opacity = '.35'; }
          ghost.style.left = (e.clientX - ghost.offsetWidth / 2) + 'px';
          ghost.style.top = (e.clientY - ghost.offsetHeight / 2) + 'px';
          var over = document.elementFromPoint(e.clientX, e.clientY);
          slots.forEach(function (sl) { sl.classList.toggle('over', !!over && sl.contains(over)); });
        });
        function end(e) {
          if (!start) return;
          if (moved) {
            var over = document.elementFromPoint(e.clientX, e.clientY);
            var target = slots.filter(function (sl) { return over && sl.contains(over); })[0];
            if (target) place(node, target);
            else if (over && tray.contains(over)) tray.appendChild(node);
          } else { tap(node); }
          if (ghost) { ghost.remove(); ghost = null; }
          node.style.opacity = '';
          slots.forEach(function (sl) { sl.classList.remove('over'); });
          start = null;
        }
        node.addEventListener('pointerup', end);
        node.addEventListener('pointercancel', function () { if (ghost) ghost.remove(); ghost = null; start = null; node.style.opacity = ''; });
      }
      reset.addEventListener('click', function () { if (locked) return; slots.forEach(function (sl) { var t = sl.querySelector('.tile'); if (t) tray.appendChild(t); }); });
      check.addEventListener('click', function () {
        if (locked) return;
        var ans = slots.map(function (sl) { var t = sl.querySelector('.tile'); return t ? t.getAttribute('data-id') : null; });
        if (ans.indexOf(null) >= 0) { ctx.say('hint', 'Masih ada slot kosong. Isi semua slot dulu, ya!', 'bad'); return; }
        ctx.submit(ans).then(function (res) {
          if (!res) return;
          if (res.correct) { locked = true; slots.forEach(function (sl) { sl.classList.add('ok'); }); }
          else if (res.done) { locked = true; }
        });
      });
      return { intro: 'Rumus SCAR berantakan! Susun potongannya ke slot dengan urutan yang benar. Awas potongan pengecoh!' };
    }
  };
})(window.SC);
