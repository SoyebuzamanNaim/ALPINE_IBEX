/**
 * FLARE-X: NASA Microgravity Fire Intelligence
 * Public Project Page & Live Data Visualization Interactions
 * Clean Laboratory Light Theme Engine & Fully Reactive Demonstration Model
 * NASA Space Apps Challenge 2026
 */

// Global Application State for Reactive Demo
const demoState = {
  material: 'PMMA',
  oxygen: 21.0,
  flow: 5.0,
  pressure: 101.3
};

// Material Physical Specifications & Verified NASA Flight Envelopes
const MATERIAL_SPECS = {
  'PMMA': {
    samples: 92,
    o2Range: [15.5, 34.0],
    flowRange: [0.0, 35.0],
    pRange: [56.5, 101.3],
    loc: 17.5,
    formula: 'C₅H₈O₂ · 1.18 g/cm³',
    desc: 'Thermally thick non-charring acrylic polymer'
  },
  'Cellulose': {
    samples: 22,
    o2Range: [15.5, 34.0],
    flowRange: [0.3, 30.0],
    pRange: [56.5, 101.3],
    loc: 16.0,
    formula: 'C₆H₁₀O₅ · 1.50 g/cm³',
    desc: 'Thermally thin ashless filter paper'
  },
  'Cotton': {
    samples: 19,
    o2Range: [16.2, 20.8],
    flowRange: [0.4, 45.0],
    pRange: [101.3, 101.3],
    loc: 16.5,
    formula: 'Natural fabric · 1.54 g/cm³',
    desc: 'Porous SIBAL woven fabric specimen'
  },
  'Nomex': {
    samples: 7,
    o2Range: [20.8, 34.0],
    flowRange: [5.0, 20.0],
    pRange: [56.5, 101.3],
    loc: 21.0,
    formula: 'Aramid polymer · 1.38 g/cm³',
    desc: 'Flame-resistant synthetic spacecraft fabric'
  },
  'Delrin': {
    samples: 5,
    o2Range: [15.0, 21.0],
    flowRange: [5.0, 10.0],
    pRange: [101.3, 101.3],
    loc: 15.8,
    formula: 'POM · 1.41 g/cm³',
    desc: 'Polyoxymethylene engineering plastic'
  }
};

document.addEventListener('DOMContentLoaded', () => {
  // Mark document as JS-enabled for progressive enhancement
  document.documentElement.classList.add('has-js');

  initTheme();
  initNavigation();
  initScrollReveal();
  initHeroMap();
  initConceptCounterfactual();
  initWorkbench();
  initPresetButtons();
  initModals();

  // Initial coordinated render of reactive demo simulation
  updateDemoSimulation();
});

/* ==============================================================================
   1. THEME ENGINE: DEFAULT LIGHT THEME WITH TOGGLE
   ============================================================================== */
function initTheme() {
  const toggleBtn = document.getElementById('theme-toggle');
  const toggleIcon = document.getElementById('theme-toggle-icon');
  const toggleLabel = document.getElementById('theme-toggle-label');

  const savedTheme = localStorage.getItem('flarex_theme') || 'light';
  applyTheme(savedTheme);

  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      const currentTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
      const newTheme = currentTheme === 'light' ? 'dark' : 'light';
      applyTheme(newTheme);
      localStorage.setItem('flarex_theme', newTheme);
    });
  }

  function applyTheme(theme) {
    if (theme === 'dark') {
      document.documentElement.setAttribute('data-theme', 'dark');
      if (toggleIcon) toggleIcon.textContent = '☀️';
      if (toggleLabel) toggleLabel.textContent = 'Light';
    } else {
      document.documentElement.removeAttribute('data-theme');
      if (toggleIcon) toggleIcon.textContent = '🌙';
      if (toggleLabel) toggleLabel.textContent = 'Dark';
    }
  }
}

/* ==============================================================================
   2. ACCESSIBLE NAVIGATION & MOBILE DRAWER
   ============================================================================== */
function initNavigation() {
  const toggle = document.querySelector('.nav-toggle');
  const nav = document.querySelector('#primary-nav');

  if (!toggle || !nav) return;

  function closeNav() {
    nav.classList.remove('open');
    toggle.setAttribute('aria-expanded', 'false');
  }

  toggle.addEventListener('click', (e) => {
    e.stopPropagation();
    const open = toggle.getAttribute('aria-expanded') === 'true';
    toggle.setAttribute('aria-expanded', String(!open));
    nav.classList.toggle('open', !open);
  });

  nav.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => closeNav());
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && nav.classList.contains('open')) {
      closeNav();
    }
  });

  document.addEventListener('click', (e) => {
    if (nav.classList.contains('open') && !nav.contains(e.target) && e.target !== toggle) {
      closeNav();
    }
  });
}

/* ==============================================================================
   3. SCROLL REVEAL OBSERVER
   ============================================================================== */
function initScrollReveal() {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    document.querySelectorAll('.reveal').forEach(el => el.classList.add('visible'));
    return;
  }

  const io = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.reveal').forEach(el => io.observe(el));
}

/* ==============================================================================
   4. HERO 2D SUPPORT MAP & DIRECT INTERACTION
   ============================================================================== */
