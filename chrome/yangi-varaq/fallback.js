// WebGPU/WebGL 3D o't 6 soniyada ishga tushmasa — oddiy (2D) o't animatsiyasini yoqadi
setTimeout(() => {
  if (document.documentElement.classList.contains("g3d-ok")) return;
  document.documentElement.classList.add("g3d-fail");
  const s = document.createElement("script"); s.src = "grass.js"; document.body.append(s);
}, 6000);
