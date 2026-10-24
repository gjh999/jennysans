/* JennySans 글자맵 (site/glyphs.html) — assets/glyphmap.json 만 읽는다. 외부 의존 0, ES5 호환. */
(function () {
  'use strict';

  var WEIGHT_NAMES = [[100, 'Thin'], [200, 'ExtraLight'], [300, 'Light'], [400, 'Regular'], [500, 'Medium'],
                      [600, 'SemiBold'], [700, 'Bold'], [800, 'ExtraBold'], [900, 'Black']];
  var CHUNK = 250;          // 한 번에 DOM 에 붙이는 셀 수
  var FIRST_PAGE = 1000;    // 그룹 없는 큰 블록의 첫 페이지 크기

  var data = null, current = null, currentGroup = -1, pending = [], rendered = 0, raf = 0;
  var elBlocks = document.getElementById('g-blocks');
  var elGroups = document.getElementById('g-groups');
  var elGrid = document.getElementById('g-grid');
  var elTitle = document.getElementById('g-title');
  var elNote = document.getElementById('g-note');
  var elMore = document.getElementById('g-more');
  var elMoreBtn = document.getElementById('g-more-btn');
  var elDetail = document.getElementById('g-detail');

  /* ---------- 유틸 ---------- */
  function hex(cp) { var s = cp.toString(16).toUpperCase(); while (s.length < 4) s = '0' + s; return s; }
  function cpsOf(ranges) {
    var out = [];
    for (var i = 0; i < ranges.length; i++) for (var c = ranges[i][0]; c <= ranges[i][1]; c++) out.push(c);
    return out;
  }
  function inRanges(ranges, cp) {
    for (var i = 0; i < ranges.length; i++) if (cp >= ranges[i][0] && cp <= ranges[i][1]) return true;
    return false;
  }
  function nearestWeight(w) {
    var best = WEIGHT_NAMES[0];
    for (var i = 0; i < WEIGHT_NAMES.length; i++) if (Math.abs(WEIGHT_NAMES[i][0] - w) < Math.abs(best[0] - w)) best = WEIGHT_NAMES[i];
    return best;
  }
  function unicodeName(block, cp) {
    if (block.names && block.names[hex(cp)]) return block.names[hex(cp)];
    if (block.name_kind === 'hangul') {
      var r = data.hangul_jamo_roman, i = cp - 0xAC00;
      if (i >= 0 && i < 11172) {
        return 'HANGUL SYLLABLE ' + r.cho[Math.floor(i / 588)] + r.jung[Math.floor((i % 588) / 28)] + r.jong[i % 28];
      }
    }
    if (block.name_kind === 'cjk') return 'CJK UNIFIED IDEOGRAPH-' + hex(cp);
    return '(이름 없음)';
  }
  function blockOf(cp) {
    for (var i = 0; i < data.blocks.length; i++) if (inRanges(data.blocks[i].ranges, cp)) return data.blocks[i];
    return null;
  }

  /* ---------- 격자 렌더 (청크 단위로 붙여 브라우저가 멎지 않게) ---------- */
  function stopRender() { if (raf) { cancelAnimationFrame(raf); raf = 0; } pending = []; }

  function pump() {
    raf = 0;
    if (!pending.length) return;
    var frag = document.createDocumentFragment(), n = Math.min(CHUNK, pending.length);
    for (var i = 0; i < n; i++) {
      var cp = pending.shift();
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'glyph-cell';
      b.setAttribute('data-cp', String(cp));
      b.setAttribute('role', 'gridcell');
      b.setAttribute('title', 'U+' + hex(cp));
      var g = document.createElement('span');
      g.className = 'glyph-cell-char';
      g.textContent = String.fromCodePoint(cp);
      var c = document.createElement('span');
      c.className = 'glyph-cell-cp';
      c.textContent = hex(cp);
      b.appendChild(g); b.appendChild(c);
      frag.appendChild(b);
      rendered++;
    }
    elGrid.appendChild(frag);
    if (pending.length) raf = requestAnimationFrame(pump);
    else elMore.hidden = !elMore.dataset.rest || elMore.dataset.rest === '0';
  }

  function renderCps(cps, append) {
    stopRender();
    if (!append) { elGrid.innerHTML = ''; rendered = 0; }
    pending = cps.slice(0);
    elGrid.setAttribute('aria-rowcount', String(Math.ceil((rendered + pending.length) / 10)));
    raf = requestAnimationFrame(pump);
  }

  /* ---------- 블록 / 그룹 선택 ---------- */
  function selectBlock(id, groupIdx, opts) {
    var block = null;
    for (var i = 0; i < data.blocks.length; i++) if (data.blocks[i].id === id) block = data.blocks[i];
    if (!block) return;
    current = block;
    currentGroup = (block.groups && block.groups.length) ? (groupIdx == null ? 0 : groupIdx) : -1;

    var btns = elBlocks.querySelectorAll('button[data-block]');
    for (var b = 0; b < btns.length; b++) btns[b].setAttribute('aria-pressed', btns[b].getAttribute('data-block') === id ? 'true' : 'false');

    elTitle.textContent = block.label;
    elNote.textContent = block.note + ' · ' + block.count.toLocaleString() + '자';

    elGroups.innerHTML = '';
    if (currentGroup >= 0) {
      for (var gi = 0; gi < block.groups.length; gi++) {
        (function (idx) {
          var g = block.groups[idx];
          var el = document.createElement('button');
          el.type = 'button';
          el.setAttribute('data-group', String(idx));
          el.setAttribute('aria-pressed', idx === currentGroup ? 'true' : 'false');
          el.textContent = g.label + ' ' + g.count;
          el.addEventListener('click', function () { selectBlock(id, idx); });
          elGroups.appendChild(el);
        })(gi);
      }
      var g2 = block.groups[currentGroup];
      elNote.textContent = block.note + ' · 전체 ' + block.count.toLocaleString() + '자 · 지금 보는 초성 ' + g2.label + ' ' + g2.count + '자';
      elMore.hidden = true; elMore.dataset.rest = '0';
      renderCps(cpsOf(g2.ranges), false);
    } else {
      var all = cpsOf(block.ranges);
      if (all.length > FIRST_PAGE) {
        elMore.dataset.rest = String(all.length - FIRST_PAGE);
        elMore.hidden = false;
        elMoreBtn.textContent = '남은 ' + (all.length - FIRST_PAGE).toLocaleString() + '자 더 보기';
        elMoreBtn.onclick = function () {
          elMore.hidden = true; elMore.dataset.rest = '0';
          renderCps(all.slice(FIRST_PAGE), true);
        };
        renderCps(all.slice(0, FIRST_PAGE), false);
      } else {
        elMore.hidden = true; elMore.dataset.rest = '0';
        renderCps(all, false);
      }
    }
    if (!(opts && opts.noScroll)) {
      var top = document.querySelector('.glyph-layout');
      if (top && window.scrollY > top.offsetTop) top.scrollIntoView({ block: 'start' });
    }
    try { history.replaceState(null, '', '#' + id + (currentGroup >= 0 ? '-' + currentGroup : '')); } catch (e) { /* file:// */ }
  }

  /* ---------- 상세 패널 ---------- */
  function showDetail(cp) {
    var block = blockOf(cp);
    document.getElementById('g-detail-glyph').textContent = String.fromCodePoint(cp);
    document.getElementById('g-detail-cp').textContent = 'U+' + hex(cp) + '  (10진 ' + cp + ')';
    document.getElementById('g-detail-name').textContent = block ? unicodeName(block, cp) : '(모름)';
    document.getElementById('g-detail-block').textContent = block ? block.label : '(폰트에 없음)';
    elDetail.hidden = false;
    elDetail.dataset.cp = String(cp);
    var cells = elGrid.querySelectorAll('.glyph-cell[aria-selected="true"]');
    for (var i = 0; i < cells.length; i++) cells[i].removeAttribute('aria-selected');
    var cell = elGrid.querySelector('.glyph-cell[data-cp="' + cp + '"]');
    if (cell) cell.setAttribute('aria-selected', 'true');
  }

  function copyText(text, btn) {
    function done(ok) {
      var orig = btn.getAttribute('data-label') || btn.textContent;
      btn.setAttribute('data-label', orig);
      btn.textContent = ok ? '복사됨' : '실패';
      btn.classList.toggle('copied', ok);
      setTimeout(function () { btn.textContent = orig; btn.classList.remove('copied'); }, 1500);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () { done(true); }, function () { done(false); });
    } else {
      var ta = document.createElement('textarea');
      ta.value = text; ta.style.position = 'fixed'; ta.style.left = '-9999px';
      document.body.appendChild(ta); ta.select();
      var ok = false; try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
      document.body.removeChild(ta); done(ok);
    }
  }

  /* ---------- 검색 ---------- */
  function search(q) {
    q = (q || '').trim();
    if (!q) return;
    var cp = null;
    var m = /^(?:u\+|U\+|0x)?([0-9a-fA-F]{4,6})$/.exec(q);
    if (m) cp = parseInt(m[1], 16);
    else cp = q.codePointAt(0);
    var block = blockOf(cp);
    if (!block) { elNote.textContent = 'U+' + hex(cp) + ' 는 이 폰트에 없습니다.'; return; }
    var gi = null;
    if (block.groups) {
      for (var i = 0; i < block.groups.length; i++) if (inRanges(block.groups[i].ranges, cp)) gi = i;
    }
    selectBlock(block.id, gi, { noScroll: true });
    // 큰 블록에서 검색 대상이 첫 페이지 밖이면 전부 펼친다
    if (!elMore.hidden && elMoreBtn.onclick) elMoreBtn.onclick();
    var tries = 0;
    (function wait() {
      var cell = elGrid.querySelector('.glyph-cell[data-cp="' + cp + '"]');
      if (cell) {
        cell.scrollIntoView({ block: 'center' });
        showDetail(cp);
      } else if (tries++ < 40) setTimeout(wait, 50);
    })();
  }

  /* ---------- 시작 ---------- */
  fetch('/assets/glyphmap.json', { cache: 'no-cache' }).then(function (r) {
    if (!r.ok) throw new Error('glyphmap.json ' + r.status);
    return r.json();
  }).then(function (json) {
    data = json;

    for (var i = 0; i < data.blocks.length; i++) {
      (function (b) {
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.setAttribute('data-block', b.id);
        btn.setAttribute('aria-pressed', 'false');
        btn.innerHTML = '<span class="gb-label"></span><span class="gb-count"></span>';
        btn.querySelector('.gb-label').textContent = b.label;
        btn.querySelector('.gb-count').textContent = b.count.toLocaleString();
        btn.addEventListener('click', function () { selectBlock(b.id); });
        elBlocks.appendChild(btn);
      })(data.blocks[i]);
    }

    var hash = (location.hash || '').replace(/^#/, '');
    var mh = /^([a-z-]+)(?:-(\d+))?$/.exec(hash);
    var startId = data.blocks[0].id, startGroup = null;
    if (mh) {
      for (var k = 0; k < data.blocks.length; k++) if (data.blocks[k].id === mh[1]) { startId = mh[1]; startGroup = mh[2] ? parseInt(mh[2], 10) : null; }
    }
    selectBlock(startId, startGroup, { noScroll: true });
    document.documentElement.setAttribute('data-glyphmap', 'ready');
  }).catch(function (e) {
    elTitle.textContent = '글자맵을 불러오지 못했습니다';
    elNote.textContent = String(e) + ' — assets/glyphmap.json 이 배포됐는지 확인하세요(tools/glyphmap.py).';
  });

  /* ---------- 컨트롤 ---------- */
  var w = document.getElementById('g-weight'), wOut = document.getElementById('g-weight-out');
  var s = document.getElementById('g-size'), sOut = document.getElementById('g-size-out');
  function setWeight(v) {
    v = parseInt(v, 10) || 400;
    elGrid.style.setProperty('--gw', String(v));
    document.getElementById('g-detail-glyph').style.setProperty('--gw', String(v));
    var n = nearestWeight(v);
    wOut.textContent = v + ' · ' + n[1] + (n[0] === v ? '' : ' 근처');
  }
  function setSize(v) { v = parseInt(v, 10) || 40; elGrid.style.setProperty('--gs', v + 'px'); sOut.textContent = v + 'px'; }
  w.addEventListener('input', function () { setWeight(w.value); });
  s.addEventListener('input', function () { setSize(s.value); });
  setWeight(w.value); setSize(s.value);

  elGrid.addEventListener('click', function (e) {
    var cell = e.target.closest ? e.target.closest('.glyph-cell') : null;
    if (cell) showDetail(parseInt(cell.getAttribute('data-cp'), 10));
  });
  document.getElementById('g-detail-close').addEventListener('click', function () { elDetail.hidden = true; });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') elDetail.hidden = true; });
  document.getElementById('g-copy-char').addEventListener('click', function () { copyText(String.fromCodePoint(parseInt(elDetail.dataset.cp, 10)), this); });
  document.getElementById('g-copy-cp').addEventListener('click', function () { copyText('U+' + hex(parseInt(elDetail.dataset.cp, 10)), this); });
  document.getElementById('g-copy-html').addEventListener('click', function () { copyText('&#x' + hex(parseInt(elDetail.dataset.cp, 10)) + ';', this); });

  var q = document.getElementById('g-search');
  q.addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); search(q.value); } });
  q.addEventListener('search', function () { search(q.value); });
})();
