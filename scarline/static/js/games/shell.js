/* SCARLINE Game Shell — alur bersama kelima game:
 * petunjuk → mulai (server membuat ronde) → jawab (server menilai) → hasil (server menyimpan).
 * Setiap game mendaftar di SC.Games[slug] = { render(ctx, round, index) → { onResult(res) } }.
 */
(function (SC) {
  'use strict';
  var el = SC.el;
  SC.Games = SC.Games || {};

  SC.startGameShell = function (slug, title) {
    var intro = document.getElementById('intro');
    var play = document.getElementById('play');
    var startBtn = document.getElementById('start-game');
    var state = null;
    var timerId = null;

    function difficulty() { var r = document.querySelector('input[name=difficulty]:checked'); return r ? r.value : 'easy'; }

    function start() {
      SC.busy(startBtn, true, 'Menyiapkan...');
      SC.api('/api/runs', { kind: 'game', ref: slug, difficulty: difficulty() }).then(function (r) {
        SC.busy(startBtn, false);
        if (!r.ok) { document.getElementById('start-error').textContent = r.data.error || 'Gagal memulai permainan.'; return; }
        state = { run: r.data, i: 0, score: 0, hearts: r.data.hearts, t0: Date.now(), roundT0: Date.now(), correct: 0 };
        intro.classList.add('hidden');
        play.classList.remove('hidden');
        layout();
        showRound();
        clearInterval(timerId);
        timerId = setInterval(tick, 500);
      });
    }

    var hud, area, side, say, nextBtn;
    function layout() {
      play.innerHTML = '';
      hud = el('div', { class: 'hud' });
      area = el('div', { class: 'game-area' });
      side = el('div', { class: 'game-side stack' });
      say = el('div', { class: 'scar-say' }, [SC.scarSvg('welcome', 84), el('div', { class: 'bubble', 'data-scar-text': '', text: state.run.scar || 'Ayo mulai!' })]);
      nextBtn = el('button', { class: 'btn btn-teal hidden', type: 'button', text: 'Lanjut →' });
      nextBtn.addEventListener('click', advance);
      side.appendChild(say);
      side.appendChild(nextBtn);
      play.appendChild(hud);
      play.appendChild(el('div', { class: 'game-grid' }, [area, side]));
    }

    function tick() {
      var t = document.getElementById('hud-time');
      if (t && state) t.textContent = Math.floor((Date.now() - state.roundT0) / 1000) + ' dtk';
    }

    function drawHud() {
      var run = state.run;
      hud.innerHTML = '';
      hud.appendChild(el('span', { class: 'chip chip-navy', text: 'Ronde ' + Math.min(state.i + 1, run.total) + ' / ' + run.total }));
      hud.appendChild(el('span', { class: 'chip chip-orange', text: 'Skor: ' + state.score }));
      if (state.hearts !== null && state.hearts !== undefined) {
        var h = el('span', { class: 'chip hearts', 'aria-label': 'Nyawa ' + state.hearts });
        for (var k = 0; k < 3; k++) h.appendChild(el('span', { class: k < state.hearts ? '' : 'lost', text: '♥' }));
        hud.appendChild(h);
      } else {
        hud.appendChild(el('span', { class: 'chip', id: 'hud-tries', text: 'Kesempatan: ' + (state.triesLeft === undefined ? run.max_tries : state.triesLeft) }));
      }
      hud.appendChild(el('span', { class: 'chip', id: 'hud-time', text: '0 dtk' }));
      var bar = el('div', { class: 'ruler teal', style: 'flex:1;min-width:120px' }, [el('div', { class: 'fill', style: 'width:' + (state.i * 100 / run.total) + '%' })]);
      hud.appendChild(bar);
    }

    var current = null;
    var busy = false;
    function showRound() {
      state.triesLeft = state.run.max_tries;
      state.roundT0 = Date.now();
      drawHud();
      area.innerHTML = '';
      nextBtn.classList.add('hidden');
      var game = SC.Games[slug];
      current = game.render(ctx, state.run.items[state.i], state.i) || {};
      SC.scarSay(say, 'explain', current.intro || 'Ronde ' + (state.i + 1) + '. Kamu pasti bisa!');
    }

    function advance() {
      if (state.i >= state.run.total - 1 || state.over) finish();
      else { state.i++; showRound(); }
    }

    var ctx = {
      area: function () { return area; },
      side: function () { return side; },
      total: function () { return state.run.total; },
      say: function (mood, text, tone) { SC.scarSay(say, mood, text, tone); },
      submit: function (answer) {
        if (busy) return Promise.resolve(null);
        busy = true;
        return SC.api('/api/runs/' + state.run.run_id + '/answer', { index: state.i, answer: answer }).then(function (r) {
          busy = false;
          if (r.status === 422) { SC.scarSay(say, 'hint', SC.esc(r.data.message || 'Jawaban belum lengkap.'), 'bad'); return null; }
          if (!r.ok) { SC.scarSay(say, 'think', SC.esc(r.data.error || 'Gagal mengirim jawaban.'), 'bad'); if (r.status === 404) setTimeout(function () { location.reload(); }, 1600); return null; }
          var res = r.data;
          state.score = res.score;
          if (res.hearts !== null && res.hearts !== undefined) state.hearts = res.hearts;
          if (res.tries_left !== null && res.tries_left !== undefined) state.triesLeft = res.tries_left;
          var html;
          if (SC.sfx) SC.sfx(res.correct ? 'correct' : 'wrong');
          if (res.correct) {
            state.correct++;
            html = '<b>' + SC.esc(res.scar) + '</b><br>+' + res.points + ' poin' + (res.bonus ? ' (termasuk bonus kecepatan ' + res.bonus + ')' : '') + '.';
            SC.scarSay(say, 'happy', html, 'ok');
          } else {
            html = '<b>' + SC.esc(res.scar) + '</b><br>' + SC.esc(res.feedback || '');
            if (res.done || res.game_over) html += '<br><br><b>Jawaban:</b> ' + SC.esc(res.answer_display || '') + (res.explain ? '<br>' + SC.esc(res.explain) : '');
            SC.scarSay(say, res.done || res.game_over ? 'encourage' : 'hint', html, 'bad');
          }
          if (res.correct && res.explain) say.querySelector('.bubble').innerHTML += '<br><span class="small">' + SC.esc(res.explain) + '</span>';
          drawHud();
          if (current.onResult) current.onResult(res);
          if (res.game_over) { state.over = true; nextBtn.textContent = 'Lihat Hasil'; nextBtn.classList.remove('hidden'); }
          else if (res.done) {
            nextBtn.textContent = state.i >= state.run.total - 1 ? 'Lihat Hasil' : 'Ronde Berikutnya →';
            nextBtn.classList.remove('hidden');
            nextBtn.focus({ preventScroll: true });
          }
          return res;
        });
      }
    };

    function finish() {
      clearInterval(timerId);
      area.innerHTML = '<p class="center">Menyimpan hasil permainan...</p>';
      nextBtn.classList.add('hidden');
      SC.api('/api/runs/' + state.run.run_id + '/finish', {}).then(function (r) {
        play.innerHTML = '';
        if (!r.ok) { play.appendChild(el('div', { class: 'notice error', text: r.data.error || 'Gagal menyimpan hasil.' })); return; }
        var again = el('button', { class: 'btn btn-primary', type: 'button', text: 'Main Lagi' });
        again.addEventListener('click', function () { play.classList.add('hidden'); intro.classList.remove('hidden'); window.scrollTo({ top: 0, behavior: 'smooth' }); });
        var back = el('a', { class: 'btn', href: '/playground', text: 'Game lain' });
        var hist = el('a', { class: 'btn btn-ghost', href: location.pathname, text: 'Lihat riwayat' });
        var panel = SC.resultPanel(r.data, { actions: [again, back, hist] });
        panel.insertBefore(el('h2', { text: state.over ? 'Nyawa habis — tapi kamu sudah belajar banyak!' : title + ' selesai!' }), panel.firstChild);
        play.appendChild(panel);
      });
    }

    startBtn.addEventListener('click', start);
  };
})(window.SC);