function initHeroMap() {
  const svg = document.getElementById('hero-support-svg');
  if (!svg) return;

  const tooltip = document.createElement('div');
  tooltip.className = 'map-tooltip';
  svg.parentElement.appendChild(tooltip);

  const circles = svg.querySelectorAll('.nasa-scatter-group circle');
  circles.forEach(circle => {
    circle.addEventListener('mouseenter', () => {
      const text = circle.getAttribute('data-run') || 'NASA Spaceflight Burn';
      tooltip.textContent = text;
      tooltip.style.display = 'block';
      circle.setAttribute('r', '9');
      circle.style.filter = 'drop-shadow(0 0 6px rgba(37, 99, 235, 0.6))';
    });

    circle.addEventListener('mousemove', (e) => {
      const rect = svg.parentElement.getBoundingClientRect();
      const x = e.clientX - rect.left + 15;
      const y = e.clientY - rect.top - 25;
      tooltip.style.left = `${x}px`;
      tooltip.style.top = `${y}px`;
    });

    circle.addEventListener('mouseleave', () => {
      tooltip.style.display = 'none';
      circle.setAttribute('r', '7');
      circle.style.filter = 'none';
    });

    circle.addEventListener('click', (e) => {
      e.stopPropagation();
      const dataStr = circle.getAttribute('data-run') || '';
      const o2Match = dataStr.match(/([\d\.]+)%\s*O/);
      const flowMatch = dataStr.match(/([\d\.]+)\s*cm\/s/);
      if (o2Match && flowMatch) {
        setDemoConditions('PMMA', parseFloat(o2Match[1]), parseFloat(flowMatch[1]), 101.3);
      }
    });
  });

  // Clicking directly on the Hero Map SVG sets the scenario probe
  svg.style.cursor = 'crosshair';
  svg.addEventListener('click', (e) => {
    const rect = svg.getBoundingClientRect();
    const svgX = ((e.clientX - rect.left) / rect.width) * 720;
    const svgY = ((e.clientY - rect.top) / rect.height) * 500;
    // Map bounds: X: 100 to 630 (Flow 0-40 cm/s), Y: 80 to 410 (O2 34-14%)
    if (svgX >= 100 && svgX <= 630 && svgY >= 80 && svgY <= 410) {
      const flow = Math.max(0.0, Math.min(40.0, 0.0 + ((svgX - 100) / 530) * 40.0));
      const o2 = Math.max(14.0, Math.min(34.0, 14.0 + ((410 - svgY) / 330) * 20.0));
      setDemoConditions(demoState.material, parseFloat(o2.toFixed(1)), parseFloat(flow.toFixed(1)), demoState.pressure);
    }
  });
}

function updateHeroMap(flow, o2, material, inEnvelope, safetyMargin) {
  const marker = document.getElementById('hero-scenario-marker');
  const label = document.getElementById('hero-scenario-label');
  const badge = document.getElementById('hero-domain-badge');

  const heroX = Math.max(100, Math.min(630, 100 + (flow / 40.0) * 530));
  const heroY = Math.max(80, Math.min(410, 410 - ((o2 - 14.0) / 20.0) * 330));

  if (marker) {
    marker.setAttribute('transform', `translate(${heroX.toFixed(1)}, ${heroY.toFixed(1)})`);
  }

  if (label) {
    label.textContent = `YOUR SCENARIO (${material}: ${o2.toFixed(1)}% O₂, ${flow.toFixed(1)} cm/s)`;
    if (heroX > 430) {
      label.setAttribute('x', '-275');
    } else {
      label.setAttribute('x', '26');
    }
  }

  if (badge) {
    if (!inEnvelope) {
      badge.className = 'state outside';
      badge.textContent = '× OUT OF ENVELOPE';
    } else if (Math.abs(safetyMargin) <= 0.8) {
      badge.className = 'state near';
      badge.textContent = '△ NEAR BOUNDARY';
    } else {
      badge.className = 'state inside';
      badge.textContent = '✓ INSIDE DOMAIN';
    }
  }
}

/* ==============================================================================
   5. CONCEPT COUNTERFACTUAL INTERACTIVE SLIDER
   ============================================================================== */
function initConceptCounterfactual() {
  const slider = document.getElementById('concept-o2-slider');
  const stepBtns = document.querySelectorAll('.counter-step-btn');

  if (slider) {
    slider.addEventListener('input', (e) => {
      const o2 = parseFloat(e.target.value);
      setDemoConditions(demoState.material, o2, demoState.flow, demoState.pressure);
    });
  }

  stepBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const val = parseFloat(btn.getAttribute('data-o2'));
      if (!isNaN(val)) {
        setDemoConditions(demoState.material, val, demoState.flow, demoState.pressure);
      }
    });
  });
}

function updateConceptCounterfactual(o2, loc, inEnvelope, safetyMargin) {
  const slider = document.getElementById('concept-o2-slider');
  const readout = document.getElementById('concept-slider-val');
  const badge = document.getElementById('concept-slider-badge');
  const star = document.getElementById('concept-scenario-star');
  const boundaryLine = document.getElementById('concept-boundary-line');
  const boundaryText = document.getElementById('concept-boundary-text');
  const stepBtns = document.querySelectorAll('.counter-step-btn');

  if (slider && Math.abs(parseFloat(slider.value) - o2) > 0.1) {
    slider.value = Math.max(14.0, Math.min(21.0, o2));
  }
  if (readout) readout.textContent = `${o2.toFixed(1)}% O₂`;

  if (badge) {
    if (!inEnvelope) {
      badge.className = 'state outside';
      badge.textContent = '× OUTSIDE (WITHHELD)';
    } else if (Math.abs(safetyMargin) <= 0.8) {
      badge.className = 'state near';
      badge.textContent = '△ NEAR BOUNDARY';
    } else if (safetyMargin > 0.8) {
      badge.className = 'state inside';
      badge.textContent = '✓ INSIDE DOMAIN';
    } else {
      badge.className = 'state near';
      badge.textContent = '△ EXTINCTION DOMAIN';
    }
  }

  if (star) {
    const ratio = Math.max(0, Math.min(1, (o2 - 14.0) / (21.0 - 14.0)));
    const x = 65 + ratio * 475;
    const y = 215 - Math.pow(ratio, 0.75) * 125;
    star.setAttribute('transform', `translate(${x.toFixed(1)}, ${y.toFixed(1)})`);
  }

  if (boundaryLine) {
    const locRatio = Math.max(0, Math.min(1, (loc - 14.0) / (21.0 - 14.0)));
    const locX = 65 + locRatio * 475;
    boundaryLine.setAttribute('x1', locX.toFixed(1));
    boundaryLine.setAttribute('x2', locX.toFixed(1));

    if (boundaryText) {
      boundaryText.setAttribute('x', Math.min(470, locX + 8).toFixed(1));
      boundaryText.textContent = `support boundary (${loc.toFixed(1)}%)`;
    }
  }

  stepBtns.forEach(btn => {
    const btnO2 = parseFloat(btn.getAttribute('data-o2'));
    btn.classList.toggle('active', Math.abs(btnO2 - o2) < 0.8);
  });
}

/* ==============================================================================
   6. FLAGSHIP SCENARIO SYNCHRONIZATION
   ============================================================================== */
