const outerDots = [
  [48, 15], [62, 18], [73, 27], [81, 40], [81, 56], [73, 69], [62, 78], [48, 81], [34, 78], [23, 69], [15, 56], [15, 40], [23, 27], [34, 18],
] as const

const middleDots = [
  [48, 26], [63, 31], [70, 46], [65, 62], [48, 70], [32, 64], [26, 47], [33, 32],
] as const

const innerDots = [
  [48, 37], [59, 43], [58, 55], [48, 62], [38, 55], [37, 43],
] as const

export function SiftLogo() {
  return <svg className="sift-logo-art" viewBox="0 0 36 36" aria-hidden="true" focusable="false">
    <path className="logo-bowl" d="M5 7h10.5l5 6H31v7.5a13 12.5 0 0 1-26 0V7Z" />
    <circle className="logo-seed" cx="11" cy="19" r="2.2" />
    <circle className="logo-seed" cx="17" cy="19" r="2.2" />
    <circle className="logo-seed" cx="23" cy="19" r="2.2" />
    <circle className="logo-seed" cx="14" cy="24" r="2.2" />
    <circle className="logo-seed" cx="20" cy="24" r="2.2" />
    <circle className="logo-seed" cx="17" cy="29" r="2.2" />
    <circle className="logo-signal" cx="27" cy="15" r="2.1" />
  </svg>
}

export function ThemeIcon({ darkMode }: { darkMode: boolean }) {
  return darkMode
    ? <svg className="theme-glyph" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="3.7" /><path d="M12 2v2m0 16v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42" /></svg>
    : <svg className="theme-glyph" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M20.2 15.1A8.2 8.2 0 0 1 8.9 3.8 8.3 8.3 0 1 0 20.2 15.1Z" /></svg>
}

export function SiftOrb() {
  return <svg className="sift-orb-art" viewBox="0 0 96 96" aria-hidden="true" focusable="false">
    <circle className="orb-shell" cx="48" cy="48" r="45" />
    <g className="orb-dots orb-dots-outer">{outerDots.map(([cx, cy]) => <circle key={`${cx}-${cy}`} className="orb-dot orb-dot-small" cx={cx} cy={cy} r="1.65" />)}</g>
    <g className="orb-dots orb-dots-middle">{middleDots.map(([cx, cy]) => <circle key={`${cx}-${cy}`} className="orb-dot orb-dot-medium" cx={cx} cy={cy} r="2.25" />)}</g>
    <g className="orb-dots orb-dots-inner">{innerDots.map(([cx, cy]) => <circle key={`${cx}-${cy}`} className="orb-dot orb-dot-bright" cx={cx} cy={cy} r="2.8" />)}</g>
    <circle className="orb-signal-halo" cx="64" cy="32" r="6.5" />
    <circle className="orb-signal" cx="64" cy="32" r="3.8" />
  </svg>
}
