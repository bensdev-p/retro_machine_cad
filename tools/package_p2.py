"""Inline the P2 scene and vendored three.js (MIT) into a single offline viewer page."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; OUT = ROOT / 'outputs/p2'; V = ROOT / 'tools/vendor/three-0.147.0'
html = (ROOT / 'tools/p2_viewer_template.html').read_text()
for key, f in (('__THREE__', 'three.min.js'), ('__ORBIT__', 'OrbitControls.js'), ('__ROOM__', 'RoomEnvironment.js')):
    html = html.replace(key, (V / f).read_text().replace('</script', '<\\/script'))
import base64
post = OUT / 'screens/post.png'
html = html.replace('__POST__', 'data:image/png;base64,' + base64.b64encode(post.read_bytes()).decode() if post.exists() else '')
html = html.replace('__SCENE__', (OUT / 'scene.json').read_text())
(OUT / 'viewer.html').write_text(html)
print('wrote', OUT / 'viewer.html', round(len(html) / 1e6, 2), 'MB')
