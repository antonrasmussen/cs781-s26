# CS781 — Proposed Papers for Presentation  
**Anton Rasmussen · Spring 2026**

## Why I chose these papers
For class, I want to present **two “anchor” papers**:

- **One classic, highly cited EHR paper** that established a practical baseline for representation learning on longitudinal clinical records.
- **One newer genomics paper** that shows what modern deep learning looks like when the “input” is biological sequence and the goal is functional prediction.

That combo gives me two major modalities the course emphasizes (**clinical records + biological sequence**) and it also lines up with my current work in the lab on **All of Us (AoU) respiratory disease analysis**.

> *Note:* Everything listed here is **primary research** (original empirical studies with new methods/results), not review articles.

---

## Papers I’m ready to present (my top two)

### 1) Miotto et al. (2016) — *Deep Patient*  
**Area:** EHR representation learning / clinical prediction

**Why I picked it:** This is one of the early papers that made “learn an embedding from longitudinal EHR codes and use it for prediction” feel concrete and useful. It’s also a great paper for talking about the stuff that can quietly break clinical ML: coding drift, site bias, temporal leakage, and confounding.

**Why it fits my work:** I can translate the ideas directly to AoU-style cohort work (stratifying patients and predicting/characterizing outcomes related to respiratory disease).

**How I’ll present it (what I’ll focus on):**
- How the unsupervised patient representations are learned from longitudinal EHR data  
- Evaluation setup and the common failure modes (leakage, confounding, site effects)  
- How I’d adapt the pattern to AoU in a responsible way (cohort definition, validation strategy, and what “good” looks like)

---

### 2) Avsec et al. (2021) — *Enformer*  
**Area:** Regulatory genomics / sequence → function

**Why I picked it:** I want one talk that’s *not* EHR, and Enformer is a strong modern example of deep learning applied to genomics where the key challenge is **long-range context** in DNA. The paper is also very teachable because it’s clear about inputs/outputs, benchmarks, and the limits of interpretation.

**Why it fits my work:** If I extend respiratory work beyond phenotype/EHR into genotype/regulatory interpretation (or even just want a serious reference point for sequence modeling in biomed), this paper is a strong anchor.

**How I’ll present it (what I’ll focus on):**
- Why long-range context matters for gene regulation  
- What the model predicts, what the training data looks like, and how performance is measured  
- Variant-effect prediction: what you can infer vs what you *can’t* infer, especially for clinical translation

---

## Other papers I can present if needed (backup options)

### 3) Jumper et al. (2021) — *AlphaFold*  
**Area:** Protein structure prediction  
**Why I’d present it:** It changed the field and it’s a clean way to discuss evaluation (CASP), generalization, and what “breakthrough performance” means in practice.  
**What I’d focus on:** The core idea of the architecture at a high level, how it was evaluated, and the difference between scientific utility and clinical validation.

### 4) Ronneberger et al. (2015) — *U-Net*  
**Area:** Biomedical image segmentation  
**Why I’d present it:** U-Net is the foundation for a lot of medical imaging segmentation work and it’s very teachable.  
**What I’d focus on:** Encoder–decoder + skip connections, segmentation losses, and the real-world issues (label quality and domain shift).

### 5) Esteva et al. (2017) — Skin cancer classification  
**Area:** Clinical imaging classification  
**Why I’d present it:** Strong example for discussing study design, dataset shift, calibration, and what it takes to make “clinician-level” claims meaningful.  
**What I’d focus on:** How the comparisons are set up and what you’d need to reproduce/translate it into a real workflow.

### 6) Lee et al. (2020) — *BioBERT*  
**Area:** Biomedical NLP  
**Why I’d present it:** It’s a key bridge paper: it shows domain-adaptive pretraining and sets up the path toward modern clinical NLP and today’s LLM ecosystem.  
**What I’d focus on:** What domain pretraining buys you, how biomedical NLP tasks are evaluated, and what changes when you move from BioBERT-era models to current LLMs.

---

## Optional: I can also present my own project direction
If it’s useful for the class, I can present a short talk on my lab-aligned direction:
- Exploratory respiratory disease analysis in AoU (COPD/asthma/allergies + SDOH)  
- A forward-looking privacy-preserving / decentralized AI framing (TinyLLM-style ideas) as a roadmap  
- Potential integration of environmental factors via Google Earth Engine / AlphaEarth-style embeddings as a methodological extension (without applying an LLM directly to participant-level AoU data at this stage)

---

## References (APA)

Avsec, Ž., Agarwal, V., Visentin, D., Ledsam, J. R., Grabska-Barwińska, A., Taylor, K. R., … Kelley, D. R. (2021). Effective gene expression prediction from sequence by integrating long-range interactions. *Nature Methods, 18*, 1196–1203. https://doi.org/10.1038/s41592-021-01252-x

Esteva, A., Kuprel, B., Novoa, R. A., Ko, J., Swetter, S. M., Blau, H. M., & Thrun, S. (2017). Dermatologist-level classification of skin cancer with deep neural networks. *Nature, 542*(7639), 115–118. https://doi.org/10.1038/nature21056

Jumper, J., Evans, R., Pritzel, A., Green, T., Figurnov, M., Ronneberger, O., … Hassabis, D. (2021). Highly accurate protein structure prediction with AlphaFold. *Nature, 596*(7873), 583–589. https://doi.org/10.1038/s41586-021-03819-2

Lee, J., Yoon, W., Kim, S., Kim, D., Kim, S., So, C. H., & Kang, J. (2020). BioBERT: A pre-trained biomedical language representation model for biomedical text mining. *Bioinformatics, 36*(4), 1234–1240. https://doi.org/10.1093/bioinformatics/btz682

Miotto, R., Li, L., Kidd, B. A., & Dudley, J. T. (2016). Deep Patient: An unsupervised representation to predict the future of patients from the electronic health records. *Scientific Reports, 6*, 26094. https://doi.org/10.1038/srep26094

Ronneberger, O., Fischer, P., & Brox, T. (2015). U-Net: Convolutional networks for biomedical image segmentation. In N. Navab, J. Hornegger, W. M. Wells, & A. F. Frangi (Eds.), *Medical Image Computing and Computer-Assisted Intervention – MICCAI 2015* (Lecture Notes in Computer Science, Vol. 9351, pp. 234–241). Springer. https://doi.org/10.1007/978-3-319-24574-4_28
