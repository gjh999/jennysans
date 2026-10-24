# 검색엔진 등록 절차 — JennySans (font.jennysoft.co.kr)

> 2026-09-07 작성(팀장). 코드 쪽 SEO 준비는 끝났다(아래 §0). 이 문서는 **사이트 소유자가 콘솔에서 직접 해야 하는 일**이다.
> 패턴은 `<사내 저장소 QPinball>\docs\SEO_REGISTRATION.md` 와 동일.

## 0. 코드 쪽에 이미 들어간 것 (`site/`, 배포 시 루트에 올라감)
| 항목 | 위치 | 내용 |
|---|---|---|
| Google 소유 확인 파일 | `site/google85364fe7cc780e8d.html` → `https://font.jennysoft.co.kr/google85364fe7cc780e8d.html` | 사용자가 준 파일 그대로(내용 `google-site-verification: google85364fe7cc780e8d.html`). 파일명의 " (1)" 은 다운로드 중복 표기라 제거함 |
| `<title>`·description·keywords·robots | `site/index.template.html` `<head>` | 한국어 제목 "JennySans 제니산스 — 범용 한글·영문(라틴) 고딕 폰트 · 무료 다운로드", `max-image-preview:large` |
| Open Graph·Twitter 카드 | 같은 곳 | `og:image` = `/assets/og-image.png`(1200×630, JennySans 로 렌더), `og:locale ko_KR`, `summary_large_image` |
| canonical·hreflang | 같은 곳 | `https://font.jennysoft.co.kr/` (ko, x-default) |
| JSON-LD | 같은 곳 | `Organization`(JennySoft) + `WebSite` + `SoftwareApplication`(이름·버전·downloadUrl·license·isBasedOn·무료 Offer) |
| 아이콘 | `site/favicon.ico`, `site/assets/{icon-512,icon-192,apple-touch-icon,favicon-32}.png` | `tools/seo_assets.py` 가 dist 폰트로 생성 |
| robots.txt | `site/robots.txt` | `Allow: /`, `Disallow: /*.bak.*`·`/test.html`, `Sitemap:` 지정 |
| sitemap.xml | `site/sitemap.xml` | 루트 + 앵커(#download·#usage·#license) + LICENSE, og 이미지 포함 |
| 본문 텍스트 | `index.html` | 크롤러가 읽는 실제 텍스트(소개·문자 범위 표·사용법·라이선스)가 HTML 에 그대로 있음(JS 렌더 아님) |

재생성: 템플릿을 고치면 `PYTHONUTF8=1 python tools/package.py --render-only`, 이미지는 `python tools/seo_assets.py`.

## 1. Google Search Console — https://search.google.com/search-console
1. 「속성 추가」 → **URL 접두어** 유형에 `https://font.jennysoft.co.kr/` 입력(HTML 파일 방식은 URL 접두어 속성에서만 쓸 수 있다).
2. 확인 방법에서 **HTML 파일** 선택 → 이미 올라가 있으므로 바로 「확인」. 실패하면 `curl -I https://font.jennysoft.co.kr/google85364fe7cc780e8d.html` 이 200 인지 본다(배포 후에만 200).
   - 도메인 속성(DNS TXT)으로도 추가하려면 QPinball 문서 §1-2 와 동일.
3. 「Sitemaps」 → `https://font.jennysoft.co.kr/sitemap.xml` 제출.
4. 「URL 검사」 → `https://font.jennysoft.co.kr/` → 「색인 생성 요청」.
5. 며칠 뒤 「URL 검사 → 크롤링된 페이지 보기」에서 제니산스로 렌더된 화면이 보이면 정상. 「개선사항 → 리치 결과」에 SoftwareApplication 이 잡히는지 확인.

## 2. 네이버 서치어드바이저 — https://searchadvisor.naver.com
1. 「웹마스터 도구」 → 사이트 등록 `https://font.jennysoft.co.kr`.
2. 소유 확인: **HTML 태그** 방식이면 `<meta name="naver-site-verification" content="값">` 값을 알려주면 템플릿 `<head>` 에 넣어 재배포. **HTML 파일** 방식이면 파일을 `site/` 에 넣고 재배포.
3. 「요청 → 사이트맵 제출」 `https://font.jennysoft.co.kr/sitemap.xml`, 「웹 페이지 수집」 `https://font.jennysoft.co.kr/`.
4. 「검증 → robots.txt」 수집 허용 확인.

## 3. 다음(카카오) — https://register.search.daum.net/index.daum
- 「신규 등록」에 URL 입력(소유 확인 없음). 사이트명 「JennySans 제니산스 — 무료 한글·영문(라틴) 고딕 폰트」.

## 4. Bing 웹마스터 — https://www.bing.com/webmasters
- 「Google Search Console 에서 가져오기」(§1 완료 후).

## 5. 등록 뒤 확인
- `site:font.jennysoft.co.kr`, 「제니산스」, 「JennySans」, 「무료 한글 고딕 폰트」 검색.
- 공유 카드: https://developers.facebook.com/tools/debug/ 에 URL → `og-image.png` 표시 확인. 카카오톡 공유 미리보기도 같은 OG 를 쓴다.
- 리치 결과 테스트: https://search.google.com/test/rich-results 에 URL → SoftwareApplication 인식 확인.

## 6. 초기 노출에 도움이 되는 것(선택)
- GitHub 공개 저장소 README 와 npm 패키지 설명에 `https://font.jennysoft.co.kr` 링크(P7b, 승인 후).
- 제니소프트 다른 사이트(qaudio·latinbeat·pinball 푸터)에서 "폰트: JennySans" 링크 한 줄.
- 눈누(noonnu.cc)·구글 폰트 같은 무료 폰트 디렉터리 등록은 OFL 이라 가능 — 원본 크레딧 표기 유지 조건. 후속 검토.

## 7. 자주 막히는 것
- 「소유 확인 실패」: 배포 전에는 인증 파일이 404 다. 본배포(P7a) 뒤에 「확인」.
- 「사이트맵을 읽을 수 없음」: `curl -I https://font.jennysoft.co.kr/sitemap.xml` 200 · `Content-Type: application/xml` 확인(nginx mime.types 기본 포함).
- OG 이미지가 옛것으로 보임: 페이스북 디버거에서 「다시 스크랩」. 이미지 경로는 버전 없는 `/assets/og-image.png` 라 교체 시 캐시 5분(nginx `/assets` 86400 → 필요하면 파일명에 해시).
