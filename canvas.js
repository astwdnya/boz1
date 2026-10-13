// Size once before OffscreenCanvas transfer. Resize only the CSS rectangle:
// the engine keeps its render targets and projection at this fixed resolution.
export function sizeGameCanvas(canvas) {
  const query = new URLSearchParams(location.search);
  const resParam = query.get('res') || localStorage.getItem('bo1z-res') || '720p';

  let targetW = 1280, targetH = 720;
  if (resParam === '1080p') {
    targetW = 1920; targetH = 1080;
  } else if (resParam === '900p') {
    targetW = 1600; targetH = 900;
  } else if (resParam === '540p') {
    targetW = 960; targetH = 540;
  } else if (resParam === 'native') {
    const width = Math.max(1, innerWidth), height = Math.max(1, innerHeight);
    const density = Math.min(devicePixelRatio || 1, 1920 / width, 1440 / height);
    const scale = Math.max(density, 800 / width, 600 / height);
    targetW = Math.round(width * scale);
    targetH = Math.round(height * scale);
  } else {
    // 720p standard HD: Xbox 360 / PS3 authentic native resolution (Rock-solid 60 FPS)
    targetW = 1280; targetH = 720;
  }

  canvas.width = targetW;
  canvas.height = targetH;
  const buffer = { width: canvas.width, height: canvas.height, devicePixelRatio };

  function fit() {
    const scale = Math.min(innerWidth / buffer.width, innerHeight / buffer.height);
    canvas.style.width = `${buffer.width * scale}px`;
    canvas.style.height = `${buffer.height * scale}px`;
  }
  fit();
  window.addEventListener('resize', fit);
  return { ...buffer, dispose: () => window.removeEventListener('resize', fit) };
}