function updateWorkflowFlagship(material, o2, flow, pressure, regimeTitle, inEnvelope) {
  const pillMat = document.getElementById('workflow-pill-mat');
  const pillO2 = document.getElementById('workflow-pill-o2');
  const pillFlow = document.getElementById('workflow-pill-flow');
  const pillStatus = document.getElementById('workflow-pill-status');
  const title = document.getElementById('workflow-scenario-title');
  const desc = document.getElementById('workflow-scenario-desc');

  if (pillMat) pillMat.textContent = material;
  if (pillO2) pillO2.textContent = `${o2.toFixed(1)}% O₂`;
  if (pillFlow) pillFlow.textContent = `${flow.toFixed(1)} cm/s`;
  if (pillStatus) {
    pillStatus.textContent = inEnvelope ? regimeTitle.toLowerCase() : 'prediction withheld';
  }
  if (title) {
    title.textContent = `${material} Combustion (${o2.toFixed(1)}% O₂, ${flow.toFixed(1)} cm/s)`;
  }
  if (desc) {
    desc.textContent = inEnvelope
      ? `Simulating ${material} combustion behavior under microgravity forced airflow at ${pressure.toFixed(1)} kPa.`
      : `Operational parameters exceed the verified NASA spaceflight envelope for ${material}. Model inference is actively withheld.`;
  }
}

/* ==============================================================================
   7. LIVE DEMONSTRATION WORKBENCH
   ============================================================================== */
function initWorkbench() {
  const tabBtns = document.querySelectorAll('.workbench-tab-btn');
  const tabPanes = document.querySelectorAll('.workbench-view-pane');

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-selected', 'false');
      });
      tabPanes.forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      btn.setAttribute('aria-selected', 'true');
      const targetId = btn.getAttribute('aria-controls');
      const targetPane = document.getElementById(targetId);
      if (targetPane) targetPane.classList.add('active');
    });
  });

  const fuelSelect = document.getElementById('demo-fuel-select');
  const o2Slider = document.getElementById('demo-o2-slider');
  const flowSlider = document.getElementById('demo-flow-slider');
  const pressureSelect = document.getElementById('demo-pressure-select');

  if (fuelSelect) {
    fuelSelect.addEventListener('change', (e) => {
      demoState.material = e.target.value;
      updateDemoSimulation();
    });
  }

  if (o2Slider) {
    o2Slider.addEventListener('input', (e) => {
      demoState.oxygen = parseFloat(e.target.value);
      updateDemoSimulation();
    });
  }

  if (flowSlider) {
    flowSlider.addEventListener('input', (e) => {
      demoState.flow = parseFloat(e.target.value);
      updateDemoSimulation();
    });
  }

  if (pressureSelect) {
    pressureSelect.addEventListener('change', (e) => {
      demoState.pressure = parseFloat(e.target.value);
      updateDemoSimulation();
    });
  }

  // Click & Drag on 2D Boundary SVG Map
  const boundarySvg = document.getElementById('demo-boundary-svg');
  if (boundarySvg) {
    let isDragging = false;

    function handleSvgClickOrDrag(e) {
      const rect = boundarySvg.getBoundingClientRect();
      const svgX = ((e.clientX - rect.left) / rect.width) * 900;
      const svgY = ((e.clientY - rect.top) / rect.height) * 500;

      if (svgX >= 90 && svgX <= 810 && svgY >= 80 && svgY <= 420) {
        const o2 = 14.0 + ((svgX - 90) / 720) * (34.0 - 14.0);
        const flow = 0.0 + ((420 - svgY) / 340) * (40.0 - 0.0);

        demoState.oxygen = Math.max(14.0, Math.min(34.0, parseFloat(o2.toFixed(1))));
        demoState.flow = Math.max(0.0, Math.min(40.0, parseFloat(flow.toFixed(1))));

        if (o2Slider) o2Slider.value = demoState.oxygen;
        if (flowSlider) flowSlider.value = demoState.flow;

        updateDemoSimulation();
      }
    }

    boundarySvg.addEventListener('mousedown', (e) => {
      isDragging = true;
      handleSvgClickOrDrag(e);
    });

    window.addEventListener('mousemove', (e) => {
      if (isDragging) handleSvgClickOrDrag(e);
    });

    window.addEventListener('mouseup', () => {
      isDragging = false;
    });
  }

  // Sweep View Simulator (Tab 2)
  const sweepSlider = document.getElementById('workbench-sweep-slider');
  const sweepPresets = document.querySelectorAll('.sweep-preset-btn');

  if (sweepSlider) {
    sweepSlider.addEventListener('input', (e) => {
      const o2 = parseFloat(e.target.value);
      demoState.oxygen = o2;
      if (o2Slider) o2Slider.value = o2;
      updateDemoSimulation();
    });
  }

  sweepPresets.forEach(btn => {
    btn.addEventListener('click', () => {
      const val = parseFloat(btn.getAttribute('data-val'));
      if (!isNaN(val)) {
        demoState.oxygen = val;
        if (o2Slider) o2Slider.value = val;
        if (sweepSlider) sweepSlider.value = val;
        updateDemoSimulation();
      }
    });
  });

  initArchiveTable();
}

/* ==============================================================================
   8. QUICK SCENARIO PRESET BUTTONS
   ============================================================================== */
function initPresetButtons() {
  const chips = document.querySelectorAll('.demo-preset-chip');
  const presets = {
    'iss': { mat: 'PMMA', o2: 21.0, flow: 5.0, p: 101.3 },
    'exploration': { mat: 'PMMA', o2: 18.5, flow: 5.0, p: 56.5 },
    'loc': { mat: 'PMMA', o2: 17.5, flow: 5.0, p: 101.3 },
    'extinction': { mat: 'PMMA', o2: 16.0, flow: 5.0, p: 101.3 },
    'withheld': { mat: 'PMMA', o2: 13.5, flow: 5.0, p: 101.3 },
    'cellulose': { mat: 'Cellulose', o2: 16.5, flow: 5.0, p: 101.3 },
    'nomex': { mat: 'Nomex', o2: 22.0, flow: 10.0, p: 101.3 }
  };

  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      const key = chip.getAttribute('data-preset');
      const p = presets[key];
      if (p) {
        setDemoConditions(p.mat, p.o2, p.flow, p.p);
      }
    });
  });
}

