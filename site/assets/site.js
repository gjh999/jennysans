/* JennySans 홈페이지 — 타입 테스터·탭·복사·테마 (font-site 소유). 외부 의존 0, ES5 호환. */
(function () {
  'use strict';
  var root = document.documentElement;

  /* ---------- 테마 ---------- */
  var toggle = document.getElementById('theme-toggle');
  function currentTheme() {
    var t = root.getAttribute('data-theme');
    if (t === 'dark' || t === 'light') return t;
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  function applyTheme(t) {
    root.setAttribute('data-theme', t);
    try { localStorage.setItem('jennysans-theme', t); } catch (e) { /* 비공개 모드 등 */ }
    if (toggle) toggle.setAttribute('aria-label', t === 'dark' ? '라이트 모드로 전환' : '다크 모드로 전환');
  }
  if (toggle) {
    toggle.setAttribute('aria-label', currentTheme() === 'dark' ? '라이트 모드로 전환' : '다크 모드로 전환');
    toggle.addEventListener('click', function () { applyTheme(currentTheme() === 'dark' ? 'light' : 'dark'); });
  }

  /* ---------- 타입 테스터 ---------- */
  var WEIGHTS = [[100, 'Thin'], [200, 'ExtraLight'], [300, 'Light'], [400, 'Regular'], [500, 'Medium'],
                 [600, 'SemiBold'], [700, 'Bold'], [800, 'ExtraBold'], [900, 'Black']];
  var PRESETS = {
    ko: { lang: 'ko', text: '다람쥐 헌 쳇바퀴에 타고파. 키스의 고유조건은 입술끼리 만나야 하고 특별한 기술은 필요치 않다.' },
    es: { lang: 'es', text: '¿Qué tal, señor? ¡Año nuevo! El veloz murciélago hindú comía feliz cardillo y kiwi. Ñandú, pingüino, 1ª 2º, 12,50 €.' },
    en: { lang: 'en', text: 'The quick brown fox jumps over the lazy dog. Sphinx of black quartz, judge my vow.' },
    num: { lang: 'ko', text: '0123456789 · 1,234,567.89 · ₩48,000 · €12,50 · $9.99 · 12:34:56 · +82-10-1234-5678 · ½ ¼ ¾ · H₂O · x² + y² = z²' },
    sym: { lang: 'ko', text: '※ ① ② ③ ㉠ ㉡ ㉢ ㈜ ㎏ ㎡ ℃ ← → ↔ ★ ☆ ○ ● ■ □ ◇ 「제니산스」 『JennySans』 〈 〉 《 》 · … ± × ÷ ≠ ≤ ≥ ∞ ∴ √' },
    mix: { lang: 'ko', text: '제니산스 JennySans — 웹·앱·게임·문서에서 같은 글꼴로. Ñandú, pingüino, 1ª 2º. Größe, Œuvre, Zażółć gęślą jaźń. 2026년 9월 6일.' }
  };
  var tester = document.getElementById('tester-text');
  var ctlW = document.getElementById('ctl-weight');
  var ctlS = document.getElementById('ctl-size');
  var ctlL = document.getElementById('ctl-lh');
  var outW = document.getElementById('out-weight');
  var outS = document.getElementById('out-size');
  var outL = document.getElementById('out-lh');

  function nearestWeight(w) {
    var best = WEIGHTS[0];
    for (var i = 0; i < WEIGHTS.length; i++) {
      if (Math.abs(WEIGHTS[i][0] - w) < Math.abs(best[0] - w)) best = WEIGHTS[i];
    }
    return best;
  }
  function setWeight(w) {
    w = Math.max(100, Math.min(900, parseInt(w, 10) || 400));
    tester.style.setProperty('--tw', String(w));
    var n = nearestWeight(w);
    if (outW) outW.textContent = w + ' · ' + n[1] + (n[0] === w ? '' : ' 근처');
    if (ctlW) ctlW.setAttribute('aria-valuetext', w + ' ' + n[1]);
  }
  function setSize(px) {
    px = parseInt(px, 10) || 56;
    tester.style.setProperty('--ts', px + 'px');
    if (outS) outS.textContent = px + 'px';
  }
  function setLineHeight(v) {
    v = parseFloat(v) || 1.35;
    tester.style.setProperty('--tl', String(v));
    if (outL) outL.textContent = v.toFixed(2).replace(/0$/, '');
  }
  function setAlign(a) {
    tester.style.setProperty('--ta', a);
    var btns = document.querySelectorAll('.segmented [data-align]');
    for (var i = 0; i < btns.length; i++) btns[i].setAttribute('aria-pressed', btns[i].getAttribute('data-align') === a ? 'true' : 'false');
  }
  function setPreset(key) {
    var p = PRESETS[key];
    if (!p) return;
    tester.textContent = p.text;
    tester.setAttribute('lang', p.lang);
    var chips = document.querySelectorAll('.chips [data-preset]');
    for (var i = 0; i < chips.length; i++) chips[i].setAttribute('aria-pressed', chips[i].getAttribute('data-preset') === key ? 'true' : 'false');
  }
  if (tester) {
    if (ctlW) { ctlW.addEventListener('input', function () { setWeight(ctlW.value); }); setWeight(ctlW.value); }
    if (ctlS) { ctlS.addEventListener('input', function () { setSize(ctlS.value); }); setSize(ctlS.value); }
    if (ctlL) { ctlL.addEventListener('input', function () { setLineHeight(ctlL.value); }); setLineHeight(ctlL.value); }
    var alignBtns = document.querySelectorAll('.segmented [data-align]');
    for (var a = 0; a < alignBtns.length; a++) {
      alignBtns[a].addEventListener('click', function () { setAlign(this.getAttribute('data-align')); });
    }
    var presetBtns = document.querySelectorAll('.chips [data-preset]');
    for (var b = 0; b < presetBtns.length; b++) {
      presetBtns[b].addEventListener('click', function () { setPreset(this.getAttribute('data-preset')); });
    }
    // 붙여넣기는 서식 없이 텍스트만
    tester.addEventListener('paste', function (e) {
      var cb = e.clipboardData || window.clipboardData;
      if (!cb) return;
      e.preventDefault();
      var text = cb.getData('text/plain');
      if (document.queryCommandSupported && document.queryCommandSupported('insertText')) {
        document.execCommand('insertText', false, text);
      } else {
        tester.textContent += text;
      }
    });
    // 직접 편집하면 프리셋 선택 해제
    tester.addEventListener('input', function () {
      var chips = document.querySelectorAll('.chips [data-preset]');
      for (var i = 0; i < chips.length; i++) chips[i].setAttribute('aria-pressed', 'false');
    });
    var reset = document.getElementById('tester-reset');
    if (reset) reset.addEventListener('click', function () {
      if (ctlW) { ctlW.value = '400'; setWeight(400); }
      if (ctlS) { ctlS.value = '56'; setSize(56); }
      if (ctlL) { ctlL.value = '1.35'; setLineHeight(1.35); }
      setAlign('left');
      setPreset('ko');
    });
  }

  /* ---------- 문장 견본: 크기·줄간격 토글 ---------- */
  var spBox = document.getElementById('specimen-box');
  if (spBox) {
    function segSet(attr, prop, value, unit) {
      spBox.style.setProperty(prop, value + (unit || ''));
      var btns = document.querySelectorAll('[' + attr + ']');
      for (var i = 0; i < btns.length; i++) btns[i].setAttribute('aria-pressed', btns[i].getAttribute(attr) === value ? 'true' : 'false');
    }
    var sizeBtns = document.querySelectorAll('[data-sp-size]');
    for (var si2 = 0; si2 < sizeBtns.length; si2++) {
      sizeBtns[si2].addEventListener('click', function () { segSet('data-sp-size', '--sp-size', this.getAttribute('data-sp-size'), 'px'); });
    }
    var lhBtns = document.querySelectorAll('[data-sp-lh]');
    for (var li = 0; li < lhBtns.length; li++) {
      lhBtns[li].addEventListener('click', function () { segSet('data-sp-lh', '--sp-lh', this.getAttribute('data-sp-lh')); });
    }
  }

  /* ---------- 탭 (WAI-ARIA tabs) ---------- */
  var tablist = document.querySelector('.tabs[role="tablist"]');
  if (tablist) {
    var tabs = Array.prototype.slice.call(tablist.querySelectorAll('[role="tab"]'));
    function selectTab(tab, focus) {
      for (var i = 0; i < tabs.length; i++) {
        var t = tabs[i], on = t === tab;
        t.setAttribute('aria-selected', on ? 'true' : 'false');
        t.setAttribute('tabindex', on ? '0' : '-1');
        var panel = document.getElementById(t.getAttribute('aria-controls'));
        if (panel) panel.hidden = !on;
      }
      if (focus) tab.focus();
      try { history.replaceState(null, '', '#usage-' + tab.id.replace(/^tab-/, '')); } catch (e) { /* file:// 등 */ }
    }
    for (var ti = 0; ti < tabs.length; ti++) {
      tabs[ti].addEventListener('click', function () { selectTab(this, false); });
      tabs[ti].addEventListener('keydown', function (e) {
        var idx = tabs.indexOf(this), next = null;
        if (e.key === 'ArrowRight') next = tabs[(idx + 1) % tabs.length];
        else if (e.key === 'ArrowLeft') next = tabs[(idx - 1 + tabs.length) % tabs.length];
        else if (e.key === 'Home') next = tabs[0];
        else if (e.key === 'End') next = tabs[tabs.length - 1];
        if (next) { e.preventDefault(); selectTab(next, true); }
      });
    }
    // #usage-web 처럼 해시로 탭을 열 수 있게
    var m = /^#usage-([a-z]+)$/.exec(location.hash);
    if (m) {
      var target = document.getElementById('tab-' + m[1]);
      if (target) {
        selectTab(target, false);
        var usage = document.getElementById('usage');
        if (usage) setTimeout(function () { usage.scrollIntoView(); }, 0);
      }
    }
  }

  /* ---------- 복사 버튼 ---------- */
  function copyText(text, btn) {
    function done(ok) {
      if (!btn) return;
      var orig = btn.getAttribute('data-label') || btn.textContent;
      btn.setAttribute('data-label', orig);
      btn.textContent = ok ? '복사됨' : '실패';
      btn.classList.toggle('copied', ok);
      setTimeout(function () { btn.textContent = orig; btn.classList.remove('copied'); }, 1500);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () { done(true); }, function () { fallback(); });
    } else { fallback(); }
    function fallback() {
      var ta = document.createElement('textarea');
      ta.value = text; ta.setAttribute('readonly', ''); ta.style.position = 'fixed'; ta.style.left = '-9999px';
      document.body.appendChild(ta); ta.select();
      var ok = false;
      try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
      document.body.removeChild(ta);
      done(ok);
    }
  }
  // 코드 블록마다 복사 버튼 주입
  var pres = document.querySelectorAll('pre');
  for (var pi = 0; pi < pres.length; pi++) {
    (function (pre) {
      var btn = document.createElement('button');
      btn.type = 'button'; btn.className = 'copy-btn'; btn.textContent = '복사'; btn.setAttribute('aria-label', '코드 복사');
      btn.addEventListener('click', function () {
        var code = pre.querySelector('code');
        copyText((code ? code.textContent : pre.textContent).replace(/\s+$/, ''), btn);
      });
      pre.appendChild(btn);
    })(pres[pi]);
  }
  var shaBtns = document.querySelectorAll('[data-copy]');
  for (var si = 0; si < shaBtns.length; si++) {
    shaBtns[si].addEventListener('click', function () { copyText(this.getAttribute('data-copy'), this); });
  }

  /* ---------- 폰트 로드 상태 (푸터, QA 용) ---------- */
  var status = document.getElementById('font-status');
  if (status && document.fonts) {
    document.fonts.ready.then(function () {
      var loaded = 0, vf = 0;
      document.fonts.forEach(function (f) {
        if (f.status !== 'loaded') return;
        if (f.family.replace(/["']/g, '') === 'JennySans') loaded++;
        else if (/JennySans VF/i.test(f.family)) vf++;
      });
      var ok = document.fonts.check('400 16px "JennySans"') && loaded > 0;
      status.textContent = ok ? ('JennySans 웹폰트 로드됨 (조각 ' + loaded + (vf ? ', 변수 ' + vf : '') + ')') : 'JennySans 웹폰트를 불러오지 못했습니다 — 폴백 글꼴로 보입니다';
      status.setAttribute('data-ok', ok ? '1' : '0');
    });
  }
})();
