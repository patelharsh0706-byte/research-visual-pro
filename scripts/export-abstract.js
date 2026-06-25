#!/usr/bin/env node
/**
 * export-abstract.js
 * ──────────────────
 * Screenshots the graphical-abstract viz panel from a live Research Visual Pro
 * page and saves it as a print-ready PNG (1400 × 840 px @ 2× DPR).
 *
 * Usage:
 *   node export-abstract.js [url] [sectionId] [slug] [outDir]
 *
 * Defaults (drug repurposing paper):
 *   node export-abstract.js
 *
 * Custom paper:
 *   node export-abstract.js \
 *     https://research-visual-pro.vercel.app/kelchtermans-2022-licensing-learning \
 *     summary \
 *     kelchtermans-2022-licensing-learning
 */

import puppeteer from 'puppeteer';
import { mkdirSync } from 'fs';
import { join, resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

const DEFAULTS = {
  url:             'https://research-visual-pro.vercel.app/drug-repurposing-pushpakom-2019',
  sectionId:       'summary',
  slug:            'drug-repurposing-pushpakom-2019',
  outDir:          resolve(__dirname, '../web/public/abstracts'),
  animationWaitMs: 4800,   // D3 animation finishes at ~4s; 800ms buffer
};

export async function exportAbstract(opts = {}) {
  const { url, sectionId, slug, outDir, animationWaitMs } = { ...DEFAULTS, ...opts };

  mkdirSync(outDir, { recursive: true });
  const outPath = join(outDir, `${slug}.png`);

  console.log('[export-abstract] launching headless Chrome…');
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu'],
  });

  try {
    const page = await browser.newPage();

    // 2× DPR: the 700×420 SVG viewBox renders at 1400×840px — crisp for print
    await page.setViewport({ width: 1400, height: 900, deviceScaleFactor: 2 });

    // Load with hash → browser scrolls to section → IntersectionObserver fires
    const pageUrl = `${url}#section-${sectionId}`;
    console.log(`[export-abstract] loading ${pageUrl}`);
    await page.goto(pageUrl, { waitUntil: 'networkidle2', timeout: 30_000 });

    // Ensure the target section is in the viewport so the observer fires
    await page.evaluate((sid) => {
      const el = document.getElementById(`section-${sid}`);
      if (el) el.scrollIntoView({ behavior: 'instant', block: 'center' });
    }, sectionId);

    // Give IntersectionObserver + lazy D3 module import time to fire
    await wait(600);

    // Fallback: if panel still isn't active, force-activate it via JS
    const isActive = await page.evaluate((sid) => {
      const panel = document.getElementById(`viz-${sid}`);
      if (!panel) return false;
      if (!panel.classList.contains('active')) {
        document.querySelectorAll('.viz-panel').forEach(p => p.classList.remove('active', 'exiting'));
        panel.classList.add('active');
      }
      return true;
    }, sectionId);

    if (!isActive) throw new Error(`#viz-${sectionId} not found — check sectionId`);

    // Wait for the full D3 animation to complete
    console.log(`[export-abstract] waiting ${animationWaitMs}ms for animation…`);
    await wait(animationWaitMs);

    // Find the rendered SVG inside the panel
    const svgEl = await page.$(`#viz-${sectionId} svg[viewBox]`);
    if (!svgEl) throw new Error(`SVG not rendered inside #viz-${sectionId}`);

    console.log('[export-abstract] capturing screenshot…');
    await svgEl.screenshot({ path: outPath, type: 'png' });

    console.log(`✓  Saved → ${outPath}`);
    return outPath;

  } finally {
    await browser.close();
  }
}

// ── CLI entry ─────────────────────────────────────────────────────────────────
const [,, url, sectionId, slug, outDir] = process.argv;
const cliOpts = Object.fromEntries(
  Object.entries({ url, sectionId, slug, outDir }).filter(([, v]) => v !== undefined)
);
exportAbstract(cliOpts)
  .catch(err => { console.error('[export-abstract] ERROR:', err.message); process.exit(1); });

function wait(ms) { return new Promise(r => setTimeout(r, ms)); }