function syncPresetChips(material, oxygen) {
  const chips = document.querySelectorAll('.demo-preset-chip');
  chips.forEach(chip => {
    const key = chip.getAttribute('data-preset');
    let active = false;
    if (key === 'iss' && material === 'PMMA' && Math.abs(oxygen - 21.0) < 0.2) active = true;
    else if (key === 'exploration' && material === 'PMMA' && Math.abs(oxygen - 18.5) < 0.2) active = true;
    else if (key === 'loc' && material === 'PMMA' && Math.abs(oxygen - 17.5) < 0.2) active = true;
    else if (key === 'extinction' && material === 'PMMA' && Math.abs(oxygen - 16.0) < 0.2) active = true;
    else if (key === 'withheld' && material === 'PMMA' && oxygen < 15.0) active = true;
    else if (key === 'cellulose' && material === 'Cellulose') active = true;
    else if (key === 'nomex' && material === 'Nomex') active = true;

    chip.classList.toggle('active', active);
  });
}

/* ==============================================================================
   9. CORE REACTIVE SIMULATION ENGINE (FULL MULTI-COMPONENT COORDINATION)
   ============================================================================== */
function updateDemoSimulation() {
  const spec = MATERIAL_SPECS[demoState.material] || MATERIAL_SPECS['PMMA'];
  const loc = spec.loc;
  const o2 = demoState.oxygen;
  const flow = demoState.flow;
  const pressure = demoState.pressure;

  // 1. Update Input Form Readouts
  const fuelCountEl = document.getElementById('demo-fuel-count');
  if (fuelCountEl) fuelCountEl.textContent = `${spec.samples} Flight Runs`;

  const o2ValEl = document.getElementById('demo-o2-val');
  if (o2ValEl) o2ValEl.textContent = `${o2.toFixed(1)}% O₂`;

  const flowValEl = document.getElementById('demo-flow-val');
  if (flowValEl) flowValEl.textContent = `${flow.toFixed(1)} cm/s`;

  const pValEl = document.getElementById('demo-p-val');
  if (pValEl) pValEl.textContent = `${pressure.toFixed(1)} kPa`;

  const svgTitleEl = document.getElementById('demo-svg-title');
  if (svgTitleEl) {
    svgTitleEl.textContent = `2-D FLAMMABILITY BOUNDARY SLICE · ${demoState.material.toUpperCase()} AT ${pressure.toFixed(1)} kPa`;
  }

  // 2. Convert (O2, Flow) into SVG Coordinates (Plot: X: 90 to 810, Y: 420 to 80)
  const probeSvgX = Math.max(90, Math.min(810, 90 + ((o2 - 14.0) / 20.0) * 720));
  const probeSvgY = Math.max(80, Math.min(420, 420 - (flow / 40.0) * 340));

  const probeMarker = document.getElementById('demo-probe-marker');
  if (probeMarker) {
    probeMarker.setAttribute('transform', `translate(${probeSvgX.toFixed(1)}, ${probeSvgY.toFixed(1)})`);
  }

  const probeLabel = document.getElementById('demo-probe-label');
  if (probeLabel) {
    probeLabel.textContent = `PROBE: ${o2.toFixed(1)}% O₂, ${flow.toFixed(1)} cm/s`;
    if (probeSvgX > 680) {
      probeLabel.setAttribute('x', '-160');
    } else {
      probeLabel.setAttribute('x', '14');
    }
  }

  // 3. Dynamic LOC Boundary Adjustment on SVG Map
  const locSvgX = 90 + ((loc - 14.0) / 20.0) * 720;
  const locLine = document.getElementById('demo-loc-line');
  const locBox = document.getElementById('demo-loc-box');
  const locText = document.getElementById('demo-loc-text');

  if (locLine) {
    locLine.setAttribute('x1', locSvgX.toFixed(1));
    locLine.setAttribute('x2', locSvgX.toFixed(1));
  }
  if (locBox) locBox.setAttribute('x', (locSvgX - 55).toFixed(1));
  if (locText) {
    locText.setAttribute('x', locSvgX.toFixed(1));
    locText.textContent = `LOC ≈ ${loc.toFixed(1)}% O₂`;
  }

  // Adjust Physical Zone Widths for Active Material's Limits
  const refusalZone = document.getElementById('demo-zone-refusal');
  const extinctionZone = document.getElementById('demo-zone-extinction');
  const marginalZone = document.getElementById('demo-zone-marginal');
  const spreadZone = document.getElementById('demo-zone-spread');

  const minO2 = spec.o2Range[0];
  const refusalWidth = Math.max(40, ((minO2 - 14.0) / 20.0) * 720);
  if (refusalZone) refusalZone.setAttribute('width', refusalWidth.toFixed(1));

  const extinctionWidth = Math.max(40, locSvgX - (90 + refusalWidth));
  if (extinctionZone) {
    extinctionZone.setAttribute('x', (90 + refusalWidth).toFixed(1));
    extinctionZone.setAttribute('width', extinctionWidth.toFixed(1));
  }

  if (marginalZone) {
    marginalZone.setAttribute('x', locSvgX.toFixed(1));
    marginalZone.setAttribute('width', '50');
  }

  if (spreadZone) {
    spreadZone.setAttribute('x', (locSvgX + 50).toFixed(1));
    spreadZone.setAttribute('width', Math.max(40, 810 - (locSvgX + 50)).toFixed(1));
  }

  // 4. Section 7 Envelope Guard & Flammability Inference
  const inO2 = o2 >= spec.o2Range[0] && o2 <= spec.o2Range[1];
  const inFlow = flow >= spec.flowRange[0] && flow <= spec.flowRange[1];
  const inP = pressure >= spec.pRange[0] && pressure <= spec.pRange[1];
  const inEnvelope = inO2 && inFlow && inP;

  const safetyMargin = o2 - loc;

  // Telemetry HUD Elements
  const hudFuel = document.getElementById('demo-hud-fuel');
  if (hudFuel) hudFuel.textContent = `${demoState.material}`;

  const hudSpecs = document.getElementById('demo-hud-fuel-specs');
  if (hudSpecs) hudSpecs.textContent = `${spec.desc} (${spec.formula})`;

  const hudAtmos = document.getElementById('demo-hud-atmos');
  if (hudAtmos) hudAtmos.textContent = `${o2.toFixed(1)}% O₂ · ${pressure.toFixed(1)} kPa`;

  const hudFlow = document.getElementById('demo-hud-flow');
  if (hudFlow) hudFlow.textContent = `${flow.toFixed(1)} cm/s (Forced)`;

  const hudLoc = document.getElementById('demo-hud-loc');
  if (hudLoc) hudLoc.textContent = `${loc.toFixed(1)}% O₂`;

  const hudMargin = document.getElementById('demo-hud-margin');
  if (hudMargin) {
    if (safetyMargin >= 0) {
      hudMargin.textContent = `+${safetyMargin.toFixed(1)}% O₂`;
      hudMargin.style.color = 'var(--green)';
    } else {
      hudMargin.textContent = `${safetyMargin.toFixed(1)}% O₂`;
      hudMargin.style.color = 'var(--red)';
    }
  }

  const hudGuard = document.getElementById('demo-hud-guard');
  if (hudGuard) {
    if (inEnvelope) {
      if (Math.abs(safetyMargin) <= 0.8) {
        hudGuard.className = 'state near';
        hudGuard.textContent = '△ NEAR BOUNDARY';
      } else {
        hudGuard.className = 'state inside';
        hudGuard.textContent = '✓ IN TRAINING DOMAIN';
      }
    } else {
      hudGuard.className = 'state outside';
      hudGuard.textContent = '× OUT OF ENVELOPE (REFUSAL)';
    }
  }

  // 5. Scientific Regime Inference & Probabilities
  let pSpread = 0, pMarginal = 0, pExtinction = 0;
  let regimeTitle = '', regimeColor = '', regimeDesc = '', regimeKey = '';

  if (!inEnvelope) {
    regimeKey = 'refusal';
    regimeTitle = 'PREDICTION WITHHELD (OUT OF DOMAIN)';
    regimeColor = 'var(--red)';
    pSpread = 0; pMarginal = 0; pExtinction = 0;
    regimeDesc = `Operational conditions exceed the tested NASA spaceflight envelope for ${demoState.material} (Oxygen: ${spec.o2Range[0]}–${spec.o2Range[1]}%, Flow: ${spec.flowRange[0]}–${spec.flowRange[1]} cm/s). Under the Section 7 Zero-Extrapolation Guard, the model abstains to prevent safety-critical hallucination.`;
  } else if (safetyMargin >= 1.0) {
    regimeKey = 'spread';
    const spreadFactor = Math.min(0.98, 0.75 + (safetyMargin / 15.0) * 0.23);
    pSpread = spreadFactor * 100;
    pMarginal = (1 - spreadFactor) * 75;
    pExtinction = 100 - pSpread - pMarginal;
    regimeTitle = 'SUSTAINED FLAME PROPAGATION';
    regimeColor = 'var(--red)';
    regimeDesc = `Opposed-flow flame propagation is sustained. Continuous solid fuel pyrolysis supplies combustible vapor to a luminous reaction zone with a positive flammability margin (+${safetyMargin.toFixed(1)}% O₂ above LOC).`;
  } else if (safetyMargin <= -0.8) {
    regimeKey = 'no_spread';
    const extFactor = Math.min(0.99, 0.75 + (Math.abs(safetyMargin) / 5.0) * 0.24);
    pExtinction = extFactor * 100;
    pMarginal = (1 - extFactor) * 80;
    pSpread = 100 - pExtinction - pMarginal;
    regimeTitle = 'EXTINCTION / NO SPREAD';
    regimeColor = 'var(--green)';
    regimeDesc = `Radiative and convective heat loss exceeds chemical heat release. The oxidizer flux (${o2.toFixed(1)}% O₂) is below the Limiting Oxygen Concentration (${loc.toFixed(1)}% O₂), causing prompt flame quenching.`;
  } else {
    regimeKey = 'marginal';
    pMarginal = 63.5;
    pSpread = Math.max(10, 24.0 + (safetyMargin * 12));
    pExtinction = Math.max(10, 100 - pMarginal - pSpread);
    regimeTitle = 'MARGINAL FLAME SPREAD';
    regimeColor = 'var(--amber)';
    regimeDesc = `Operation near the flammability threshold. Flame exists as a weak, non-luminous blue hemispherical cap hovering close to the surface with intermittent or creeping propagation.`;
  }

  // Update Inferred Regime Title & Description
  const titleEl = document.getElementById('demo-regime-title');
  if (titleEl) {
    titleEl.textContent = regimeTitle;
    titleEl.style.color = regimeColor;
  }

  const descEl = document.getElementById('demo-regime-desc');
  if (descEl) descEl.textContent = regimeDesc;

  // Update Probability Progress Bars
  const spreadBar = document.getElementById('demo-prob-spread-bar');
  const spreadPct = document.getElementById('demo-prob-spread-pct');
  if (spreadBar && spreadPct) {
    spreadBar.style.width = `${pSpread.toFixed(1)}%`;
    spreadPct.textContent = `${pSpread.toFixed(1)}%`;
  }

  const marginalBar = document.getElementById('demo-prob-marginal-bar');
  const marginalPct = document.getElementById('demo-prob-marginal-pct');
  if (marginalBar && marginalPct) {
    marginalBar.style.width = `${pMarginal.toFixed(1)}%`;
    marginalPct.textContent = `${pMarginal.toFixed(1)}%`;
  }

  const extBar = document.getElementById('demo-prob-extinction-bar');
  const extPct = document.getElementById('demo-prob-extinction-pct');
  if (extBar && extPct) {
    extBar.style.width = `${pExtinction.toFixed(1)}%`;
    extPct.textContent = `${pExtinction.toFixed(1)}%`;
  }

  // 6. Coordinate Across ALL Other Sections of the Page!
  updateHeroMap(flow, o2, demoState.material, inEnvelope, safetyMargin);
  updateWorkflowFlagship(demoState.material, o2, flow, pressure, regimeTitle, inEnvelope);
  updateConceptCounterfactual(o2, loc, inEnvelope, safetyMargin);
  updateModelCardChip(demoState.material, o2, regimeTitle, pSpread, inEnvelope);
  updateConfusionMatrix(regimeKey, inEnvelope);
  synchronizeSweepView(o2, loc, safetyMargin, demoState.material, flow, pressure);
  syncPresetChips(demoState.material, o2);

  // 7. Dynamically Render Filtered NASA Scatter Circles on SVG
  renderDynamicScatterPoints();
}

