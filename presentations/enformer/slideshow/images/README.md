# Paper figure crops for Slidev

Source PDF (same course folder): `../s41592-021-01252-x.pdf` (Avsec et al., 2021, *Nature Methods*).

**Note:** The repo ships **tiny 1×1 placeholder PNGs** with the expected filenames so `npm run build` succeeds before you add real crops. **Replace each file** with your exported figure (same filename).

Export PNGs into this directory (`slideshow/images/`) using Preview, Adobe Acrobat, or `pdftoppm` / `pdfimages`. Recommended width **1200–1600 px** for legibility on slide export.

Filenames expected by `slides.md`:

| File | Paper figure | What to crop | PDF page (approx.) |
|------|--------------|--------------|-------------------|
| `fig_1b.png` | Fig. 1b | Both scatter panels (Across genes / Across CAGE experiments) with corner means visible (Enformer vs Basenji2). | p. 2–3 |
| `fig_1c.png` | Fig. 1c | All four assay-type columns (CAGE, ChIP histone, ChIP TF, DNase/ATAC) with x-axis Pearson labels. | p. 3 |
| `fig_2a.png` | Fig. 2a | HNRNPA1 locus strip: CAGE, H3K27ac, enhancers, attention, Enformer vs Basenji2 gradient×input. | p. 4 |
| `fig_2b.png` | Fig. 2b | auPRC bar panels for Gasperini and Fulco datasets (Enformer vs Basenji2 vs random / ABC variants). | p. 4 |
| `fig_2c.png` | Fig. 2c | Average attention-matrix difference heatmap (TAD boundary centering — red stripe / blue off-diagonal). | p. 4 |
| `fig_3d.png` | Fig. 3d | GTEx fine-mapped variant classification scatter (Enformer auROC vs Basenji2 auROC, 48 tissues, means in corners). | p. 5–6 |
| `fig_3e.png` | Fig. 3e | Four distance-bin violin plots (variant–TSS distance) if space; else crop bottom row only. | p. 6 |
| `fig_4a.png` | Fig. 4a | Horizontal bar chart: correlation by locus (methods above/below break). | p. 7 |
| `fig_4b.png` | Fig. 4b | Scatter: Enformer vs CAGI5 Group 3 per locus with corner means. | p. 7 |
| `extdata_fig5a.png` | Extended Data Fig. 5a | Validation curves: transformer vs dilated conv across model sizes / data fractions. | p. 17 (Ext. Data PDF page) |

**Tip:** Nature two-column layout often splits Fig. 1 across pages; use **single-page PDF export** or crop from the **HTML article figure** on nature.com if easier.

After updating crops, reload Slidev. Slides reference `./images/<filename>.png` via `<img class="paper-fig" …>` in `slides.md`.
