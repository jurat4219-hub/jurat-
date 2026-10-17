// Ish saytlari — o'zgartirish uchun shu ro'yxatni tahrirlang
const LINKS = [
  ["Didox", "https://didox.uz"],
  ["my.soliq", "https://my.soliq.uz"],
  ["Soliq servis", "https://soliqservis.uz"],
  ["Xalq Bank", "https://xb.uz"],
  ["Trast Bank", "https://trustbank.uz"],
  ["Orginfo", "https://orginfo.uz"],
  ["Registr.stat", "https://registr.stat.uz"],
  ["Gmail", "https://mail.google.com"],
  ["Claude", "https://claude.ai"],
  ["GitHub", "https://github.com/jurat4219-hub/jurat-"]
];
const nav = document.getElementById("links");
for (const [name, url] of LINKS) {
  const a = document.createElement("a"); a.href = url;
  const img = document.createElement("img");
  img.src = "https://www.google.com/s2/favicons?sz=64&domain=" + new URL(url).hostname; img.alt = "";
  img.addEventListener("error", () => {           // internet/ikonka bo'lmasa — bosh harf
    const f = document.createElement("b"); f.className = "harf"; f.textContent = name[0]; img.replaceWith(f);
  });
  const s = document.createElement("span"); s.textContent = name;
  a.append(img, s); nav.append(a);
}
const OY = ["yanvar","fevral","mart","aprel","may","iyun","iyul","avgust","sentabr","oktabr","noyabr","dekabr"];
const KUN = ["yakshanba","dushanba","seshanba","chorshanba","payshanba","juma","shanba"];
function tick() {
  const d = new Date();
  document.getElementById("time").textContent = String(d.getHours()).padStart(2, "0") + ":" + String(d.getMinutes()).padStart(2, "0");
  document.getElementById("date").textContent = `${KUN[d.getDay()]} · ${d.getDate()} ${OY[d.getMonth()]} ${d.getFullYear()}`;
}
tick(); setInterval(tick, 10000);
// manzil yozilsa — to'g'ridan-to'g'ri ochish
document.getElementById("search").addEventListener("submit", e => {
  const v = document.getElementById("q").value.trim();
  if (/^[\w-]+(\.[\w-]+)+(\/\S*)?$/.test(v) && !/\s/.test(v)) { e.preventDefault(); location.href = "https://" + v; }
});