/* ==============================================================================
   10. MODEL GOVERNANCE CONFUSION MATRIX & MODEL CARD CHIP
   ============================================================================== */
function updateConfusionMatrix(regimeKey, inEnvelope) {
  const rowSpread = document.getElementById('cm-row-spread');
  const rowMarginal = document.getElementById('cm-row-marginal-spread');
  const rowNoSpread = document.getElementById('cm-row-no-spread');
  const banner = document.getElementById('cm-active-banner');

  [rowSpread, rowMarginal, rowNoSpread].forEach(row => {
    if (row) {
      row.classList.remove('active-regime-row');
      const badge = row.querySelector('.active-regime-badge');
      if (badge) badge.remove();
    }
  });

  if (!inEnvelope) {
    if (banner) {
      banner.style.background = 'var(--red-subtle)';
      banner.style.color = 'var(--red)';
      banner.style.borderColor = 'var(--red-border)';
      banner.textContent = '⚠ SECTION 7 ENVELOPE GUARD TRIGGERED: PREDICTION WITHHELD · ZERO EXTRAPOLATION ENFORCED';
    }
    return;
  }

  let activeRow = null;
  let text = '';
  let bg = '';
  let color = '';
  let border = '';

  if (regimeKey === 'spread') {
    activeRow = rowSpread;
    text = 'ACTIVE PREDICTION: SUSTAINED SPREAD (89.3% Recall Hit Rate)';
    bg = 'var(--blue-subtle)';
    color = 'var(--blue)';
    border = 'var(--blue-border)';
  } else if (regimeKey === 'marginal') {
    activeRow = rowMarginal;
    text = 'ACTIVE PREDICTION: MARGINAL FLAME SPREAD (52.4% Recall Hit Rate)';
    bg = 'var(--amber-subtle)';
    color = 'var(--amber)';
    border = 'var(--amber-border)';
  } else {
    activeRow = rowNoSpread;
    text = 'ACTIVE PREDICTION: EXTINCTION / NO SPREAD (75.5% Recall Hit Rate)';
    bg = 'var(--green-subtle)';
    color = 'var(--green)';
    border = 'var(--green-border)';
  }

  if (activeRow) {
    activeRow.classList.add('active-regime-row');
    const recallCell = activeRow.cells[activeRow.cells.length - 1];
    if (recallCell && !recallCell.querySelector('.active-regime-badge')) {
      const b = document.createElement('span');
      b.className = 'active-regime-badge';
      b.textContent = 'ACTIVE';
      recallCell.appendChild(b);
    }
  }

  if (banner) {
    banner.style.background = bg;
    banner.style.color = color;
    banner.style.borderColor = border;
    banner.textContent = text;
  }
}

