# -*- coding: utf-8 -*-
"""Jurat Yordamchi — Windows desktop AI agent (MVP, 1-bosqich).

NIMA QILADI (1-bosqich):
  - Siz "Ekranni ko'r" tugmasini bosganingizda ekranni suratga oladi (doimiy kuzatuv YO'Q).
  - OCR bilan matnni o'qiydi, qaysi dastur ochiqligini biladi.
  - Siz yozgan topshiriq + ekran matnini Claude (Pro obunangiz) ga beradi.
  - Xato, maslahat va qadamlar rejasini O'ZBEK LOTIN yozuvida ko'rsatadi.
  - Hammasi xotira (SQLite) va jurnalga yoziladi.

KUZATUV INDIKATORI: yuqorida katta rangli holat ("● TAYYOR" / "● KO'RMOQDA").
PAUZA/STOP: istalgan vaqtda. Doimiy fon kuzatuvi yo'q — faqat tugma bosganda qaraydi.

AMAL BAJARISH (sichqoncha/klaviatura): amal.py da, MVP'da O'CHIQ (xavfsizlik).
"""
import os, sys, threading, time, traceback
import tkinter as tk
from tkinter import ttk, scrolledtext

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import xotira, koz, miya, amal

RANG = {"bg": "#14130f", "panel": "#201e18", "ink": "#efeadf", "mut": "#a79f8e",
        "acc": "#58b6a4", "ko": "#e0b64a", "xato": "#e07a5f", "chiz": "#36322a"}


