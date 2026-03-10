# Research Papers

PDFs in this folder are course readings for CS781 – AI for Health Sciences (Spring 2026). Below: title, authors, page count, publication year, and a one-sentence summary for each.

| PDF | Title | Authors | Pages | Year | Summary |
|-----|--------|---------|-------|------|---------|
| `1706.04599v2.pdf` | On Calibration of Modern Neural Networks | Chuan Guo, Geoff Pleiss, Yu Sun, Kilian Q. Weinberger | 14 | 2017 | Shows that modern neural networks are poorly calibrated and that temperature scaling effectively restores reliable confidence estimates. |
| `1710.06071v1.pdf` | PubMed 200k RCT: a Dataset for Sequential Sentence Classification in Medical Abstracts | Franck Dernoncourt, Ji Young Lee | 6 | 2017 | Introduces a large dataset of ~200k RCT abstracts with sentence-level labels (background, objective, method, result, conclusion) for sequential sentence classification. |
| `1808.06752v2.pdf` | Lessons from Natural Language Inference in the Clinical Domain | Alexey Romanov, Chaitanya Shivade | 14 | 2018 | Presents MedNLI, a doctor-annotated NLI dataset from clinical notes, and strategies for transfer learning and domain knowledge in medical NLP. |
| `1972-05083-001.pdf` | (Communications of the ACM, 1972) | — | 5 | 1972 | Classic CACM article (exact title from metadata unavailable). |
| `2208.07339v2.pdf` | LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale | Tim Dettmers, Mike Lewis, Younes Belkada, Luke Zettlemoyer | 20 | 2022 | Enables 8-bit inference for large transformers (e.g. 175B parameters) with no accuracy loss via vector-wise quantization and mixed-precision handling of outlier dimensions. |
| `2305.14314v1.pdf` | QLoRA: Efficient Finetuning of Quantized LLMs | Tim Dettmers, Artidoro Pagnoni, Ari Holtzman, Luke Zettlemoyer | 26 | 2023 | Finetunes quantized LLMs (e.g. 65B on a single 48GB GPU) by backpropagating through frozen 4-bit weights into Low Rank Adapters while matching 16-bit quality. |
| `2402.10373v3.pdf` | BioMistral: A Collection of Open-Source Pretrained Large Language Models for Medical Domains | Yanis Labrak, Adrien Bazoge, Emmanuel Morin, Pierre-Antoine Gourraud, Mickael Rouvier, Richard Dufour | 17 | 2024 | Introduces medical LLMs based on Mistral, continued on PubMed Central, with strong performance on medical QA and the first large-scale multilingual medical LLM evaluation. |
| `775047.775151.pdf` | — | — | 7 | — | (Title and authors not identified from filename or metadata.) |
| `978-3-319-24574-4_28.pdf` | U-Net: Convolutional Networks for Biomedical Image Segmentation | Olaf Ronneberger, Philipp Fischer, Thomas Brox | 8 | 2015 | Proposes the U-Net architecture with contracting and expanding paths for accurate biomedical image segmentation from few annotated samples. |
| `Angelopoulos22-intro.pdf` | A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification | Anastasios N. Angelopoulos, Stephen Bates | 51 | 2022 | Practical introduction to conformal prediction and distribution-free uncertainty quantification with finite-sample guarantees and code examples. |
| `NIPS-2017-a-unified-approach-to-interpreting-model-predictions-Paper.pdf` | A Unified Approach to Interpreting Model Predictions | Scott M. Lundberg, Su-In Lee | 10 | 2017 | Unifies local explanation methods via Shapley values and introduces SHAP for interpreting any model’s predictions. |
| `bioinformatics_36_4_1234.pdf` | (Bioinformatics 36(4), 2020) | — | 7 | 2020 | Article from *Bioinformatics* vol. 36, issue 4 (see PDF for full citation). |
| `nature21056.pdf` | Dermatologist-level classification of skin cancer with deep neural networks | Andre Esteva et al. | 12 | 2017 | Demonstrates that a CNN trained on large clinical image datasets can classify skin lesions with accuracy matching board-certified dermatologists. |
| `s41586-021-03819-2.pdf` | Highly accurate protein structure prediction with AlphaFold | John Jumper et al. | 12 | 2021 | Presents AlphaFold 2, which achieves highly accurate protein structure prediction from sequence and wins CASP14. |
| `s41588-018-0295-5.pdf` | A primer on deep learning in genomics | James Zou et al. | 7 | 2019 | Tutorial on applying deep learning to genomics tasks (e.g. regulatory element prediction and variant effect) with practical guidance. |
| `s41592-021-01252-x.pdf` | Effective gene expression prediction from sequence by integrating long-range interactions | Žiga Avsec et al. | 24 | 2021 | Introduces Enformer, a transformer-based model that predicts gene expression and variant effects by integrating long-range (e.g. 100 kb) sequence context. |
| `srep26094.pdf` | Deep Patient: An Unsupervised Representation to Predict the Future of Patients from the Electronic Health Records | Riccardo Miotto et al. | 10 | 2016 | Learns unsupervised patient representations from EHRs with stacked denoising autoencoders to improve prediction of future diseases. |

---

*Page counts and metadata were extracted from the PDFs; titles, authors, years, and summaries were completed using arXiv, journal DOIs, and standard references where needed.*
