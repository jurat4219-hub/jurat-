// Jonli o't maydoni (kutubxonasiz, canvas 2D). Sichqoncha yaqinidagi o't chetga egiladi, shamol to'lqinlari yuradi.
(() => {
  const cv = document.getElementById("grass"), ctx = cv.getContext("2d");
  let W, H, dpr, blades = [], mx = -9999, my = -9999, t = 0, running = true;
  const rnd = (a, b) => a + Math.random() * (b - a);
  function build() {
    dpr = Math.min(window.devicePixelRatio || 1, 1.5);
    W = cv.width = innerWidth * dpr; H = cv.height = innerHeight * dpr;
    blades = [];
    const n = Math.round(Math.min(2600, innerWidth * 1.9));
    for (let i = 0; i < n; i++) {
      const z = Math.random();                         // 0 = uzoq, 1 = yaqin
      const base = H * (0.58 + 0.42 * Math.pow(z, 1.4)) + rnd(-6, 6) * dpr;
      blades.push({
        x: rnd(-20, W + 20), y: base, z,
        h: (40 + 210 * Math.pow(z, 1.6)) * dpr * rnd(0.7, 1.15),
        w: (1.2 + 5.5 * z) * dpr,
        ph: rnd(0, Math.PI * 2), bend: 0,
        hue: rnd(62, 84), lit: 18 + 38 * z + rnd(-6, 6)
      });
    }
    blades.sort((a, b) => a.z - b.z);
  }
  function frame() {
    if (!running) return;
    t += 0.016;
    ctx.clearRect(0, 0, W, H);
    // osmon yorug'ligi
    const g = ctx.createRadialGradient(W / 2, H * 0.62, 0, W / 2, H * 0.62, W * 0.7);
    g.addColorStop(0, "rgba(120,140,40,0.22)"); g.addColorStop(1, "rgba(0,0,0,0)");
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    for (const b of blades) {
      const wind = Math.sin(t * 1.3 + b.x * 0.004 + b.ph * 0.3) * 0.5 + Math.sin(t * 0.55 + b.x * 0.0013) * 0.7;
      // sichqoncha ta'siri
      const dx = b.x - mx, dy = (b.y - b.h * 0.6) - my, dist = Math.hypot(dx, dy), R = 170 * dpr;
      let push = 0;
      if (dist < R) push = (1 - dist / R) * Math.sign(dx || 1) * 1.6;
      b.bend += ((wind * (0.35 + 0.65 * b.z)) + push - b.bend) * 0.08;
      const tipX = b.x + b.bend * b.h * 0.55, tipY = b.y - b.h * (1 - Math.min(0.45, Math.abs(b.bend) * 0.22));
      const cX = b.x + b.bend * b.h * 0.18, cY = b.y - b.h * 0.55;
      ctx.beginPath();
      ctx.moveTo(b.x - b.w, b.y);
      ctx.quadraticCurveTo(cX - b.w * 0.6, cY, tipX, tipY);
      ctx.quadraticCurveTo(cX + b.w * 0.6, cY, b.x + b.w, b.y);
      ctx.closePath();
      const blur = 1 - b.z;                              // uzoqdagilar xiraroq
      ctx.fillStyle = `hsla(${b.hue},${55 + 15 * b.z}%,${b.lit}%,${0.35 + 0.65 * b.z - blur * 0.1})`;
      ctx.fill();
    }
    // pastki qorong'ilik (matn o'qilishi uchun)
    const v = ctx.createLinearGradient(0, H * 0.75, 0, H);
    v.addColorStop(0, "rgba(5,6,5,0)"); v.addColorStop(1, "rgba(5,6,5,0.55)");
    ctx.fillStyle = v; ctx.fillRect(0, H * 0.75, W, H * 0.25);
    requestAnimationFrame(frame);
  }
  addEventListener("resize", build);
  addEventListener("pointermove", e => { mx = e.clientX * dpr; my = e.clientY * dpr; });
  addEventListener("pointerleave", () => { mx = my = -9999; });
  document.addEventListener("visibilitychange", () => {   // varaq ko'rinmasa — to'xtaydi (kompyuter qizimaydi)
    running = !document.hidden; if (running) requestAnimationFrame(frame);
  });
  build(); requestAnimationFrame(frame);
})();