class App:
    def __init__(self, root):
        self.root = root
        self.band = False  # hozir ko'rmoqdami
        xotira.boshlash()
        root.title("Jurat Yordamchi")
        root.configure(bg=RANG["bg"])
        root.geometry("560x680")
        root.minsize(440, 560)

        top = tk.Frame(root, bg=RANG["panel"]); top.pack(fill="x")
        self.holat = tk.Label(top, text="●  TAYYOR", fg=RANG["acc"], bg=RANG["panel"],
                              font=("Segoe UI", 15, "bold"), anchor="w", padx=16, pady=12)
        self.holat.pack(side="left")
        self.oyna_l = tk.Label(top, text="", fg=RANG["mut"], bg=RANG["panel"],
                               font=("Segoe UI", 9), anchor="e", padx=16)
        self.oyna_l.pack(side="right")

        info = tk.Label(root, text="Ekranni men so'raganimda ko'radi. Doimiy kuzatuv yo'q.",
                        fg=RANG["mut"], bg=RANG["bg"], font=("Segoe UI", 9), pady=4)
        info.pack(fill="x")

        tk.Label(root, text="Topshiriq (bo'sh qoldirsangiz — umumiy tekshiradi):",
                 fg=RANG["ink"], bg=RANG["bg"], anchor="w", padx=14).pack(fill="x")
        self.sorov = tk.Entry(root, font=("Segoe UI", 11), bg=RANG["panel"], fg=RANG["ink"],
                              insertbackground=RANG["ink"], relief="flat")
        self.sorov.pack(fill="x", padx=14, pady=(2, 8), ipady=6)
        self.sorov.bind("<Return>", lambda e: self.korish())

        btns = tk.Frame(root, bg=RANG["bg"]); btns.pack(fill="x", padx=14)
        self.b_kor = self._btn(btns, "🔍  Ekranni ko'r", self.korish, RANG["acc"], "#06241f")
        self.b_kor.pack(side="left")
        self.b_faol = tk.IntVar(value=1)
        tk.Checkbutton(btns, text="faqat faol oyna", variable=self.b_faol, bg=RANG["bg"],
                       fg=RANG["mut"], selectcolor=RANG["panel"], activebackground=RANG["bg"],
                       activeforeground=RANG["ink"], font=("Segoe UI", 9)).pack(side="left", padx=10)
        self._btn(btns, "⏸  Pauza", self.pauza, RANG["panel"], RANG["ink"]).pack(side="right")
        self._btn(btns, "⏹  Stop", self.stop, RANG["panel"], RANG["ink"]).pack(side="right", padx=6)

        tk.Label(root, text="Natija:", fg=RANG["ink"], bg=RANG["bg"], anchor="w",
                 padx=14).pack(fill="x", pady=(10, 0))
        self.out = scrolledtext.ScrolledText(root, font=("Segoe UI", 11), bg=RANG["panel"],
                                             fg=RANG["ink"], relief="flat", wrap="word", height=14,
                                             insertbackground=RANG["ink"], padx=10, pady=8)
        self.out.pack(fill="both", expand=True, padx=14, pady=6)
        self._yoz("Tayyor. «Ekranni ko'r» tugmasini bosing yoki topshiriq yozib Enter bosing.\n"
                  "Masalan: Excel reys jadvalini ochib, «xato yoki takror bormi» deb so'rang.")

        bot = tk.Frame(root, bg=RANG["bg"]); bot.pack(fill="x", padx=14, pady=(0, 10))
        self._btn(bot, "🕘  Tarix", self.tarix, RANG["panel"], RANG["mut"]).pack(side="left")
        tk.Label(bot, text="Amal bajarish (sichqoncha/klaviatura): hozircha o'chiq",
                 fg=RANG["mut"], bg=RANG["bg"], font=("Segoe UI", 8)).pack(side="right")

    def _btn(self, parent, text, cmd, bg, fg):
        return tk.Button(parent, text=text, command=cmd, bg=bg, fg=fg, relief="flat",
                         font=("Segoe UI", 10, "bold"), padx=14, pady=8, cursor="hand2",
                         activebackground=bg, activeforeground=fg)

    def _holat(self, matn, rang):
        self.holat.config(text=matn, fg=rang)

    def _yoz(self, matn, toza=True):
        if toza:
            self.out.delete("1.0", "end")
        self.out.insert("end", matn)
        self.out.see("end")

    def korish(self):
        if self.band:
            return
        self.band = True
        self.b_kor.config(state="disabled")
        self._holat("●  KO'RMOQDA…", RANG["ko"])
        self._yoz("Ekran o'qilmoqda…")
        threading.Thread(target=self._korish_ish, daemon=True).start()

    def _korish_ish(self):
        try:
            oyna = koz.faol_oyna_nomi()
            self.root.after(0, lambda: self.oyna_l.config(text=oyna[:48]))
            img = koz.surat(faqat_faol=bool(self.b_faol.get()))
            koz.saqla(img)
            ocr = koz.matn(img)
            self.root.after(0, lambda: self._yoz("Claude tahlil qilmoqda…"))
            sorov = self.sorov.get().strip()
            javob = miya.sora(ocr, sorov, oyna=oyna, kontekst=xotira.kontekst())
            xotira.vazifa_yoz(oyna, sorov, javob)
            xotira.jurnal_yoz("korish", f"oyna={oyna}; sorov={sorov}")
            self.root.after(0, lambda: self._yoz(javob))
        except Exception as e:
            err = "".join(traceback.format_exception_only(type(e), e)).strip()
            xotira.jurnal_yoz("xato", err)
            self.root.after(0, lambda: self._yoz(f"Xato: {err}\n\nTekshiring: mss, pillow, pytesseract o'rnatilganmi; Tesseract-OCR bormi."))
        finally:
            self.band = False
            self.root.after(0, lambda: (self.b_kor.config(state="normal"), self._holat("●  TAYYOR", RANG["acc"])))

    def pauza(self):
        self._holat("●  PAUZA", RANG["mut"])
        self._yoz("Pauza. «Ekranni ko'r» bosmaguningizcha hech narsa qilmayman.", toza=False)

    def stop(self):
        xotira.jurnal_yoz("stop", "foydalanuvchi to'xtatdi")
        self.root.destroy()

    def tarix(self):
        rows = xotira.oxirgi_vazifalar(15)
        if not rows:
            self._yoz("Tarix bo'sh."); return
        s = ["SO'NGGI VAZIFALAR:\n"]
        for vaqt, oyna, sorov, javob in rows:
            s.append(f"── {vaqt} · {oyna[:40]}\nSo'rov: {sorov}\n{(javob or '')[:400]}\n")
        self._yoz("\n".join(s))


def main():
    root = tk.Tk()
    try:
        root.tk.call("tk", "scaling", 1.2)
    except Exception:
        pass
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
