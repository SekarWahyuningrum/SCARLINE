/* SCARLINE FX — efek suara, musik latar, confetti, level-up, lencana, tema, loading,
 * animasi gulir, penghitung, pencarian materi, bookmark, dropdown, dan tombol kembali ke atas.
 * Semua efek menghormati pengaturan "kurangi animasi" (prefers-reduced-motion). */
(function (SC) {
  'use strict';
  var el = SC.el;
  var root = document.documentElement;
  var body = document.body;
  var prefs = {};
  try { prefs = JSON.parse(body.getAttribute('data-prefs') || '{}'); } catch (e) { prefs = {}; }
  var logged = !!body.getAttribute('data-logged');
  var v2 = !!body.getAttribute('data-v2');

  function store(key, val) { try { if (val === undefined) return localStorage.getItem(key); localStorage.setItem(key, val); } catch (e) { return null; } }
  SC.reducedMotion = function () { return root.getAttribute('data-motion') === 'reduce'; };

  /** Simpan preferensi ke akun (jika migrasi 002 aktif) dan ke browser. */
  SC.savePref = function (values) {
    Object.keys(values).forEach(function (k) { prefs[k] = values[k]; });
    if (logged && v2) return SC.api('/api/prefs', values);
    return Promise.resolve({ ok: true });
  };

  /* ------------------------------------------------------------ audio */
  var ctx = null;
  function audio() {
    if (!ctx) { var AC = window.AudioContext || window.webkitAudioContext; if (!AC) return null; ctx = new AC(); }
    if (ctx.state === 'suspended') ctx.resume();
    return ctx;
  }
  function sfxOn() { var s = store('scarline-sfx'); if (s !== null) return s === '1'; return prefs.sfx !== false; }
  function tone(freq, start, dur, type, vol) {
    var a = audio(); if (!a) return;
    var o = a.createOscillator(), g = a.createGain();
    o.type = type || 'sine'; o.frequency.value = freq;
    var t = a.currentTime + start;
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(vol || 0.12, t + 0.015);
    g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    o.connect(g); g.connect(a.destination);
    o.start(t); o.stop(t + dur + 0.05);
  }
  var SOUNDS = {
    click: function () { tone(660, 0, 0.06, 'triangle', 0.05); },
    start: function () { tone(392, 0, 0.12, 'triangle'); tone(523, 0.1, 0.16, 'triangle'); },
    correct: function () { tone(523.25, 0, 0.14, 'triangle'); tone(783.99, 0.1, 0.22, 'triangle'); },
    wrong: function () { tone(220, 0, 0.18, 'sawtooth', 0.05); tone(196, 0.12, 0.22, 'sawtooth', 0.05); },
    done: function () { tone(440, 0, 0.15, 'triangle'); tone(554, 0.12, 0.15, 'triangle'); tone(659, 0.24, 0.3, 'triangle'); },
    win: function () { [523, 659, 784, 1047].forEach(function (f, i) { tone(f, i * 0.09, 0.28, 'triangle', 0.1); }); },
    level: function () { [392, 494, 587, 784, 988].forEach(function (f, i) { tone(f, i * 0.08, 0.35, 'square', 0.05); }); },
    badge: function () { [880, 1175, 1568].forEach(function (f, i) { tone(f, i * 0.07, 0.4, 'sine', 0.08); }); }
  };
  SC.sfx = function (name) { if (!sfxOn() || !SOUNDS[name]) return; try { SOUNDS[name](); } catch (e) { /* audio diblokir */ } };

  /* Musik latar: arpeggio pentatonik lembut yang dibangkitkan WebAudio (tanpa file audio). */
  var music = { on: false, timer: null, step: 0, gain: null };
  var SCALE = [261.63, 293.66, 329.63, 392.0, 440.0, 523.25, 587.33, 659.25];
  var CHORDS = [[0, 2, 4, 7], [1, 3, 5, 7], [0, 3, 5, 6], [2, 4, 6, 7]];
  function musicNote() {
    var a = audio(); if (!a || !music.gain) return;
    var chord = CHORDS[Math.floor(music.step / 8) % CHORDS.length];
    var idx = chord[music.step % 4] + (music.step % 8 >= 4 ? 0 : 0);
    var f = SCALE[idx] * (music.step % 8 >= 4 ? 1 : 0.5);
    var o = a.createOscillator(), g = a.createGain();
    o.type = 'sine'; o.frequency.value = f;
    var t = a.currentTime;
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(0.5, t + 0.04);
    g.gain.exponentialRampToValueAtTime(0.0001, t + 1.4);
    o.connect(g); g.connect(music.gain);
    o.start(t); o.stop(t + 1.5);
    if (music.step % 8 === 0) { var b = a.createOscillator(), bg = a.createGain(); b.type = 'triangle'; b.frequency.value = SCALE[chord[0]] / 4; bg.gain.setValueAtTime(0.0001, t); bg.gain.exponentialRampToValueAtTime(0.35, t + 0.2); bg.gain.exponentialRampToValueAtTime(0.0001, t + 3.2); b.connect(bg); bg.connect(music.gain); b.start(t); b.stop(t + 3.3); }
    music.step++;
  }
  SC.music = {
    start: function () {
      var a = audio(); if (!a || music.on) return;
      music.gain = a.createGain(); music.gain.gain.value = 0.045; music.gain.connect(a.destination);
      music.on = true; musicNote(); music.timer = setInterval(musicNote, 420);
      syncMusicButtons();
    },
    stop: function () {
      music.on = false; clearInterval(music.timer);
      if (music.gain) { try { music.gain.disconnect(); } catch (e) { /* abaikan */ } music.gain = null; }
      syncMusicButtons();
    },
    isOn: function () { return music.on; }
  };
  function musicWanted() { var s = store('scarline-music'); if (s !== null) return s === '1'; return !!prefs.music; }
  function syncMusicButtons() {
    document.querySelectorAll('[data-music-toggle]').forEach(function (b) { b.setAttribute('aria-pressed', music.on ? 'true' : 'false'); b.classList.toggle('is-on', music.on); });
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-music-toggle]');
    if (!b) return;
    if (music.on) { SC.music.stop(); store('scarline-music', '0'); SC.savePref({ music: false }); }
    else { SC.music.start(); store('scarline-music', '1'); SC.savePref({ music: true }); SC.toast('Musik latar menyala', 'Klik ikon musik lagi untuk mematikan.', 'happy'); }
  });
  // Browser hanya mengizinkan audio setelah interaksi pertama.
  if (musicWanted()) {
    var kick = function () { document.removeEventListener('pointerdown', kick); document.removeEventListener('keydown', kick); if (musicWanted()) SC.music.start(); };
    document.addEventListener('pointerdown', kick); document.addEventListener('keydown', kick);
  }

  /* ------------------------------------------------------------ tema */
  SC.setTheme = function (t, save) {
    var resolved = t === 'system' ? (window.matchMedia && matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light') : t;
    root.setAttribute('data-theme', resolved);
    root.setAttribute('data-pref-theme', t);
    store('scarline-theme', t);
    if (save) SC.savePref({ theme: t });
  };
  document.addEventListener('click', function (e) {
    if (!e.target.closest('[data-theme-toggle]')) return;
    SC.setTheme(root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark', true);
    SC.sfx('click');
  });
  SC.setMotion = function (reduce) {
    if (reduce || (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches)) root.setAttribute('data-motion', 'reduce');
    else root.removeAttribute('data-motion');
    store('scarline-motion', reduce ? 'reduce' : '');
  };

  /* ------------------------------------------------------------ confetti */
  SC.confetti = function (opts) {
    if (SC.reducedMotion()) return;
    opts = opts || {};
    var cv = el('canvas', { class: 'confetti-canvas', 'aria-hidden': 'true' });
    body.appendChild(cv);
    var w = cv.width = innerWidth, h = cv.height = innerHeight, c2 = cv.getContext('2d');
    var colors = ['#C87945', '#648B83', '#E6C878', '#25334A', '#B5523B', '#FFFDF7'];
    var parts = [];
    for (var i = 0; i < (opts.count || 140); i++) {
      parts.push({ x: w / 2 + (Math.random() - 0.5) * w * 0.3, y: h * 0.35, vx: (Math.random() - 0.5) * 14, vy: -Math.random() * 13 - 4,
        r: 4 + Math.random() * 5, c: colors[i % colors.length], a: Math.random() * 6, va: (Math.random() - 0.5) * 0.3, shape: i % 3 });
    }
    var t0 = performance.now();
    (function frame(now) {
      var dt = Math.min(2, (now - (frame.last || now)) / 16); frame.last = now;
      c2.clearRect(0, 0, w, h);
      parts.forEach(function (p) {
        p.vy += 0.35 * dt; p.vx *= 0.99; p.x += p.vx * dt; p.y += p.vy * dt; p.a += p.va * dt;
        c2.save(); c2.translate(p.x, p.y); c2.rotate(p.a); c2.fillStyle = p.c;
        if (p.shape === 0) c2.fillRect(-p.r, -p.r / 2, p.r * 2, p.r);
        else if (p.shape === 1) { c2.beginPath(); c2.arc(0, 0, p.r / 1.6, 0, 7); c2.fill(); }
        else { c2.beginPath(); c2.moveTo(0, -p.r); c2.lineTo(p.r, p.r); c2.lineTo(-p.r, p.r); c2.fill(); }
        c2.restore();
      });
      if (now - t0 < 3200) requestAnimationFrame(frame); else cv.remove();
    })(t0);
  };

  /* ------------------------------------------------------------ modal */
  SC.modal = function (content, opts) {
    opts = opts || {};
    var rootEl = document.getElementById('modal-root') || body;
    var back = el('div', { class: 'modal-back', role: 'presentation' });
    var box = el('div', { class: 'modal ' + (opts.cls || ''), role: 'dialog', 'aria-modal': 'true', 'aria-label': opts.label || 'Pemberitahuan' });
    var close = el('button', { class: 'modal-x', type: 'button', 'aria-label': 'Tutup' }, ['×']);
    box.appendChild(close);
    box.appendChild(content);
    back.appendChild(box);
    rootEl.appendChild(back);
    var prev = document.activeElement;
    function done() { back.classList.add('out'); setTimeout(function () { back.remove(); if (prev && prev.focus) prev.focus(); }, 220); document.removeEventListener('keydown', esc); }
    function esc(e) { if (e.key === 'Escape') done(); }
    close.addEventListener('click', done);
    back.addEventListener('click', function (e) { if (e.target === back) done(); });
    document.addEventListener('keydown', esc);
    setTimeout(function () { var f = box.querySelector('[data-autofocus]') || close; f.focus(); }, 30);
    return { close: done, el: box };
  };

  /* ------------------------------------------------------------ XP, level-up, lencana */
  function countUp(node, from, to, suffix) {
    if (SC.reducedMotion() || from === to) { node.textContent = to + (suffix || ''); return; }
    var t0 = performance.now(), dur = 900;
    (function f(now) {
      var k = Math.min(1, (now - t0) / dur), e = 1 - Math.pow(1 - k, 3);
      node.textContent = Math.round(from + (to - from) * e) + (suffix || '');
      if (k < 1) requestAnimationFrame(f);
    })(t0);
  }
  SC.countUp = countUp;
  var queue = [];
  function nextCelebration() {
    if (document.querySelector('.modal-back') || !queue.length) return;
    var item = queue.shift();
    var m = SC.modal(item.content, { cls: 'celebrate-modal', label: item.label });
    SC.sfx(item.sound); SC.confetti();
    var obs = new MutationObserver(function () { if (!document.body.contains(m.el)) { obs.disconnect(); setTimeout(nextCelebration, 250); } });
    obs.observe(document.getElementById('modal-root') || body, { childList: true, subtree: true });
  }
  function celebrate(content, sound, label) { queue.push({ content: content, sound: sound, label: label }); nextCelebration(); }

  SC.updateHeaderXP = function (stats) {
    if (!stats) return;
    var xpEl = document.querySelector('[data-header-xp]');
    if (xpEl) {
      var prevXP = parseInt(xpEl.textContent, 10) || 0;
      countUp(xpEl, prevXP, stats.total_xp, ' XP');
      var prevLevel = parseInt(xpEl.getAttribute('data-level'), 10) || 1;
      if (stats.level && stats.level.level > prevLevel) {
        xpEl.setAttribute('data-level', stats.level.level);
        celebrate(el('div', { class: 'levelup' }, [
          el('div', { class: 'lv-burst' }, [SC.scarSvg('celebrate', 150)]),
          el('p', { class: 'eyebrow', text: 'Level up!' }),
          el('h2', { text: 'Level ' + stats.level.level + ' — ' + stats.level.name }),
          el('p', { text: 'Total ' + stats.total_xp + ' XP. Luar biasa, terus jelajahi dunia SCARLINE!' }),
          el('button', { class: 'btn btn-primary', type: 'button', 'data-autofocus': '', text: 'Lanjutkan', onclick: function () { var x = document.querySelector('.modal-x'); if (x) x.click(); } })
        ]), 'level', 'Naik level');
      }
    }
    var lv = document.querySelector('.user-chip .lvl');
    if (lv && stats.level) lv.textContent = 'Lv ' + stats.level.level;
  };

  SC.celebrateAchievements = function (list) {
    (list || []).forEach(function (a) {
      var ic = document.querySelector('template#badge-icon-' + a.icon);
      celebrate(el('div', { class: 'badge-pop' }, [
        el('div', { class: 'badge-glow' }, [el('span', { class: 'medal big', html: ic ? ic.innerHTML : '★' })]),
        el('p', { class: 'eyebrow', text: 'Lencana baru!' }),
        el('h2', { text: a.title }),
        el('p', { text: a.description }),
        el('p', { class: 'chip chip-yellow', text: '+' + a.xp_bonus + ' XP bonus' }),
        el('div', { class: 'row', style: 'justify-content:center' }, [
          el('a', { class: 'btn', href: '/achievements', text: 'Galeri lencana' }),
          el('button', { class: 'btn btn-primary', type: 'button', 'data-autofocus': '', text: 'Hore!', onclick: function () { var x = document.querySelector('.modal-x'); if (x) x.click(); } })
        ])
      ]), 'badge', 'Lencana baru');
    });
  };

  /* ------------------------------------------------------------ loading screen */
  var loader = document.getElementById('loader');
  if (loader) {
    var msgs = ['Menyiapkan bidang koordinat...', 'SCAR mengasah pensil gradien...', 'Menggambar garis lurus pertama...', 'Membuka gerbang SCARLINE WORLD...'];
    var mi = 0, msgEl = loader.querySelector('[data-loader-msg]');
    var rot = setInterval(function () { mi = (mi + 1) % msgs.length; if (msgEl) msgEl.textContent = msgs[mi]; }, 650);
    var hide = function () { clearInterval(rot); loader.classList.add('done'); setTimeout(function () { loader.remove(); }, 500); try { sessionStorage.setItem('scarline-loaded', '1'); } catch (e) { /* abaikan */ } };
    var minWait = SC.reducedMotion() ? 0 : 1100, t0 = Date.now();
    var go = function () { setTimeout(hide, Math.max(0, minWait - (Date.now() - t0))); };
    if (document.readyState === 'complete') go(); else window.addEventListener('load', go);
    setTimeout(hide, 4000);
  }

  /* ------------------------------------------------------------ animasi gulir & penghitung */
  var revealEls = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && !SC.reducedMotion()) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        en.target.classList.add('in');
        var counters = en.target.querySelectorAll('[data-count]');
        if (en.target.hasAttribute('data-count')) counters = [en.target];
        Array.prototype.forEach.call(counters, function (c) { countUp(c, 0, parseInt(c.getAttribute('data-count'), 10) || 0, c.getAttribute('data-suffix') || ''); });
        io.unobserve(en.target);
      });
    }, { threshold: 0.15 });
    revealEls.forEach(function (r) { r.classList.add('pre'); io.observe(r); });
  }

  /* Kalimat SCAR muncul seperti diketik. */
  document.querySelectorAll('[data-typewriter]').forEach(function (b) {
    if (SC.reducedMotion()) return;
    var text = b.getAttribute('data-typewriter'), i = 0;
    b.textContent = '';
    b.classList.add('typing');
    var t = setInterval(function () { b.textContent = text.slice(0, ++i); if (i >= text.length) { clearInterval(t); b.classList.remove('typing'); } }, 28);
  });

  /* ------------------------------------------------------------ tombol kembali ke atas & topbar */
  var toTop = document.querySelector('[data-to-top]');
  var topbar = document.getElementById('topbar');
  var onScroll = function () {
    var y = window.scrollY;
    if (toTop) toTop.classList.toggle('show', y > 600);
    if (topbar) topbar.classList.toggle('scrolled', y > 8);
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
  if (toTop) toTop.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: SC.reducedMotion() ? 'auto' : 'smooth' }); });

  /* ------------------------------------------------------------ dropdown navigasi */
  document.addEventListener('click', function (e) {
    document.querySelectorAll('details[data-dd][open]').forEach(function (d) { if (!d.contains(e.target)) d.removeAttribute('open'); });
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') document.querySelectorAll('details[data-dd][open]').forEach(function (d) { d.removeAttribute('open'); var s = d.querySelector('summary'); if (s) s.focus(); });
  });

  /* ------------------------------------------------------------ efek klik (ripple) */
  document.addEventListener('pointerdown', function (e) {
    var b = e.target.closest('.btn, .opt, .action, .game-card');
    if (!b || SC.reducedMotion() || b.disabled) return;
    var r = b.getBoundingClientRect();
    var rp = el('span', { class: 'btn-ripple', style: 'left:' + (e.clientX - r.left) + 'px;top:' + (e.clientY - r.top) + 'px' });
    b.appendChild(rp);
    setTimeout(function () { rp.remove(); }, 600);
  });

  /* ------------------------------------------------------------ bookmark & favorit materi */
  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-toggle-list]');
    if (!b) return;
    var list = b.getAttribute('data-toggle-list');
    SC.busy(b, true, '...');
    SC.api('/api/bookmark', { slug: b.getAttribute('data-slug'), list: list }).then(function (r) {
      SC.busy(b, false);
      if (!r.ok) { SC.toast('Gagal menyimpan', r.data.error || 'Coba lagi.', 'think'); return; }
      var on = r.data.on;
      b.classList.toggle('btn-yellow', on);
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
      var label = b.querySelector('span');
      if (label) label.textContent = list === 'favorites' ? (on ? 'Favorit' : 'Jadikan favorit') : (on ? 'Ditandai' : 'Bookmark');
      SC.sfx('click');
      SC.toast(on ? (list === 'favorites' ? 'Ditambahkan ke favorit' : 'Materi ditandai') : 'Dihapus dari daftar', 'Lihat semuanya di SCAR\'s Diary.', 'happy');
    });
  });

  /* ------------------------------------------------------------ pencarian materi */
  var dlg = document.getElementById('search-dialog');
  if (dlg) {
    var input = document.getElementById('search-input'), results = document.getElementById('search-results');
    var index = null, active = 0;
    var norm = function (s) { return String(s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[−–]/g, '-'); };
    var load = function () {
      if (index) return Promise.resolve(index);
      return fetch('/search-index.json', { credentials: 'same-origin' }).then(function (r) { return r.json(); }).then(function (d) {
        index = d.map(function (it) { return Object.assign({}, it, { hay: norm(it.title + ' ' + it.sub + ' ' + it.text) }); });
        return index;
      }).catch(function () { index = []; return index; });
    };
    var render = function () {
      var q = norm(input.value.trim());
      results.innerHTML = '';
      if (!q) { results.appendChild(el('li', { class: 'muted small', text: 'Ketik kata kunci, misalnya “gradien”, “kuadran”, atau “tegak lurus”.' })); return; }
      var words = q.split(/\s+/);
      var hits = (index || []).filter(function (it) { return words.every(function (w) { return it.hay.indexOf(w) >= 0; }); }).slice(0, 12);
      if (!hits.length) { results.appendChild(el('li', { class: 'empty-hit' }, [SC.scarSvg('think', 48), el('span', { text: 'SCAR tidak menemukan “' + input.value + '”. Coba kata lain atau tanya SCAR AI Tutor.' })])); return; }
      active = Math.min(active, hits.length - 1);
      hits.forEach(function (it, i) {
        var a = el('a', { href: it.url, class: i === active ? 'on' : '' }, [el('b', { text: it.title }), el('small', { text: it.sub })]);
        results.appendChild(el('li', { role: 'option', 'aria-selected': i === active ? 'true' : 'false' }, [a]));
      });
    };
    SC.openSearch = function () { if (dlg.open) return; dlg.showModal(); input.value = ''; active = 0; load().then(render); setTimeout(function () { input.focus(); }, 20); };
    document.addEventListener('click', function (e) {
      if (e.target.closest('[data-search-open]')) SC.openSearch();
      if (e.target.closest('[data-search-close]')) dlg.close();
    });
    dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); });
    input.addEventListener('input', function () { active = 0; render(); });
    input.addEventListener('keydown', function (e) {
      var links = results.querySelectorAll('a');
      if (e.key === 'ArrowDown') { active = Math.min(links.length - 1, active + 1); render(); e.preventDefault(); }
      if (e.key === 'ArrowUp') { active = Math.max(0, active - 1); render(); e.preventDefault(); }
      if (e.key === 'Enter' && links[active]) { location.href = links[active].getAttribute('href'); }
    });
    document.addEventListener('keydown', function (e) {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); SC.openSearch(); }
    });
  }

  /* ------------------------------------------------------------ pengingat belajar */
  if (logged && prefs && window.Notification) {
    var rt = store('scarline-reminder');
    if (rt && Notification.permission === 'granted') {
      var check = function () {
        var now = new Date(), hm = ('0' + now.getHours()).slice(-2) + ':' + ('0' + now.getMinutes()).slice(-2);
        var today = now.toISOString().slice(0, 10);
        if (hm === rt && store('scarline-reminded') !== today) {
          store('scarline-reminded', today);
          new Notification('Waktunya belajar bersama SCAR!', { body: 'Selesaikan tantangan harianmu dan jaga learning streak-mu.', icon: '/static/img/favicon.svg' });
        }
      };
      setInterval(check, 30000); check();
    }
  }
})(window.SC);
