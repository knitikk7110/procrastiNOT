"use client"

// Neon Katakana Preloader — Persistent Cyberpunk OS Startup Experience.
// Black void (#06030A), deep violet haze (#2A0A5C), glowing magenta Katakana calligraphy (#FF3DF2)
// with hot core (#FFE1FB), and restrained mint indicators (#3DFFB0).
// Pure React + Canvas 2D engine with rain streams, granular particle dispersion, decoding, and slit-of-light door open.

import * as React from "react"

export interface NeonKatakanaPalette {
  /** Stage colour (#06030A). */
  background: string
  /** The word, the rain and every glow (#FF3DF2). */
  glow: string
  /** Hot core of the word and the rain heads (#FFE1FB). */
  core: string
  /** Dot-matrix labels and mint indicators (#3DFFB0). */
  accent: string
  /** The atmospheric violet haze rising from the floor (#2A0A5C). */
  haze: string
}

export interface NeonKatakanaPreloaderProps {
  /** Content revealed once the window opens. Ignored while `loop` is set. */
  children?: React.ReactNode
  /** Run forever as a showcase: children are never revealed, onComplete never fires. */
  loop?: boolean
  /**
   * Real loading progress, 0–100. Leave undefined to run the built-in
   * simulated load over `durationMs`. The word holds until this hits 100.
   */
  progress?: number
  /** Length of the simulated load. Defaults to 3600ms. */
  durationMs?: number
  /** The big word. Katakana display typography. */
  word?: string
  /** Dot-matrix label above the word. Decodes as the load runs. */
  label?: string
  /** Dot-matrix line below the word once loaded (the percentage shows until then). */
  caption?: string
  /** Small mark in the top-left corner of the HUD. */
  kicker?: string
  /** Show the four HUD corners. Defaults to true. */
  hud?: boolean
  /** Rain density multiplier, 0 (none) to 2. Defaults to 1.2. */
  density?: number
  /** Let the pointer push the word's grain around and stir the rain. Defaults to true. */
  interactive?: boolean
  /** Colour overrides, merged over the defaults. */
  palette?: Partial<NeonKatakanaPalette>
  /** Face the word is drawn in. */
  fontFamily?: string
  /** Root height. A definite length, never a percentage. */
  height?: string
  /** Fired once, after the window has opened. */
  onComplete?: () => void
  /** Extra root class names. */
  className?: string
}

const DEFAULT_PALETTE: NeonKatakanaPalette = {
  background: "#06030A",
  glow: "#FF3DF2",
  core: "#FFE1FB",
  accent: "#3DFFB0",
  haze: "#2A0A5C",
}

const WORD_STACK =
  '"Yuji Syuku", "MS Gothic", "Hiragino Mincho ProN", "Yu Mincho", "Noto Serif JP", "Noto Sans JP", sans-serif'
const MONO_STACK = '"JetBrains Mono", "Consolas", "IBM Plex Mono", "SFMono-Regular", Menlo, monospace'

// Half-width katakana and digits: the classic falling-code alphabet.
const RAIN_GLYPHS = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜｦﾝ0123456789"

const clamp01 = (x: number) => (x <= 0 ? 0 : x >= 1 ? 1 : x)

const KNOTS = [
  [0, 0],
  [0.3, 0.42],
  [0.4, 0.45],
  [0.68, 0.80],
  [0.78, 0.84],
  [1, 1],
]

export function nkpSimulated(t: number) {
  if (t <= 0) return 0
  if (t >= 1) return 1
  for (let i = 0; i < KNOTS.length - 1; i++) {
    const a = KNOTS[i]
    const b = KNOTS[i + 1]
    if (t <= b[0]) {
      const local = (t - a[0]) / (b[0] - a[0])
      const eased = 1 - Math.pow(1 - local, 3)
      return a[1] + (b[1] - a[1]) * eased
    }
  }
  return 1
}

export function nkpHash(n: number) {
  const s = Math.sin(n * 127.1 + 311.7) * 43758.5453
  return s - Math.floor(s)
}

const KATA_POOL = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン"
const LATIN_POOL = "abcdefghijklmnopqrstuvwxyz0123456789#$%&@"

