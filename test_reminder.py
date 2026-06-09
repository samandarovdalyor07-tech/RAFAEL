from core.brain.reminder import _parse_reminder_text

tests = [
    "soat 15 da dars boshlanadi eslat",
    "30 minutdan keyin choy ichish eslatib tur",
    "soat 18:30 da uyga ket eslatib ber",
    "yarim soatdan keyin eslatma",
    "2 soatdan keyin loyiha tekshir",
]
for t in tests:
    dt, msg = _parse_reminder_text(t)
    if dt:
        print(f"  OK  [{dt.strftime('%H:%M')}] '{msg}'")
    else:
        print(f"  --  vaqt topilmadi: {t}")