function updateModelCardChip(material, o2, regimeTitle, pSpread, inEnvelope) {
  const textEl = document.getElementById('model-card-live-text');
  if (textEl) {
    if (!inEnvelope) {
      textEl.textContent = `LIVE STATUS: ${material} @ ${o2.toFixed(1)}% O₂ → PREDICTION WITHHELD (OUT OF DOMAIN)`;
    } else {
      textEl.textContent = `LIVE INFERENCE: ${material} @ ${o2.toFixed(1)}% O₂ → ${regimeTitle.toUpperCase()} (${pSpread.toFixed(1)}%)`;
    }
  }
}

/* ==============================================================================
   11. DYNAMIC NASA SCATTER POINTS & ARCHIVE HIGHLIGHTING
   ============================================================================== */
function renderDynamicScatterPoints() {
  const container = document.getElementById('demo-dynamic-scatter-group');
  const nearestLine = document.getElementById('demo-nearest-line');
  const nearestList = document.getElementById('demo-nearest-burns-list');
  const archiveActiveFuel = document.getElementById('archive-active-fuel');
  const archiveNearestId = document.getElementById('archive-nearest-id');

  if (!container) return;
  container.innerHTML = '';

  const experiments = window.FLAREX_EXPERIMENTS || [];
  const materialBurns = experiments.filter(e => e.mat === demoState.material);

  if (materialBurns.length === 0) return;

  // Calculate Euclidean distances to find closest 3
  const scored = materialBurns.map(exp => {
    const dO2 = exp.o2 - demoState.oxygen;
    const dFlow = exp.flow - demoState.flow;
    const dist = Math.sqrt(dO2 * dO2 + dFlow * dFlow);
    return { ...exp, dist };
  }).sort((a, b) => a.dist - b.dist);

  const closest = scored[0];

  // Tooltip for SVG points
  let svgTooltip = document.getElementById('demo-svg-tooltip');
  if (!svgTooltip) {
    svgTooltip = document.createElement('div');
    svgTooltip.id = 'demo-svg-tooltip';
    svgTooltip.className = 'map-tooltip';
    const wrap = container.closest('.demo-canvas-wrap');
    if (wrap) wrap.appendChild(svgTooltip);
  }

  // Render scatter points
  scored.forEach((exp, idx) => {
    const cx = Math.max(90, Math.min(810, 90 + ((exp.o2 - 14.0) / 20.0) * 720));
    const cy = Math.max(80, Math.min(420, 420 - (exp.flow / 40.0) * 340));

    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    circle.setAttribute('cx', cx.toFixed(1));
    circle.setAttribute('cy', cy.toFixed(1));
    circle.setAttribute('r', idx === 0 ? '8' : '5.5');

    let fill = '#1d4ed8';
    if (exp.out === 'spread') fill = '#dc2626';
    else if (exp.out === 'marginal_spread') fill = '#d97706';
    else if (exp.out === 'no_spread') fill = '#059669';

    circle.setAttribute('fill', fill);
    circle.setAttribute('stroke', idx === 0 ? '#0284c7' : '#ffffff');
    circle.setAttribute('stroke-width', idx === 0 ? '3.5' : '1.5');
    circle.style.cursor = 'pointer';

    circle.addEventListener('click', (e) => {
      e.stopPropagation();
      setDemoConditions(exp.mat, exp.o2, exp.flow, exp.p);
    });

    circle.addEventListener('mouseenter', () => {
      circle.setAttribute('r', '10');
      if (svgTooltip) {
        svgTooltip.textContent = `${exp.id} (${exp.inv})\n${exp.mat} · ${exp.o2.toFixed(1)}% O₂ · ${exp.flow.toFixed(1)} cm/s\nOutcome: ${exp.out.replace('_', ' ').toUpperCase()}`;
        svgTooltip.style.display = 'block';
      }
    });

    circle.addEventListener('mousemove', (e) => {
      if (svgTooltip) {
        const wrap = container.closest('.demo-canvas-wrap');
        if (wrap) {
          const rect = wrap.getBoundingClientRect();
          svgTooltip.style.left = `${e.clientX - rect.left + 15}px`;
          svgTooltip.style.top = `${e.clientY - rect.top - 20}px`;
        }
      }
    });

    circle.addEventListener('mouseleave', () => {
      circle.setAttribute('r', idx === 0 ? '8' : '5.5');
      if (svgTooltip) svgTooltip.style.display = 'none';
    });

    container.appendChild(circle);
  });

  // Connect nearest flight run with dashed line
  if (nearestLine && closest) {
    const probeSvgX = Math.max(90, Math.min(810, 90 + ((demoState.oxygen - 14.0) / 20.0) * 720));
    const probeSvgY = Math.max(80, Math.min(420, 420 - (demoState.flow / 40.0) * 340));
    const closestSvgX = Math.max(90, Math.min(810, 90 + ((closest.o2 - 14.0) / 20.0) * 720));
    const closestSvgY = Math.max(80, Math.min(420, 420 - (closest.flow / 40.0) * 340));

    nearestLine.setAttribute('x1', probeSvgX.toFixed(1));
    nearestLine.setAttribute('y1', probeSvgY.toFixed(1));
    nearestLine.setAttribute('x2', closestSvgX.toFixed(1));
    nearestLine.setAttribute('y2', closestSvgY.toFixed(1));
  }

  // Populate Top 3 Nearest Runs in Sidebar
  if (nearestList) {
    nearestList.innerHTML = '';
    scored.slice(0, 3).forEach(b => {
      const item = document.createElement('div');
      item.className = 'nearest-burn-item';
      const outLabel = b.out.replace('_', ' ').toUpperCase();

      item.innerHTML = `
        <div>
          <strong>${b.id}</strong> (${b.inv})
          <div class="burn-meta">${b.o2.toFixed(1)}% O₂ · ${b.flow.toFixed(1)} cm/s · ${b.p.toFixed(1)} kPa</div>
        </div>
        <span class="badge-outcome ${b.out === 'spread' ? 'badge-spread' : (b.out === 'marginal_spread' ? 'badge-marginal' : 'badge-no-spread')}">
          ${outLabel}
        </span>
      `;

      item.addEventListener('click', () => {
        setDemoConditions(b.mat, b.o2, b.flow, b.p);
      });

      nearestList.appendChild(item);
    });
  }

  // Synchronize Tab 3 Spaceflight Archive Status Bar & Highlight Row
  if (archiveActiveFuel) archiveActiveFuel.textContent = demoState.material;
  if (archiveNearestId && closest) {
    archiveNearestId.textContent = `${closest.id} (${closest.mat} @ ${closest.o2.toFixed(1)}% O₂)`;
  }

  // Highlight closest row in Archive table
  const tbody = document.getElementById('archive-table-body');
  if (tbody && closest) {
    const rows = tbody.querySelectorAll('tr');
    rows.forEach(row => {
      const idCell = row.cells[0];
      if (idCell && idCell.textContent.trim() === closest.id) {
        row.classList.add('active-flight-row');
      } else {
        row.classList.remove('active-flight-row');
      }
    });
  }
}