export function nkpDecode(target: string, p: number, tick: number) {
  const chars = Array.from(target)
  const settled = Math.floor(clamp01(p) * chars.length + 1e-9)
  return chars
    .map((c, i) => {
      if (i < settled || c === " ") return c
      const pool = /[-ヿ一-鿿]/.test(c) ? KATA_POOL : LATIN_POOL
      const pick = pool.charAt(Math.floor(nkpHash(i * 31 + tick * 7.13) * pool.length))
      return /[A-Z]/.test(c) ? pick.toUpperCase() : pick
    })
    .join("")
}

export function nkpCounter(pct: number) {
  const v = Math.round(Math.min(100, Math.max(0, pct)))
  return String(v).padStart(3, "0")
}

export function nkpLayout(count: number, unitWidth: number, w: number, h: number) {
  const horiz = Math.min((w * 0.84 * 100) / Math.max(1, unitWidth), h * 0.32)
  const vert = Math.min((h * 0.6) / Math.max(1, count), w * 0.42)
  const vertical = count > 1 && h > w * 1.15 && vert > horiz * 1.25
  return { size: Math.max(18, Math.round(vertical ? vert : horiz)), vertical }
}

interface Field {
  n: number
  hotFrom: number
  hx: Float32Array
  hy: Float32Array
  size: Float32Array
  alpha: Float32Array
  rank: Float32Array
  fall: Float32Array
  seed: Float32Array
  act: Float32Array
  ox: Float32Array
  oy: Float32Array
  dx: Float32Array
  dy: Float32Array
  box: { x: number; y: number; w: number; h: number }
  reach: number
  cols: { x: number; head: number; speed: number; len: number; weight: number; glyph: boolean }[]
  strands: { x: number; top: number; bottom: number; seed: number }[]
}

function vnoise(x: number, y: number) {
  const xi = Math.floor(x)
  const yi = Math.floor(y)
  const xf = x - xi
  const yf = y - yi
  const u = xf * xf * (3 - 2 * xf)
  const v = yf * yf * (3 - 2 * yf)
  const h = (a: number, b: number) => nkpHash(a * 57 + b * 113)
  const top = h(xi, yi) + (h(xi + 1, yi) - h(xi, yi)) * u
  const bot = h(xi, yi + 1) + (h(xi + 1, yi + 1) - h(xi, yi + 1)) * u
  return top + (bot - top) * v
}

