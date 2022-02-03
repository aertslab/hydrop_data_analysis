# HyDrop Data Analysis
Tutorials for HyDrop data analysis (and how exactly we came to the figures presented in the paper). Scripts should yield the exact same results if your package versions and file md5sums match the ones described in the tutorial, but newer versions are most likely also fine.

If you want to verify our results, make sure all package versions match. For example, the HyDrop-RNA data analysis was performed with scanpy 1.7.2 and anndata 0.7.6. I have re-run these scripts with scanpy 1.7.1 and anndata 0.7.5, and the cell filtering differed slightly (9511 instead of 9508 cells passing filter), leading to a slightly altered UMAP.

The directory `manuscript_beadqc` also contains all the raw .TIF microscopy images used in the manuscript, as well as the image analysis tool used to count them and perform simple analysis such as intensity and diameter measurements. The file "intensities.xlsx" also contains the parameters and measurements.
