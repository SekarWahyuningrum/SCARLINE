/* SCARLINE Quiz — perender soal & pelari kuis (mini quiz, Training Zone, Tantangan Harian).
 * Kunci jawaban TIDAK ada di browser: setiap jawaban dinilai oleh server.
 */
(function (SC) {
  'use strict';
  var el = SC.el;
  var LETTERS = ['A', 'B', 'C', 'D', 'E', 'F'];
  var TYPE_LABEL = { mc: 'Pilihan ganda', tf: 'Benar atau salah', num: 'Isian angka', point: 'Tentukan koordinat titik', line: 'Lengkapi persamaan y = mx + c', match: 'Memasangkan garis' };

  /** Render satu soal. Mengembalikan { el, getAnswer, setAnswer, lock, mark } */
  SC.renderQuestion = function (q, opts) {
    opts = opts || {};
    var root = el('div', { class: 'question' });
    var answer = null;
    var locked = false;
    var onChange = opts.onChange || function () {};
    root.appendChild(el('div', { class: 'qtype', text: (TYPE_LABEL[q.type] || 'Soal') + (q.topic ? ' · ' + q.topic.replace('-', ' & ') : '') }));
    root.appendChild(el('p', { class: 'prompt', text: q.prompt }));

    var body = el('div', { class: 'qbody' });
    root.appendChild(body);
    var api = { el: root, mark: function () {} };

    if (q.graph && q.type !== 'point') {
      var g = el('div', { style: 'max-width:340px;margin:0 auto 16px' });
      body.appendChild(g);
      setTimeout(function () { SC.Plane.fromSpec(g, q.graph); }, 0);
    }

    if (q.type === 'mc' || q.type === 'tf') {
      var options = q.type === 'tf' ? ['Benar', 'Salah'] : q.options;
      var grid = el('div', { class: 'options' });
      var btns = options.map(function (txt, i) {
        var b = el('button', { type: 'button', class: 'opt' }, [el('span', { class: 'key', text: q.type === 'tf' ? (i === 0 ? 'B' : 'S') : LETTERS[i] }), el('span', { text: txt })]);
        b.addEventListener('click', function () {
          if (locked) return;
          btns.forEach(function (x) { x.classList.remove('sel'); });
          b.classList.add('sel');
          answer = q.type === 'tf' ? i === 0 : i;
          onChange(answer);
        });
        grid.appendChild(b);
        return b;
      });
      body.appendChild(grid);
      api.setAnswer = function (v) {
        if (v === null || v === undefined) return;
        var idx = q.type === 'tf' ? (v ? 0 : 1) : v;
        if (btns[idx]) { btns[idx].classList.add('sel'); answer = v; }
      };
      api.mark = function (correct) {
        btns.forEach(function (b) { b.disabled = true; if (b.classList.contains('sel')) b.classList.add(correct ? 'right' : 'wrong'); });
      };
    } else if (q.type === 'num') {
      var inp = el('input', { class: 'num-input', style: 'width:160px', inputmode: 'decimal', 'aria-label': 'Jawaban', placeholder: 'mis. -1/2' });
      inp.addEventListener('input', function () { answer = inp.value.trim() || null; onChange(answer); });
      inp.addEventListener('keydown', function (e) { if (e.key === 'Enter' && opts.onEnter) opts.onEnter(); });
      body.appendChild(el('div', { class: 'row' }, [el('b', { text: 'Jawaban:' }), inp, el('span', { class: 'small muted', text: 'Boleh bilangan bulat, desimal, atau pecahan (3/4).' })]));
      api.setAnswer = function (v) { if (v !== null && v !== undefined) { inp.value = v; answer = v; } };
      api.mark = function () { inp.disabled = true; };
      api.focus = function () { inp.focus(); };
    } else if (q.type === 'point') {
      var holder = el('div', { style: 'max-width:420px;margin:0 auto' });
      var info = el('p', { class: 'center small', text: 'Klik bidang koordinat untuk memilih titik.' });
      body.appendChild(holder); body.appendChild(info);
      var plane = new SC.Plane(holder, {
        range: q.range || 6, clickable: true,
        onClick: function (w) {
          if (locked) return;
          answer = [w.x, w.y];
          plane.points = [{ x: w.x, y: w.y, label: SC.pt(w.x, w.y) }];
          plane.render();
          info.textContent = 'Titik dipilih: ' + SC.pt(w.x, w.y) + ' — ' + SC.quadrant(w.x, w.y);
          onChange(answer);
        }
      });
      plane.render();
      api.setAnswer = function (v) { if (v) { answer = v; plane.points = [{ x: v[0], y: v[1], label: SC.pt(v[0], v[1]) }]; plane.render(); info.textContent = 'Titik dipilih: ' + SC.pt(v[0], v[1]); } };
      api.mark = function (correct, display) {
        if (plane.points[0]) plane.points[0].cls = correct ? 'ok' : 'bad';
        plane.render();
      };
    } else if (q.type === 'line') {
      var mIn = el('input', { class: 'num-input', inputmode: 'decimal', 'aria-label': 'Nilai m (gradien)', placeholder: 'm' });
      var cIn = el('input', { class: 'num-input', inputmode: 'decimal', 'aria-label': 'Nilai c (konstanta)', placeholder: 'c' });
      var preview = el('div', { style: 'max-width:300px;margin:14px auto 0' });
      var pv = null;
      function upd() {
        answer = (mIn.value.trim() || cIn.value.trim()) ? { m: mIn.value.trim(), c: cIn.value.trim() } : null;
        var m = SC.parseNum(mIn.value), c = SC.parseNum(cIn.value);
        if (!pv) { pv = new SC.Plane(preview, { range: 8 }); }
        pv.clear();
        if (isFinite(m) && isFinite(c)) pv.addLine({ m: m, c: c, label: SC.eq(m, c) });
        pv.render();
        onChange(answer);
      }
      mIn.addEventListener('input', upd); cIn.addEventListener('input', upd);
      body.appendChild(el('div', { class: 'line-input' }, ['y =', mIn, 'x +', cIn]));
      body.appendChild(el('p', { class: 'small muted', text: 'Contoh: untuk y = −2x + 3 isi m = -2 dan c = 3. Jika c negatif, tulis tanda minusnya (c = -1). Pecahan boleh, mis. 1/2.' }));
      body.appendChild(preview);
      setTimeout(upd, 0);
      api.setAnswer = function (v) { if (v) { mIn.value = v.m || ''; cIn.value = v.c || ''; setTimeout(upd, 0); } };
      api.mark = function () { mIn.disabled = true; cIn.disabled = true; };
    } else if (q.type === 'match') {
      var pairs = [];
      var pick = null;
      var mg = el('div', { class: 'match-grid' });
      var status = el('p', { class: 'small muted', text: 'Klik dua garis untuk memasangkannya. Klik garis yang sudah berpasangan untuk melepasnya.' });
      var items = q.items.map(function (txt, i) {
        var b = el('button', { type: 'button', class: 'match-item', text: txt });
        b.addEventListener('click', function () {
          if (locked) return;
          var existing = pairs.findIndex(function (p) { return p[0] === i || p[1] === i; });
          if (existing >= 0) { pairs.splice(existing, 1); pick = null; return refresh(); }
          if (pick === null) { pick = i; return refresh(); }
          if (pick === i) { pick = null; return refresh(); }
          pairs.push([pick, i]); pick = null; refresh();
        });
        mg.appendChild(b);
        return b;
      });
      function refresh() {
        items.forEach(function (b, i) {
          b.classList.toggle('sel', pick === i);
          var pi = pairs.findIndex(function (p) { return p[0] === i || p[1] === i; });
          if (pi >= 0) b.setAttribute('data-pair', String(pi % 3)); else b.removeAttribute('data-pair');
        });
        answer = pairs.length ? pairs.map(function (p) { return p.slice(); }) : null;
        status.textContent = pairs.length + ' pasangan dibuat.';
        onChange(answer);
      }
      body.appendChild(mg); body.appendChild(status);
      api.setAnswer = function (v) { if (v) { pairs = v.map(function (p) { return p.slice(); }); refresh(); } };
      api.mark = function () { items.forEach(function (b) { b.disabled = true; }); };
    }

    api.getAnswer = function () { return answer; };
    api.lock = function () { locked = true; };
    if (!api.setAnswer) api.setAnswer = function () {};
    return api;
  };

  function feedbackBlock(res) {
    var wrap = el('div', { class: 'feedback' });
    var say = el('div', { class: 'scar-say ' + (res.correct ? 'ok' : 'bad') }, [SC.scarSvg(res.correct ? 'happy' : 'encourage', 80), el('div', { class: 'bubble' })]);
    var bubbleHtml = '<b>' + SC.esc(res.scar || (res.correct ? 'Benar!' : 'Belum tepat.')) + '</b>';
    if (!res.correct && res.feedback) bubbleHtml += '<br>' + SC.esc(res.feedback);
    say.querySelector('.bubble').innerHTML = bubbleHtml;
    wrap.appendChild(say);
    if (res.explain || res.answer_display) {
      wrap.appendChild(el('div', { class: 'explain', html: (res.answer_display ? '<b>Jawaban benar:</b> ' + SC.esc(res.answer_display) + '<br>' : '') + (res.explain ? '<b>Pembahasan:</b> ' + SC.esc(res.explain) : '') }));
    }
    return wrap;
  }
  SC.feedbackBlock = feedbackBlock;

  /** Panel hasil akhir (dipakai kuis & game). */
  SC.resultPanel = function (data, opts) {
    opts = opts || {};
    var pct = data.percent !== undefined ? Math.round(data.percent) : data.score;
    var good = pct >= 70;
    var p = el('div', { class: 'result-panel' });
    p.appendChild(SC.scarSvg(good ? 'celebrate' : 'encourage', 150));
    p.appendChild(el('div', { class: 'big-score', text: (data.max_score ? data.score + ' poin' : pct) }));
    var sub = data.max_score ? (pct + '% dari ' + data.max_score + ' poin maksimal · ' + data.correct + '/' + data.total + ' benar') : (data.correct + ' dari ' + data.total + ' jawaban benar');
    p.appendChild(el('p', { class: 'muted', text: sub }));
    p.appendChild(el('div', { html: SC.stars(data.stars || 0) }));
    p.appendChild(el('p', { style: 'font-weight:800;margin-top:10px', text: data.scar || '' }));
    var xpTxt = data.xp_awarded > 0 ? '+' + data.xp_awarded + ' XP diperoleh!' : (opts.noXpText || 'Tidak ada XP baru — XP hanya diberikan jika kamu memecahkan rekor terbaikmu.');
    p.appendChild(el('p', { class: 'chip ' + (data.xp_awarded > 0 ? 'chip-yellow' : ''), text: xpTxt }));
    if (data.stats) {
      p.appendChild(el('p', { class: 'small muted', style: 'margin-top:10px', text: 'Total XP: ' + data.stats.total_xp + ' · Level ' + data.stats.level.level + ' (' + data.stats.level.name + ')' }));
      SC.updateHeaderXP(data.stats);
    }
    SC.celebrateAchievements(data.new_achievements);
    var actions = el('div', { class: 'row', style: 'justify-content:center;margin-top:16px' });
    (opts.actions || []).forEach(function (a) { actions.appendChild(a); });
    p.appendChild(actions);
    return p;
  };

  /** Kuis berurutan dengan umpan balik per soal. */
  SC.QuizRunner = function (mount, cfg) {
    var state = { run: null, i: 0, score: 0 };
    function err(msg) { mount.innerHTML = ''; mount.appendChild(el('div', { class: 'notice error', text: msg })); var b = el('button', { class: 'btn btn-sm', type: 'button', text: 'Coba lagi' }); b.onclick = start; mount.appendChild(b); }

    function start() {
      mount.innerHTML = '<p class="center"><span class="spin" style="display:inline-block;width:22px;height:22px;border:3px solid var(--navy);border-right-color:transparent;border-radius:50%;animation:spin .7s linear infinite"></span> SCAR menyiapkan soal...</p>';
      SC.api('/api/runs', { kind: cfg.kind, ref: cfg.ref }).then(function (r) {
        if (!r.ok) return err(r.data.error || 'Gagal memulai.');
        state.run = r.data; state.i = 0; state.score = 0;
        show();
      });
    }

    function show() {
      var run = state.run, q = run.items[state.i];
      mount.innerHTML = '';
      var top = el('div', { class: 'quiz-top' }, [
        el('span', { class: 'chip chip-navy', text: 'Soal ' + (state.i + 1) + ' / ' + run.total }),
        el('span', { class: 'chip', text: 'Benar: ' + state.score })
      ]);
      var bar = el('div', { class: 'ruler teal', style: 'flex:1;min-width:120px' }, [el('div', { class: 'fill', style: 'width:' + (state.i * 100 / run.total) + '%' })]);
      top.insertBefore(bar, top.children[1]);
      mount.appendChild(top);
      var card = el('div', { class: 'qcard' });
      var view = SC.renderQuestion(q, { onEnter: function () { check.click(); } });
      card.appendChild(view.el);
      var msg = el('p', { class: 'small', style: 'color:var(--red);font-weight:700;min-height:1.2em', 'aria-live': 'polite' });
      var check = el('button', { class: 'btn btn-primary', type: 'button', text: 'Periksa Jawaban' });
      var fbHolder = el('div', {});
      card.appendChild(msg);
      card.appendChild(el('div', { class: 'row' }, [check]));
      card.appendChild(fbHolder);
      mount.appendChild(card);
      if (view.focus) view.focus();

      check.addEventListener('click', function () {
        var ans = view.getAnswer();
        if (ans === null || ans === undefined || ans === '') { msg.textContent = 'Jawab dulu, ya! SCAR menunggu.'; return; }
        msg.textContent = '';
        SC.busy(check, true, 'Memeriksa...');
        SC.api('/api/runs/' + run.run_id + '/answer', { index: state.i, answer: ans }).then(function (r) {
          if (r.status === 422) { SC.busy(check, false); msg.textContent = r.data.message || r.data.error; return; }
          if (!r.ok) { SC.busy(check, false); msg.textContent = r.data.error || 'Gagal memeriksa jawaban.'; return; }
          view.lock(); view.mark(r.data.correct);
          if (r.data.correct) state.score++;
          fbHolder.appendChild(feedbackBlock(r.data));
          check.remove();
          var last = state.i === run.total - 1;
          var next = el('button', { class: 'btn btn-teal', type: 'button', text: last ? 'Lihat Hasil' : 'Soal Berikutnya →', style: 'margin-top:14px' });
          next.addEventListener('click', function () { if (last) finish(); else { state.i++; show(); mount.scrollIntoView({ behavior: 'smooth', block: 'start' }); } });
          fbHolder.appendChild(next);
          next.focus();
        });
      });
    }

    function finish() {
      mount.innerHTML = '<p class="center">Menyimpan hasil...</p>';
      SC.api('/api/runs/' + state.run.run_id + '/finish', {}).then(function (r) {
        if (!r.ok) return err(r.data.error || 'Gagal menyimpan hasil.');
        mount.innerHTML = '';
        var again = el('button', { class: 'btn', type: 'button', text: 'Ulangi' });
        again.onclick = start;
        var actions = [again].concat(cfg.extraActions ? cfg.extraActions(r.data) : []);
        mount.appendChild(SC.resultPanel(r.data, { actions: actions, noXpText: cfg.noXpText && cfg.noXpText(r.data) }));
        if (cfg.onFinish) cfg.onFinish(r.data);
      });
    }

    return { start: start };
  };
})(window.SC);