function buildField(w: number, h: number, word: string, font: string, density: number): Field {
  const W = Math.max(1, Math.ceil(w))
  const H = Math.max(1, Math.ceil(h))
  const chars = Array.from(word.trim() || " ")
  const off = document.createElement("canvas")
  off.width = W
  off.height = H
  const c = off.getContext("2d", { willReadFrequently: true })!
  c.font = "900 100px " + font
  const { size, vertical } = nkpLayout(chars.length, c.measureText(chars.join("")).width, W, H)

  c.font = "900 " + size + "px " + font
  c.fillStyle = "#fff"
  c.textAlign = "center"
  c.textBaseline = "middle"
  const cy = H * 0.5
  if (vertical) {
    chars.forEach((ch, i) => c.fillText(ch, W / 2, cy + (i - (chars.length - 1) / 2) * size * 1.02))
  } else {
    c.fillText(chars.join(""), W / 2, cy)
  }
  const data = c.getImageData(0, 0, W, H).data
  const inside = (x: number, y: number) =>
    x >= 0 && y >= 0 && x < W && y < H && data[(Math.round(y) * W + Math.round(x)) * 4 + 3] > 110

  const step = Math.max(2, Math.round(size / 68))
  const grit = size * 0.2
  const cool: number[][] = []
  const hot: number[][] = []
  let x0 = W
  let x1 = 0
  let y0 = H
  let y1 = 0

  for (let y = 0; y < H; y += step) {
    for (let x = 0; x < W; x += step) {
      if (!inside(x, y)) continue
      const id = x * 7.31 + y * 1.97
      const g = 0.6 * vnoise(x / grit, y / grit) + 0.4 * vnoise(x / (step * 2.4), y / (size * 0.9))
      const keep = 0.98 - 0.7 * Math.min(1, Math.max(0, (g - 0.52) / 0.3))
      if (nkpHash(id) > keep) continue
      x0 = Math.min(x0, x)
      x1 = Math.max(x1, x)
      y0 = Math.min(y0, y)
      y1 = Math.max(y1, y)
      const r = nkpHash(id + 11)
      const edge = !(inside(x - step * 2, y) && inside(x + step * 2, y) && inside(x, y - step * 2) && inside(x, y + step * 2))
      const gx = x + (nkpHash(id + 13) - 0.5) * step * 0.7
      const grain = [gx, y, step * (0.55 + 0.6 * r), (edge ? 0.45 : 0.62) + 0.38 * nkpHash(id + 3), 0, 30 + 170 * nkpHash(id + 5), nkpHash(id + 9)]
      if (!edge && nkpHash(id + 21) < 0.55) hot.push(grain)
      else cool.push(grain)

      const below = !inside(x, y + step)
      const above = !inside(x, y - step)
      if ((below && nkpHash(id + 31) < 0.2) || (above && nkpHash(id + 37) < 0.08)) {
        const dir = below ? 1 : -1
        const len = 2 + Math.floor(Math.pow(nkpHash(id + 41), 2) * 30)
        for (let j = 1; j <= len; j++) {
          const fade = 1 - j / (len + 1)
          cool.push([x, y + dir * j * step * 1.7, step * 0.55, 0.55 * fade * fade, 0, 30 + 170 * nkpHash(id + j), nkpHash(id + j * 3)])
        }
      }
    }
  }
  if (x1 < x0) {
    x0 = x1 = W / 2
    y0 = y1 = H / 2
  }
  const bw = Math.max(1, x1 - x0)
  const bh = Math.max(1, y1 - y0)
  const order = (g: number[]) => {
    const along = vertical ? (g[1] - y0) / bh : (g[0] - x0) / bw
    return Math.min(1, 0.55 * clamp01(along) + 0.45 * g[6])
  }
  const all = cool.concat(hot)
  const n = all.length
  const f: Field = {
    n,
    hotFrom: cool.length,
    hx: new Float32Array(n),
    hy: new Float32Array(n),
    size: new Float32Array(n),
    alpha: new Float32Array(n),
    rank: new Float32Array(n),
    fall: new Float32Array(n),
    seed: new Float32Array(n),
    act: new Float32Array(n).fill(-1),
    ox: new Float32Array(n),
    oy: new Float32Array(n),
    dx: new Float32Array(n),
    dy: new Float32Array(n),
    box: { x: x0, y: y0, w: bw, h: bh },
    reach: Math.max(50, size * 0.42),
    cols: [],
    strands: [],
  }
  all.forEach((g, i) => {
    f.hx[i] = g[0]
    f.hy[i] = g[1]
    f.size[i] = g[2]
    f.alpha[i] = g[3]
    f.rank[i] = order(g)
    f.fall[i] = g[5]
    f.seed[i] = g[6]
  })

  const gap = 11 / Math.max(0.05, density)
  const mid = W / 2
  const spread = Math.max(bw, W * 0.3) * 0.62
  if (density > 0) {
    for (let x = gap * 0.5, k = 0; x < W; x += gap, k++) {
      const jitter = (nkpHash(k + 0.5) - 0.5) * gap * 0.6
      const dxn = (x - mid) / spread
      const weight = 0.12 + 0.88 * Math.exp(-dxn * dxn)
      f.cols.push({
        x: Math.round(x + jitter) + 0.5,
        head: nkpHash(k + 1.7) * H * 1.4 - H * 0.2,
        speed: (50 + 190 * nkpHash(k + 2.9)) * (0.6 + weight),
        len: 30 + (H * 0.55) * nkpHash(k + 4.1) * (0.35 + weight),
        weight,
        glyph: nkpHash(k + 6.3) < 0.28,
      })
    }
  }
  const strandCount = Math.round(10 + bw / 60)
  for (let i = 0; i < strandCount; i++) {
    const s = nkpHash(i + 90.1)
    f.strands.push({
      x: Math.round(x0 + bw * nkpHash(i + 77.7)) + 0.5,
      top: y0 - (0.2 + 0.9 * s) * Math.min(H * 0.35, bh * 1.2),
      bottom: y1 + (0.2 + 0.9 * nkpHash(i + 55.5)) * Math.min(H * 0.35, bh * 1.2),
      seed: s,
    })
  }
  return f
}