/* ==============================================================================
   12. SYNCHRONIZE SWEEP VIEW (TAB 2)
   ============================================================================== */
function synchronizeSweepView(o2, loc, safetyMargin, material, flow, pressure) {
  const sweepSub = document.getElementById('demo-sweep-sub');
  const sweepReadout = document.getElementById('sweep-readout-val');
  const sweepStatus = document.getElementById('sweep-readout-status');
  const sweepIndicator = document.getElementById('svg-sweep-indicator');
  const sweepSafetyLabel = document.getElementById('svg-sweep-safety-label');
  const sweepBracketLine = document.getElementById('sweep-safety-bracket-line');
  const sweepArrowLeft = document.getElementById('sweep-safety-arrow-left');
  const sweepArrowRight = document.getElementById('sweep-safety-arrow-right');
  const sweepLabelBox = document.getElementById('sweep-safety-label-box');
  const sweepLocLine = document.getElementById('sweep-loc-line');
  const sweepLocBox = document.getElementById('sweep-loc-box');
  const sweepLocText = document.getElementById('sweep-loc-text');
  const sweepSlider = document.getElementById('workbench-sweep-slider');

  if (sweepSub) {
    sweepSub.textContent = `${material} AT ${pressure.toFixed(1)} kPa · ${flow.toFixed(1)} cm/s VENTILATION · ${o2.toFixed(1)}% O₂ PROBE`;
  }

  if (sweepSlider && Math.abs(parseFloat(sweepSlider.value) - o2) > 0.1) {
    sweepSlider.value = o2;
  }

  if (sweepReadout) sweepReadout.textContent = `${o2.toFixed(1)}% O₂`;

  // Scale on Sweep SVG: 14.0% = 80px, 21.0% = 820px. 740px width for 7% range
  const locRatio = Math.max(0, Math.min(1, (loc - 14.0) / (21.0 - 14.0)));
  const locX = 80 + locRatio * 740;

  if (sweepLocLine) {
    sweepLocLine.setAttribute('x1', locX.toFixed(1));
    sweepLocLine.setAttribute('x2', locX.toFixed(1));
  }
  if (sweepLocBox) sweepLocBox.setAttribute('x', (locX - 60).toFixed(1));
  if (sweepLocText) {
    sweepLocText.setAttribute('x', locX.toFixed(1));
    sweepLocText.textContent = `LOC: ${loc.toFixed(1)}% O₂`;
  }

  const probeRatio = Math.max(0, Math.min(1, (o2 - 14.0) / (21.0 - 14.0)));
  const probeX = 80 + probeRatio * 740;

  if (sweepIndicator) {
    sweepIndicator.setAttribute('transform', `translate(${probeX.toFixed(1)}, 0)`);
  }

  // Safety Margin bracket between LOC and Probe
  const xMin = Math.min(locX, probeX);
  const xMax = Math.max(locX, probeX);
  const width = Math.max(12, xMax - xMin);

  if (sweepBracketLine) {
    sweepBracketLine.setAttribute('x1', xMin.toFixed(1));
    sweepBracketLine.setAttribute('x2', xMax.toFixed(1));
  }
  if (sweepArrowLeft) {
    sweepArrowLeft.setAttribute('points', `${xMin},206 ${xMin - 8},210 ${xMin},214`);
  }
  if (sweepArrowRight) {
    sweepArrowRight.setAttribute('points', `${xMax},206 ${xMax + 8},210 ${xMax},214`);
  }
  if (sweepLabelBox) {
    sweepLabelBox.setAttribute('x', (xMin + (width - 160) / 2).toFixed(1));
  }

  if (sweepSafetyLabel) {
    sweepSafetyLabel.setAttribute('x', (xMin + width / 2).toFixed(1));
    if (safetyMargin >= 0) {
      sweepSafetyLabel.textContent = `SAFETY MARGIN: +${safetyMargin.toFixed(1)}% O₂`;
      sweepSafetyLabel.setAttribute('fill', '#1d4ed8');
    } else {
      sweepSafetyLabel.textContent = `BELOW LOC: ${safetyMargin.toFixed(1)}% O₂`;
      sweepSafetyLabel.setAttribute('fill', '#d97706');
    }
  }

  if (sweepStatus) {
    if (safetyMargin > 0.5) {
      sweepStatus.className = 'state inside';
      sweepStatus.textContent = `✓ INSIDE DOMAIN (+${safetyMargin.toFixed(1)}% MARGIN)`;
    } else if (Math.abs(safetyMargin) <= 0.5) {
      sweepStatus.className = 'state near';
      sweepStatus.textContent = `△ LOC BOUNDARY (${safetyMargin.toFixed(1)}% MARGIN)`;
    } else if (o2 >= 15.5) {
      sweepStatus.className = 'state near';
      sweepStatus.textContent = `△ EXTINCTION REGIME (${safetyMargin.toFixed(1)}% MARGIN)`;
    } else {
      sweepStatus.className = 'state outside';
      sweepStatus.textContent = '× OUT OF ENVELOPE (PREDICTION REFUSED)';
    }
  }
}

