# Examples

Drop any of these files into DoodleCode Studio (📂 Open) to see them
rendered as a doodle canvas. They use the project's own
[file format](../docs/FILE_FORMAT.md) and are valid Python that runs
end-to-end outside the app.

## Onboarding

| File | What it shows | Cells |
|------|---------------|-------|
| [`how_it_works.py`](how_it_works.py) | In-app tutorial: callout editor, save / export, presentation mode. | 9 |

## Python foundations

| File | Topic |
|------|-------|
| [`module_01_python_basics.py`](module_01_python_basics.py) | Types, strings, formatting, debugging |
| [`module_02_file_handling.py`](module_02_file_handling.py) | File I/O, CSV, JSON, pathlib, log rotation |
| [`module_03_ai_doodle_demo.py`](module_03_ai_doodle_demo.py) | A working PyTorch model in 6 colored sections |

## Python for Machine Learning (10-part series)

A self-contained ML curriculum, each file ~20–40 cells with structured
callouts on every code block.

| # | File | Topic |
|---|------|-------|
| 4  | [`module_04_numpy_for_ml.py`](module_04_numpy_for_ml.py)       | NumPy: arrays, indexing, broadcasting, vectorisation |
| 5  | [`module_05_pandas_for_ml.py`](module_05_pandas_for_ml.py)     | Pandas: DataFrames, filtering, groupby, merging |
| 6  | [`module_06_visualization.py`](module_06_visualization.py)     | matplotlib + seaborn: line, scatter, heatmap, pairplot |
| 7  | [`module_07_statistics.py`](module_07_statistics.py)           | Mean / variance, distributions, correlation, CLT, hypothesis tests |
| 8  | [`module_08_linear_algebra.py`](module_08_linear_algebra.py)   | Dot product, matmul, norms, eigendecomposition, SVD, normal equation |
| 9  | [`module_09_probability.py`](module_09_probability.py)         | Distributions, Bayes, LLN, MLE, Monte Carlo π |
| 10 | [`module_10_preprocessing.py`](module_10_preprocessing.py)     | Imputation, scaling, encoding, train/test split, pipelines |
| 11 | [`module_11_sklearn_basics.py`](module_11_sklearn_basics.py)   | fit/predict API, metrics, K-fold CV, model comparison |
| 12 | [`module_12_regression.py`](module_12_regression.py)           | Linear, polynomial, ridge/lasso, logistic regression |
| 13 | [`module_13_neural_networks.py`](module_13_neural_networks.py) | NN from scratch in NumPy, then sklearn MLP, then PyTorch |

## Writing your own

Start from the in-app tutorial — duplicate `how_it_works.py`, change
the cells, and save. The file you save is exactly the format the app
reads. See [docs/FILE_FORMAT.md](../docs/FILE_FORMAT.md) for the spec
and the colour palette.