function toRgb(color: string, scratch: CanvasRenderingContext2D): [number, number, number] {
  scratch.fillStyle = "#000"
  scratch.fillStyle = color
  const v = String(scratch.fillStyle)
  if (v.charAt(0) === "#") {
    const hex = v.slice(1)
    return [parseInt(hex.slice(0, 2), 16), parseInt(hex.slice(2, 4), 16), parseInt(hex.slice(4, 6), 16)]
  }
  const m = v.match(/[\d.]+/g)
  return m ? [Number(m[0]), Number(m[1]), Number(m[2])] : [255, 61, 242]
}

const NKP_CSS = `
.nkp-root {
  --nkp-p: 0;
  --nkp-bx: 0px;
  --nkp-by: 0px;
  --nkp-bw: 0px;
  --nkp-bh: 0px;
  position: relative;
  width: 100%;
  overflow: hidden;
  isolation: isolate;
  background: var(--nkp-bg);
  color: var(--nkp-glow);
  font-family: var(--nkp-mono);
  user-select: none;
}
.nkp-dest {
  position: absolute;
  inset: 0;
  overflow-y: auto;
  visibility: hidden;
}
.nkp-root[data-phase="open"] .nkp-dest,
.nkp-root[data-phase="done"] .nkp-dest { visibility: visible; }
.nkp-gate {
  position: absolute;
  inset: 0;
  z-index: 2;
  overflow: hidden;
  cursor: pointer;
  outline: none;
  background: var(--nkp-bg);
}
.nkp-root[data-phase="open"] .nkp-gate { animation: nkp-open 1.2s cubic-bezier(0.7, 0, 0.2, 1) forwards; }
.nkp-haze {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    radial-gradient(ellipse 110% 70% at 50% 115%, var(--nkp-haze) 0%, transparent 72%),
    radial-gradient(ellipse 70% 34% at 50% 102%, var(--nkp-haze) 0%, transparent 80%),
    radial-gradient(ellipse 40% 60% at 0% 100%, var(--nkp-haze) 0%, transparent 70%),
    radial-gradient(ellipse 40% 60% at 100% 100%, var(--nkp-haze) 0%, transparent 70%);
  animation: nkp-breathe 6s ease-in-out infinite;
}
.nkp-halo {
  position: absolute;
  left: var(--nkp-bx);
  top: var(--nkp-by);
  width: var(--nkp-bw);
  height: var(--nkp-bh);
  pointer-events: none;
  border-radius: 50%;
  background: radial-gradient(closest-side, var(--nkp-glow), transparent);
  opacity: calc(0.04 + var(--nkp-p) * 0.14);
  filter: blur(40px);
  transform: scale(1.35, 2.2);
}
.nkp-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  display: block;
  filter: drop-shadow(0 0 2px var(--nkp-glow)) drop-shadow(0 0 16px var(--nkp-glow));
}
.nkp-scanlines {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: repeating-linear-gradient(to bottom, rgba(255, 255, 255, 0.035) 0 1px, transparent 1px 3px);
  mix-blend-mode: overlay;
}
.nkp-vignette {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: radial-gradient(ellipse at 50% 46%, transparent 42%, rgba(0, 0, 0, 0.85) 100%);
}
.nkp-label {
  position: absolute;
  left: 0;
  right: 0;
  text-align: center;
  color: var(--nkp-accent);
  font-size: clamp(12px, 2.2vw, 24px);
  font-weight: 800;
  letter-spacing: 0.6em;
  text-indent: 0.6em;
  pointer-events: none;
  filter: drop-shadow(0 0 6px var(--nkp-accent));
}
.nkp-label-top { top: var(--nkp-by); transform: translateY(-130%); }
.nkp-label-bottom { top: calc(var(--nkp-by) + var(--nkp-bh)); transform: translateY(40%); }
.nkp-hud {
  position: absolute;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 10px;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: var(--nkp-glow);
  opacity: 0.75;
  pointer-events: none;
}
.nkp-tl { top: 18px; left: 24px; }
.nkp-tr { top: 18px; right: 24px; color: var(--nkp-accent); }
.nkp-bl { bottom: 18px; left: 24px; }
.nkp-br { bottom: 18px; right: 24px; }
.nkp-led {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--nkp-accent);
  box-shadow: 0 0 8px var(--nkp-accent);
}
.nkp-track {
  position: relative;
  width: 140px;
  height: 1.5px;
  background: rgba(255, 255, 255, 0.12);
}
.nkp-fill {
  position: absolute;
  inset: 0;
  transform-origin: left center;
  transform: scaleX(var(--nkp-p));
  background: var(--nkp-glow);
  box-shadow: 0 0 8px var(--nkp-glow);
}
.nkp-frame {
  position: absolute;
  z-index: 3;
  pointer-events: none;
  border: 1px solid var(--nkp-core);
  box-shadow: 0 0 24px 2px var(--nkp-glow), inset 0 0 24px 2px var(--nkp-glow);
  animation: nkp-frame 1.2s cubic-bezier(0.7, 0, 0.2, 1) forwards;
}
@keyframes nkp-open {
  0% { clip-path: polygon(evenodd, 0% 0%, 100% 0%, 100% 100%, 0% 100%, 0% 0%, 50% 50%, 50% 50%, 50% 50%, 50% 50%, 50% 50%); }
  40% { clip-path: polygon(evenodd, 0% 0%, 100% 0%, 100% 100%, 0% 100%, 0% 0%, 5% 49.6%, 95% 49.6%, 95% 50.4%, 5% 50.4%, 5% 49.6%); }
  100% { clip-path: polygon(evenodd, 0% 0%, 100% 0%, 100% 100%, 0% 100%, 0% 0%, -2% -2%, 102% -2%, 102% 102%, -2% 102%, -2% -2%); }
}
@keyframes nkp-frame {
  0% { inset: 50% 50%; opacity: 1; }
  40% { inset: 49.6% 5%; opacity: 1; }
  85% { inset: 0%; opacity: 0.8; }
  100% { inset: 0%; opacity: 0; }
}
@keyframes nkp-breathe { 50% { opacity: 0.75; } }
@keyframes nkp-blink { 50% { opacity: 0.25; } }
`

