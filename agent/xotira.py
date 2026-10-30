# -*- coding: utf-8 -*-
"""Agent xotirasi va jurnal — SQLite. Vazifalar tarixi, so'rov-javoblar, amallar jurnali."""
import os, sqlite3, time, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "agent_xotira.db")


def _con():
    c = sqlite3.connect(DB)
    c.execute("PRAGMA journal_mode=WAL")
    return c


def boshlash():
    with _con() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS vazifa(
            id INTEGER PRIMARY KEY AUTOINCREMENT, vaqt TEXT, oyna TEXT,
            sorov TEXT, javob TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS jurnal(
            id INTEGER PRIMARY KEY AUTOINCREMENT, vaqt TEXT, tur TEXT, matn TEXT)""")


def _ts():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def vazifa_yoz(oyna, sorov, javob):
    with _con() as c:
        c.execute("INSERT INTO vazifa(vaqt,oyna,sorov,javob) VALUES(?,?,?,?)",
                  (_ts(), oyna or "", sorov or "", javob or ""))


def jurnal_yoz(tur, matn):
    with _con() as c:
        c.execute("INSERT INTO jurnal(vaqt,tur,matn) VALUES(?,?,?)", (_ts(), tur, matn))


def oxirgi_vazifalar(n=20):
    with _con() as c:
        return c.execute("SELECT vaqt,oyna,sorov,javob FROM vazifa ORDER BY id DESC LIMIT ?",
                         (n,)).fetchall()


def kontekst(n=5):
    """Oxirgi N vazifani qisqa matn qilib — Claude'ga kontekst sifatida beriladi."""
    rows = oxirgi_vazifalar(n)
    if not rows:
        return ""
    qisqa = []
    for vaqt, oyna, sorov, javob in reversed(rows):
        qisqa.append(f"[{vaqt}] So'rov: {sorov[:120]} | Javob: {(javob or '')[:160]}")
    return "Oldingi vazifalar (kontekst):\n" + "\n".join(qisqa)


if __name__ == "__main__":
    boshlash()
    vazifa_yoz("Excel - reys.xlsx", "xato bormi", "3-qatorda sana noto'g'ri")
    jurnal_yoz("test", "sinov yozuvi")
    print("Vazifalar:", oxirgi_vazifalar())
    print("Kontekst:\n", kontekst())
