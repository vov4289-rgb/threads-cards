# 클라우드 게시 루틴이 쓰는 Threads 게시 스크립트.
# 토큰은 다루지 않는다: 클라우드 환경의 네트워크 시크릿이 graph.threads.net 요청에 Authorization 헤더를 붙인다.
# 사용: python3 post.py <글.txt> [이미지URL]  |  python3 post.py check-image <이미지URL> (게시 안 함)
import json, sys, time, urllib.error, urllib.parse, urllib.request
API = "https://graph.threads.net/v1.0"
def out(**kw):
    print(json.dumps(kw, ensure_ascii=False)); sys.exit(0 if kw.get("ok") else 1)
def call(method, url, params):
    data = None
    if method == "GET":
        url += "?" + urllib.parse.urlencode(params)
    else:
        data = urllib.parse.urlencode(params).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data, method=method), timeout=60) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read().decode('utf-8','replace')[:300]}") from None
    except urllib.error.URLError as e:
        raise RuntimeError(f"네트워크 오류: {e.reason}") from None
def container(text, image_url):
    params = {"media_type": "TEXT", "text": text}
    if image_url:
        params.update(media_type="IMAGE", image_url=image_url)
    cid = call("POST", f"{API}/me/threads", params)["id"]
    for _ in range(12 if image_url else 1):
        time.sleep(5)
        if not image_url:
            return cid
        st = call("GET", f"{API}/{cid}", {"fields": "status,error_message"})
        if st.get("status") == "FINISHED":
            return cid
        if st.get("status") in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"이미지 처리 실패: {st.get('error_message') or st.get('status')}")
    raise RuntimeError("이미지 처리가 60초 안에 끝나지 않았어요")
if sys.argv[1] == "check-image":
    try:
        out(ok=True, container=container("이미지 확인용 (게시 안 함)", sys.argv[2]), published=False)
    except (RuntimeError, KeyError) as e:
        out(ok=False, error=str(e))
text = open(sys.argv[1], encoding="utf-8").read().strip()
image_url = sys.argv[2] if len(sys.argv) > 2 else None
if not text or len(text) > 500:
    out(ok=False, error=f"글 길이 문제: {len(text)}자")
image_error = None
try:
    try:
        cid = container(text, image_url)
    except (RuntimeError, KeyError) as e:
        if not image_url:
            raise
        # 아직 게시 전이라 글만으로 다시 만들어도 중복 게시 위험이 없다
        image_error = str(e)[:200]
        cid = container(text, None)
    p = call("POST", f"{API}/me/threads_publish", {"creation_id": cid})
except (RuntimeError, KeyError) as e:
    out(ok=False, error=str(e))
link = None
try:
    link = call("GET", f"{API}/{p['id']}", {"fields": "permalink"}).get("permalink")
except RuntimeError:
    pass
out(ok=True, id=p.get("id"), permalink=link, image=bool(image_url and not image_error), imageError=image_error)