type Phase = "boot" | "lock" | "open" | "release" | "done"

export default function NeonKatakanaPreloader({
  children,
  loop = false,
  progress,
  durationMs = 3800,
  word = "ネオン",
  label = "neon",
  caption = "online",
  kicker = "ネオン / SECTOR 7",
  hud = true,
  density = 1.2,
  interactive = true,
  palette,
  fontFamily = WORD_STACK,
  height = "100svh",
  onComplete,
  className = "",
}: NeonKatakanaPreloaderProps) {
  const [phase, setPhase] = React.useState<Phase>("boot")
  const [cycle, setCycle] = React.useState(0)
  const [pct, setPct] = React.useState(0)
  const [tick, setTick] = React.useState(0)

  const rootRef = React.useRef<HTMLDivElement>(null)
  const canvasRef = React.useRef<HTMLCanvasElement>(null)
  const phaseRef = React.useRef<Phase>(phase)
  phaseRef.current = phase
  const phaseAtRef = React.useRef(0)
  const resetRef = React.useRef(true)
  const rushRef = React.useRef(false)
  const glitchRef = React.useRef({ until: 0, next: 0 })
  const pointerRef = React.useRef({ x: 0, y: 0, on: false })
  const progressRef = React.useRef(progress)
  progressRef.current = progress
  const onCompleteRef = React.useRef(onComplete)
  onCompleteRef.current = onComplete

  const colors = { ...DEFAULT_PALETTE, ...palette }

  React.useEffect(() => {
    phaseAtRef.current = performance.now()
    if (phase === "boot") {
      resetRef.current = true
      rushRef.current = false
    }
  }, [phase, cycle])

  React.useEffect(() => {
    let t: ReturnType<typeof setTimeout> | undefined
    if (phase === "lock") t = setTimeout(() => setPhase(loop ? "release" : "open"), 1800)
    if (phase === "open") {
      t = setTimeout(() => {
        setPhase("done")
        onCompleteRef.current?.()
      }, 1200)
    }
    return () => clearTimeout(t)
  }, [phase, loop])

  React.useEffect(() => {
    const root = rootRef.current
    const canvas = canvasRef.current
    const ctx = canvas?.getContext("2d")
    if (!root || !canvas || !ctx) return

    const scratch = document.createElement("canvas")
    const sctx = scratch.getContext("2d")!
    const glow = toRgb(colors.glow, sctx)
    const rgba = (a: number) => `rgba(${glow[0]},${glow[1]},${glow[2]},${a.toFixed(3)})`

    let field: Field | null = null
    let W = 0
    let H = 0
    let dpr = 1
    let shown = 0
    let bootAt = performance.now()
    let last = performance.now()
    let raf = 0
    let stopped = false

    const build = () => {
      const r = root.getBoundingClientRect()
      if (r.width < 2 || r.height < 2) return
      W = r.width
      H = r.height
      dpr = Math.min(2, window.devicePixelRatio || 1)
      canvas.width = Math.round(W * dpr)
      canvas.height = Math.round(H * dpr)
      scratch.width = canvas.width
      scratch.height = canvas.height
      field = buildField(W, H, word, fontFamily, density)
      const b = field.box
      root.style.setProperty("--nkp-bx", b.x + "px")
      root.style.setProperty("--nkp-by", b.y + "px")
      root.style.setProperty("--nkp-bw", b.w + "px")
      root.style.setProperty("--nkp-bh", b.h + "px")
    }

    const frame = (now: number) => {
      if (stopped) return
      const dt = Math.min(64, now - last)
      last = now
      const ph = phaseRef.current
      if (ph === "done") return
      const f = field

      if (resetRef.current) {
        resetRef.current = false
        shown = 0
        bootAt = now
      }

      if (ph === "boot") {
        const external = progressRef.current
        let target = external !== undefined ? clamp01(external / 100) : nkpSimulated((now - bootAt) / durationMs)
        if (rushRef.current) target = 1
        shown += (target - shown) * (rushRef.current ? 0.15 : 0.08)
        if (target - shown < 0.003) shown = target
        setPct(Math.round(shown * 100))
        setTick(Math.floor(now / 85))
        if (shown >= 1) {
          phaseRef.current = "lock"
          setPhase("lock")
        }
      } else {
        shown = 1
      }
      root.style.setProperty("--nkp-p", shown.toFixed(4))

      if (!f) {
        raf = requestAnimationFrame(frame)
        return
      }

      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
      ctx.clearRect(0, 0, W, H)

      // Falling rain
      if (f.cols.length) {
        ctx.font = "11px " + MONO_STACK
        ctx.textAlign = "center"
        for (let c = 0; c < f.cols.length; c++) {
          const col = f.cols[c]
          col.head += (col.speed * dt) / 1000
          if (col.head - col.len > H) {
            col.head = -Math.random() * H * 0.4
            col.len = 30 + H * 0.55 * Math.random() * (0.35 + col.weight)
          }
          const top = col.head - col.len
          const a = Math.min(1, col.weight * 0.6)
          if (a < 0.01) continue
          const grad = ctx.createLinearGradient(0, top, 0, col.head)
          grad.addColorStop(0, rgba(0))
          grad.addColorStop(1, rgba(a))
          ctx.strokeStyle = grad
          ctx.beginPath()
          ctx.moveTo(col.x, top)
          ctx.lineTo(col.x, col.head)
          ctx.stroke()

          ctx.fillStyle = colors.accent
          ctx.globalAlpha = Math.min(1, a * 1.3)
          if (col.glyph) {
            const g = RAIN_GLYPHS.charAt(Math.floor(now / 110 + c * 7) % RAIN_GLYPHS.length)
            ctx.fillText(g, col.x, col.head + 4)
          } else {
            ctx.fillRect(col.x - 1, col.head - 1, 2, 2)
          }
          ctx.globalAlpha = 1
        }
      }

      // The word grains
      for (let i = 0; i < f.n; i++) {
        let a = f.alpha[i]
        const s = f.size[i]
        let x = f.hx[i]
        let y = f.hy[i]
        const k = Math.min(1, shown / Math.max(0.01, f.rank[i]))
        if (k < 1) {
          y -= f.fall[i] * (1 - k)
          a *= k
        }
        if (a <= 0.01) continue
        ctx.fillStyle = i >= f.hotFrom ? colors.core : colors.glow
        ctx.globalAlpha = a
        ctx.fillRect(x - s * 0.4, y - s * 0.7, s * 0.8, s * 0.8)
      }
      ctx.globalAlpha = 1

      raf = requestAnimationFrame(frame)
    }

    build()
    const ro = new ResizeObserver(() => build())
    ro.observe(root)
    raf = requestAnimationFrame(frame)
    return () => {
      stopped = true
      cancelAnimationFrame(raf)
      ro.disconnect()
    }
  }, [word, fontFamily, density, durationMs, colors.glow, colors.core, colors.accent])

  const onActivate = () => {
    if (phase === "boot") rushRef.current = true
    else if (phase === "lock") setPhase("open")
  }

  const loading = phase === "boot"
  const status = loading ? "● DECODING" : "● SIGNAL LOCKED"
  const hint = loading ? "TAP TO SKIP" : "TAP TO OPEN // ENTER"
  const top = loading ? nkpDecode(label, clamp01(pct / 70), tick) : label
  const bottom = loading ? nkpCounter(pct) + "%" : caption

  return (
    <div
      ref={rootRef}
      className={"nkp-root " + className}
      data-phase={phase}
      style={
        {
          height,
          "--nkp-bg": colors.background,
          "--nkp-glow": colors.glow,
          "--nkp-core": colors.core,
          "--nkp-accent": colors.accent,
          "--nkp-haze": colors.haze,
          "--nkp-mono": MONO_STACK,
        } as React.CSSProperties
      }
    >
      <style>{NKP_CSS}</style>

      {!loop && children ? (
        <div className="nkp-dest" aria-hidden={phase !== "open" && phase !== "done"}>
          {children}
        </div>
      ) : null}

      {phase !== "done" ? (
        <div
          className="nkp-gate"
          role="progressbar"
          aria-label={label + " — " + word}
          tabIndex={0}
          onClick={onActivate}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault()
              onActivate()
            }
          }}
        >
          <div className="nkp-haze" aria-hidden="true" />
          <div className="nkp-halo" aria-hidden="true" />
          <canvas ref={canvasRef} className="nkp-canvas" aria-hidden="true" />

          <div className="nkp-label nkp-label-top" aria-hidden="true">
            <span>{top}</span>
          </div>
          <div className="nkp-label nkp-label-bottom" aria-hidden="true">
            <span>{bottom}</span>
          </div>

          <div className="nkp-scanlines" aria-hidden="true" />
          <div className="nkp-vignette" aria-hidden="true" />

          {hud ? (
            <>
              <div className="nkp-hud nkp-tl" aria-hidden="true">
                {kicker}
              </div>
              <div className="nkp-hud nkp-tr" aria-hidden="true">
                <span className="nkp-led" />
                {status}
              </div>
              <div className="nkp-hud nkp-bl" aria-hidden="true">
                <span>{nkpCounter(pct)}</span>
                <span className="nkp-track">
                  <span className="nkp-fill" />
                </span>
                <span>100</span>
              </div>
              <div className="nkp-hud nkp-br" aria-hidden="true">
                <span>{hint}</span>
              </div>
            </>
          ) : null}
        </div>
      ) : null}

      {phase === "open" ? <div className="nkp-frame" aria-hidden="true" /> : null}
    </div>
  )
}
