from core.brain.parser import parse

tests = [
    "googloch",
    "chromenioch",
    "telegramoch",
    "viskotoch",
    "noutbukniuchir",
    "soatnecha",
    "google och",
    "chrome ni och",
    "rafael chromeni och",
    "YouTubeda anime qidir",
    "ovozni oshir",
    "bluetooth CH86 ga ula",
]
for t in tests:
    r = parse(t)
    if r:
        val = r.get("app") or r.get("query") or r.get("device") or ""
        print(f"  OK  {t:30} => {r['action']} {val}")
    else:
        print(f"  --  {t}")
