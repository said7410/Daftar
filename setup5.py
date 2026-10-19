"""@manhwaatomic_bot GitHub qismini o'rnatadi (kod + workflow'lar + sirlar; eski atomic.yml ishlarini bekor qiladi). Ishga tushirish:
   python setup.py <GITHUB_TOKEN>      (token: repo + workflow ruxsati, hisob giminiuchun2-maker)
Nima qiladi: kodni Shaxsiy reposiga yuklaydi, sirlarni (bot tokeni, Gemini kalitlari...) GitHub Secrets'ga
shifrlab yozadi, zaxira workflow'ni birinchi marta ishga tushiradi. Sirlar kodga YOZILMAYDI."""
import base64, json, os, subprocess, sys, tempfile, urllib.request
from pathlib import Path

tok = sys.argv[1]
OWNER, REPO = "said7410", "Daftar"
HERE = Path(__file__).parent
HOME = Path.home()


def api(method, path, body=None):
    req = urllib.request.Request("https://api.github.com" + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req) as r:
        raw = r.read()
        return json.loads(raw) if raw else {}


def envfile(p):
    out = {}
    for line in Path(p).read_text(encoding="utf-8").splitlines():
        k, _, v = line.strip().partition("=")
        if k and not k.startswith("#"):
            out[k] = v
    return out


# 1) kod -> repo (vaqtincha git, token saqlanmaydi)
with tempfile.TemporaryDirectory() as tmp:
    work = Path(tmp) / "r"
    subprocess.run(["robocopy", str(HERE), str(work), "/E", "/XF", "setup.py", "/NFL", "/NDL", "/NJH", "/NJS"],
                   capture_output=True)
    g = lambda *a: subprocess.run(["git", "-C", str(work), *a], check=True)
    g("init", "-q", "-b", "main")
    g("add", "-A")
    g("-c", "user.name=" + OWNER, "-c", f"user.email={OWNER}@users.noreply.github.com",
      "commit", "-q", "-m", "Atomic bot: zaxira server (telefon asosiy)")
    g("push", "-q", "-f", f"https://x-access-token:{tok}@github.com/{OWNER}/{REPO}.git", "main")
print("kod yuklandi")

# 2) sirlar
from nacl import encoding, public

pk = api("GET", f"/repos/{OWNER}/{REPO}/actions/secrets/public-key")
box = public.SealedBox(public.PublicKey(pk["key"].encode(), encoding.Base64Encoder()))
tg = {}
for l in (HOME / "manhwa-gate" / ".tg-api.txt").read_text().splitlines():
    k, _, v = l.partition("=")
    tg[k] = v.strip()
keys = ",".join((HOME / "manhwa-gate" / f).read_text().strip() for f in (".gemini.3.key", ".gemini.3b.key"))
mine = {"BOT_TOKEN": (HOME / "manhwa-gate" / ".bot5.token").read_text().strip(), "OWNER_ID": "8706650133",
        "GEMINI_API_KEY": keys, "TG_API_ID": tg["api_id"], "TG_API_HASH": tg["api_hash"]}
old = envfile(HOME / "manhwa-tarjima-bot" / ".env")
gate = json.loads((HOME / "manhwa-gate" / ".secrets.5.json").read_text(encoding="utf-8"))
secrets = {"BOT_TOKEN": mine["BOT_TOKEN"], "OWNER_ID": mine["OWNER_ID"], "GEMINI_API_KEY": mine["GEMINI_API_KEY"],
           "TG_API_ID": mine["TG_API_ID"], "TG_API_HASH": mine["TG_API_HASH"], "GATE_KEY": gate["GATE_KEY"]}
for name, val in secrets.items():
    enc = base64.b64encode(box.encrypt(val.encode())).decode()
    api("PUT", f"/repos/{OWNER}/{REPO}/actions/secrets/{name}", {"encrypted_value": enc, "key_id": pk["key_id"]})
    print("sir yozildi:", name)

# 3) eski ishlar yangi kod bilan almashtiriladi: avval YANGISI navbatga qo'yiladi (concurrency: eskisi tugaguncha
#    kutadi), keyin eskisi bekor qilinadi - bot uzilishi ~1 daqiqa. Bobi yarimda qolgan bo'lsa darvozada 150 s dan
#    keyin qayta navbatga tushadi (yo'qolmaydi). atomic.yml (eski polling) ishlari esa shunchaki bekor qilinadi.
old_runs = []
for st in ("in_progress", "queued", "pending"):
    for run in api("GET", f"/repos/{OWNER}/{REPO}/actions/runs?status={st}&per_page=30").get("workflow_runs", []):
        old_runs.append((run["id"], run["path"].rsplit("/", 1)[-1]))
active = {n for _, n in old_runs}
for wf in ("bot.yml",):
    if wf in active:
        api("POST", f"/repos/{OWNER}/{REPO}/actions/workflows/{wf}/dispatches", {"ref": "main"})
        print("yangi ish navbatga qo'yildi:", wf)
import time
time.sleep(5)
for rid, name in old_runs:
    if name in ("bot.yml",):
        try:
            api("POST", f"/repos/{OWNER}/{REPO}/actions/runs/{rid}/cancel")
            print("eski ish bekor qilindi:", name, rid)
        except Exception as e:
            print("bekor qilib bo'lmadi:", name, rid, e)
print("GitHub qismi tayyor: https://github.com/%s/%s/actions" % (OWNER, REPO))