/* ==============================================================================
   13. ONE-CLICK SETTER FOR ANY EXPERIMENTAL DEMO CONDITIONS
   ============================================================================== */
function setDemoConditions(material, oxygen, flow, pressure) {
  demoState.material = material;
  demoState.oxygen = oxygen;
  demoState.flow = flow;
  demoState.pressure = pressure;

  const fuelSelect = document.getElementById('demo-fuel-select');
  const o2Slider = document.getElementById('demo-o2-slider');
  const flowSlider = document.getElementById('demo-flow-slider');
  const pressureSelect = document.getElementById('demo-pressure-select');

  if (fuelSelect) fuelSelect.value = material;
  if (o2Slider) o2Slider.value = oxygen;
  if (flowSlider) flowSlider.value = flow;
  if (pressureSelect) pressureSelect.value = pressure.toFixed(1);

  updateDemoSimulation();
}

/* ==============================================================================
   14. SPACEFLIGHT ARCHIVE TABLE (145 VERIFIED RUNS)
   ============================================================================== */
function initArchiveTable() {
  const tbody = document.getElementById('archive-table-body');
  const searchInput = document.getElementById('archive-search-box');
  const matFilter = document.getElementById('archive-filter-mat');
  const outFilter = document.getElementById('archive-filter-out');
  const countLabel = document.getElementById('archive-count-label');

  if (!tbody) return;

  const experiments = window.FLAREX_EXPERIMENTS || [];

  function renderRows(items) {
    tbody.innerHTML = '';
    if (countLabel) countLabel.textContent = `Showing ${items.length} of ${experiments.length} runs`;

    if (items.length === 0) {
      tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: var(--text-muted); padding: 24px;">No spaceflight experiments matched the active filters.</td></tr>';
      return;
    }

    items.slice(0, 100).forEach(exp => {
      const tr = document.createElement('tr');
      const badgeClass = exp.out === 'spread' ? 'badge-spread' : (exp.out === 'marginal_spread' ? 'badge-marginal' : 'badge-no-spread');
      const outcomeLabel = exp.out.replace('_', ' ');

      tr.innerHTML = `
        <td><strong style="font-family: var(--font-mono); color: var(--blue);">${exp.id}</strong></td>
        <td>${exp.inv}</td>
        <td><strong>${exp.mat}</strong></td>
        <td>${exp.o2.toFixed(1)}%</td>
        <td>${exp.p.toFixed(1)} kPa</td>
        <td>${exp.flow.toFixed(1)} cm/s</td>
        <td><span class="badge-outcome ${badgeClass}">${outcomeLabel}</span></td>
        <td><a href="${exp.url}" target="_blank" rel="noopener noreferrer" style="color: var(--blue); font-family: var(--font-mono); font-size: 11.5px;">NTRS ↗</a></td>
      `;

      tr.addEventListener('click', (e) => {
        if (e.target.closest('a')) return;
        setDemoConditions(exp.mat, exp.o2, exp.flow, exp.p);
      });

      tbody.appendChild(tr);
    });
  }

  function applyFilters() {
    const q = (searchInput ? searchInput.value : '').toLowerCase().trim();
    const mat = matFilter ? matFilter.value : '';
    const out = outFilter ? outFilter.value : '';

    const filtered = experiments.filter(item => {
      const matchQ = !q || JSON.stringify(item).toLowerCase().includes(q);
      const matchMat = !mat || item.mat === mat;
      const matchOut = !out || item.out === out;
      return matchQ && matchMat && matchOut;
    });

    renderRows(filtered);
  }

  if (searchInput) searchInput.addEventListener('input', applyFilters);
  if (matFilter) matFilter.addEventListener('change', applyFilters);
  if (outFilter) outFilter.addEventListener('change', applyFilters);

  renderRows(experiments);
}

/* ==============================================================================
   15. ACCESSIBLE MODAL DIALOGS
   ============================================================================== */
function initModals() {
  const triggers = document.querySelectorAll('.modal-trigger');
  triggers.forEach(trig => {
    trig.addEventListener('click', (e) => {
      e.preventDefault();
      const modalId = trig.getAttribute('data-modal');
      const modal = document.getElementById(modalId);
      if (modal && typeof modal.showModal === 'function') {
        modal.showModal();
      }
    });
  });

  const closeBtns = document.querySelectorAll('.modal-close-btn');
  closeBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const modalId = btn.getAttribute('data-close-modal');
      const modal = document.getElementById(modalId);
      if (modal && typeof modal.close === 'function') {
        modal.close();
      }
    });
  });

  document.querySelectorAll('dialog.flarex-modal').forEach(dialog => {
    dialog.addEventListener('click', (e) => {
      const rect = dialog.getBoundingClientRect();
      const isInDialog = (
        rect.top <= e.clientY && e.clientY <= rect.top + rect.height &&
        rect.left <= e.clientX && e.clientX <= rect.left + rect.width
      );
      if (!isInDialog) {
        dialog.close();
      }
    });
  });
}
