/* SCARLINE core — utilitas bersama (fetch + CSRF, toast, SCAR, pecahan). */
(function (global) {
  'use strict';

  var SC = global.SC || {};
  var csrfMeta = document.querySelector('meta[name="csrf-token"]');
  SC.csrf = csrfMeta ? csrfMeta.getAttribute('content') : '';

  /** POST/GET JSON ke server. Mengembalikan Promise {ok, status, data}. */
  SC.api = function (url, body, method) {
    var opts = {
      method: method || (body === undefined ? 'GET' : 'POST'),
      headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': SC.csrf, 'Accept': 'application/json' },
      credentials: 'same-origin'
    };
    if (body !== undefined) opts.body = JSON.stringify(body);
    return fetch(url, opts).then(function (res) {
      return res.json().catch(function () { return {}; }).then(function (data) {
        if (res.status === 401 && data.login) {
          SC.toast('Sesi berakhir', 'Silakan masuk kembali.', 'encourage');
          setTimeout(function () { global.location.href = data.login + '?next=' + encodeURIComponent(global.location.pathname); }, 1400);
        }
        return { ok: res.ok, status: res.status, data: data };
      });
    }).catch(function () {
      return { ok: false, status: 0, data: { error: 'Tidak dapat terhubung ke server. Periksa koneksi internetmu.' } };
    });
  };

  SC.el = function (tag, attrs, children) {
    var node = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (k) {
        var v = attrs[k];
        if (v === null || v === undefined || v === false) return;
        if (k === 'class') node.className = v;
        else if (k === 'text') node.textContent = v;
        else if (k === 'html') node.innerHTML = v;
        else if (k.indexOf('on') === 0 && typeof v === 'function') node.addEventListener(k.slice(2), v);
        else node.setAttribute(k, v === true ? '' : v);
      });
    }
    (children || []).forEach(function (c) {
      if (c === null || c === undefined) return;
      node.appendChild(typeof c === 'string' ? document.createTextNode(c) : c);
    });
    return node;
  };

  SC.esc = function (s) {
    return String(s === undefined || s === null ? '' : s).replace(/[&<>"']/g, function (ch) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch];
    });
  };

  /* ------------------------------------------------------------ SCAR */
  SC.scarSvg = function (mood, size) {
    var tpl = document.getElementById('scar-template');
    if (!tpl) return document.createElement('span');
    var svg = tpl.content.firstElementChild.cloneNode(true);
    svg.setAttribute('data-mood', mood || 'happy');
    if (size) { svg.setAttribute('width', size); svg.setAttribute('height', Math.round(size * 1.1)); }
    return svg;
  };

  /** Ubah ekspresi & kalimat SCAR di dalam elemen .scar-say */
  SC.scarSay = function (wrap, mood, text, tone) {
    if (!wrap) return;
    var svg = wrap.querySelector('.scar');
    var bubble = wrap.querySelector('[data-scar-text]');
    if (svg) {
      svg.setAttribute('data-mood', mood);
      svg.classList.remove('bounce', 'shake');
      void svg.getBoundingClientRect();
      if (mood === 'happy' || mood === 'celebrate') svg.classList.add('bounce');
      if (mood === 'encourage') svg.classList.add('shake');
    }
    if (bubble && text !== undefined) bubble.innerHTML = text;
    wrap.classList.remove('ok', 'bad');
    if (tone) wrap.classList.add(tone);
  };

  /* ------------------------------------------------------------ toast */
  SC.toast = function (title, body, mood) {
    var stack = document.getElementById('toasts');
    if (!stack) return;
    var t = SC.el('div', { class: 'toast', role: 'status' }, [SC.scarSvg(mood || 'celebrate', 48), SC.el('div', {}, [SC.el('strong', { text: title }), SC.el('span', { text: body || '' })])]);
    stack.appendChild(t);
    setTimeout(function () { t.style.transition = 'opacity .4s'; t.style.opacity = '0'; }, 5200);
    setTimeout(function () { t.remove(); }, 5700);
  };

  SC.celebrateAchievements = function (list) {
    (list || []).forEach(function (a, i) {
      setTimeout(function () { SC.toast('Lencana baru: ' + a.title + '!', a.description + ' (+' + a.xp_bonus + ' XP)', 'celebrate'); }, 400 + i * 900);
    });
  };

  SC.updateHeaderXP = function (stats) {
    if (!stats) return;
    var el = document.querySelector('[data-header-xp]');
    if (el) el.textContent = stats.total_xp + ' XP';
    var lv = document.querySelector('.user-chip .lvl');
    if (lv && stats.level) lv.textContent = 'Lv ' + stats.level.level;
  };

  /* ------------------------------------------------------------ math helpers */
  function gcd(a, b) { a = Math.abs(a); b = Math.abs(b); while (b) { var t = b; b = a % b; a = t; } return a || 1; }
  SC.gcd = gcd;

  /** Parse "3/4", "-1,5", "−2" menjadi angka; NaN jika tidak valid. */
  SC.parseNum = function (raw) {
    if (raw === null || raw === undefined) return NaN;
    var s = String(raw).trim().replace(/−|–/g, '-').replace(/,/g, '.').replace(/\s+/g, '');
    if (!s) return NaN;
    if (!/^[+-]?(\d+(\.\d+)?|\.\d+)(\/[+-]?\d+(\.\d+)?)?$/.test(s)) return NaN;
    if (s.indexOf('/') >= 0) {
      var p = s.split('/');
      var d = parseFloat(p[1]);
      return d === 0 ? NaN : parseFloat(p[0]) / d;
    }
    return parseFloat(s);
  };

  /** Tampilkan angka sebagai pecahan sederhana jika memungkinkan: 0.5 → "1/2". */
  SC.fmt = function (v) {
    if (!isFinite(v)) return '—';
    var sign = v < 0 ? '−' : '';
    var a = Math.abs(v);
    for (var den = 1; den <= 12; den++) {
      var num = Math.round(a * den);
      if (Math.abs(num / den - a) < 1e-9) {
        var g = gcd(num, den);
        num /= g; var d = den / g;
        return sign + (d === 1 ? String(num) : num + '/' + d);
      }
    }
    return sign + (Math.round(a * 1000) / 1000).toString();
  };

  SC.term = function (m, v) {
    var a = Math.abs(m);
    if (Math.abs(a - 1) < 1e-9) return v;
    var f = SC.fmt(a);
    return (f.indexOf('/') >= 0 ? '(' + f + ')' : f) + v;
  };

  /** "y = 2x − 3" dari m, c */
  SC.eq = function (m, c) {
    if (Math.abs(m) < 1e-12) return 'y = ' + SC.fmt(c);
    var head = (m < 0 ? '−' : '') + SC.term(m, 'x');
    if (Math.abs(c) < 1e-12) return 'y = ' + head;
    return 'y = ' + head + ' ' + (c < 0 ? '− ' : '+ ') + SC.fmt(Math.abs(c));
  };

  SC.pt = function (x, y) { return '(' + SC.fmt(x) + ', ' + SC.fmt(y) + ')'; };

  SC.quadrant = function (x, y) {
    if (x === 0 && y === 0) return 'titik asal O(0, 0)';
    if (x === 0) return 'sumbu Y';
    if (y === 0) return 'sumbu X';
    if (x > 0 && y > 0) return 'Kuadran I';
    if (x < 0 && y > 0) return 'Kuadran II';
    if (x < 0 && y < 0) return 'Kuadran III';
    return 'Kuadran IV';
  };

  SC.stars = function (n) {
    var out = '<span class="stars" aria-label="' + n + ' dari 3 bintang">';
    for (var i = 0; i < 3; i++) {
      out += '<svg width="26" height="26" viewBox="0 0 24 24" class="' + (i < n ? 'on' : '') + '" fill="' + (i < n ? '#E6C878' : 'none') + '" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"><path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z"/></svg>';
    }
    return out + '</span>';
  };

  SC.busy = function (btn, on, label) {
    if (!btn) return;
    if (on) {
      btn.dataset.label = btn.innerHTML;
      btn.disabled = true;
      btn.innerHTML = '<span class="spin"></span> ' + (label || 'Memproses...');
    } else {
      btn.disabled = false;
      if (btn.dataset.label) btn.innerHTML = btn.dataset.label;
    }
  };

  SC.shuffle = function (arr) {
    var a = arr.slice();
    for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var t = a[i]; a[i] = a[j]; a[j] = t; }
    return a;
  };

  /* ------------------------------------------------------------ UI wiring */
  document.addEventListener('click', function (e) {
    var dismiss = e.target.closest('[data-dismiss]');
    if (dismiss) { var f = dismiss.closest('.flash'); if (f) f.remove(); }
    var toggle = e.target.closest('[data-nav-toggle]');
    if (toggle) {
      var nav = document.getElementById('mainnav');
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    }
    var pw = e.target.closest('[data-pw-toggle]');
    if (pw) {
      var input = document.getElementById(pw.getAttribute('data-pw-toggle'));
      var show = input.type === 'password';
      input.type = show ? 'text' : 'password';
      pw.setAttribute('aria-label', show ? 'Sembunyikan password' : 'Tampilkan password');
      pw.querySelector('.eye').classList.toggle('hidden', show);
      pw.querySelector('.eye-off').classList.toggle('hidden', !show);
    }
  });

  setTimeout(function () {
    document.querySelectorAll('.flash-success, .flash-info').forEach(function (f) { f.style.transition = 'opacity .5s'; f.style.opacity = '0'; setTimeout(function () { f.remove(); }, 600); });
  }, 6000);

  // Formulir dengan loading state
  document.addEventListener('submit', function (e) {
    var form = e.target;
    if (form.hasAttribute('data-loading')) {
      var btn = form.querySelector('button[type=submit]');
      setTimeout(function () { SC.busy(btn, true, form.getAttribute('data-loading')); }, 0);
    }
  });

  global.SC = SC;
})(window);
