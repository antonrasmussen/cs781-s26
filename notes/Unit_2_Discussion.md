One Key Concept Learned: Representation of Genomic Sequences via One-Hot Encoding

A central concept from this module is using one-hot encoding to represent DNA sequences for deep learning. Unlike label encoding (e.g., A=1, C=2, G=3, T=4), which imposes artificial ordinal relationships among nucleotides, one-hot encoding preserves their categorical, non-hierarchical nature. Each nucleotide becomes a 4-dimensional vector (e.g., A = [1,0,0,0]), enabling convolutional filters to detect biologically meaningful motifs similarly to edge detection in computer vision.

Critically, this encoding choice is a modeling assumption, not merely a preprocessing detail: nucleotides are discrete symbolic units, not ordered quantities. Encoding them otherwise introduces spurious inductive biases that could produce misleading biological interpretations. From my data engineering background, this parallels schema design in healthcare pipelines, where poorly structured ingestion schemas introduce silent bias just as incorrect feature encoding distorts downstream model behavior.


One Exercise Result: CNNs Outperforming Transformers

An important observation was that a 1D CNN outperformed a Transformer on transcription-factor binding site classification, despite Transformers being state-of-the-art for many sequence tasks. This underscores that architectural superiority is task-dependent. CNNs are well-suited for detecting localized sequence motifs central to TF binding (signal locality), while Transformers excel at long-range dependencies that may not be critical in short genomic sequences.

Model selection in genomics should therefore be guided by biological signal structure -- motif locality vs. long-range regulatory interactions -- not by trends in ML literature. Deploying overly complex models without demonstrated domain-specific benefit risks reducing interpretability and increasing overfitting. This mirrors a familiar data engineering principle: the most scalable or modern system is not always the most appropriate one.


One Challenge: Interpreting Performance Beyond Accuracy

A key challenge was interpreting model performance in a biologically meaningful way rather than relying on aggregate accuracy alone. A model can achieve high accuracy while failing to capture true biological motifs, especially with class imbalance or dataset bias.

To address this, I analyzed normalized confusion matrices to examine error distributions across classes, paying particular attention to the False Positive Rate. This metric is especially relevant in clinical diagnostic contexts, where false positives can lead to over-treatment and carry significant patient risk. This shift from accuracy to error distribution transparency aligns with trustworthy AI practices that prioritize robustness over single-metric reporting. From my healthcare data engineering experience, this parallels how monitoring pipelines solely by throughput can mask silent data quality failures.


One Open Question: When Do Transformers Surpass CNNs in Genomics?

An open question is under what conditions Transformers begin to outperform CNNs in genomic analysis. Despite their theoretical power via self-attention, Transformers underperformed in this exercise. I hypothesize they will surpass CNNs when: (1) sequence lengths are long enough for long-range regulatory interactions to matter, (2) training datasets are large enough to support higher parameter complexity, or (3) the task involves global context (e.g., enhancer-promoter interactions) rather than local motif detection.

Systematically investigating these thresholds could form a meaningful research direction. This also intersects with trustworthy AI -- if Transformers require significantly larger datasets to generalize, their deployment in data-limited biomedical settings risks overfitting and reduced reliability. Understanding these tradeoffs is essential for building genomic AI systems that balance predictive power, interpretability, and data efficiency.


Concluding Reflection

This module reinforced that successful deep learning in genomics demands attention to data representation, domain-aligned architecture selection, and evaluation transparency. These challenges closely mirror those in healthcare data engineering, where data quality and bias mitigation directly influence analytic reliability. By integrating principled encoding, appropriate model selection, and rigorous performance analysis, we move toward a trustworthy AI paradigm where models are not only performant but also scientifically interpretable and operationally reliable.
