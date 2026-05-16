# %% [markdown]
# # Module 8 — Linear Algebra for ML
# Vectors, matrices, dot products, norms, projections, eigenvectors and
# SVD. The machinery beneath every regression, classification, neural
# network, and dimensionality-reduction technique.

# %% kind=import color=sky title="Imports"
import numpy as np
np.set_printoptions(precision=3, suppress=True)
np.random.seed(0)


# %% kind=assign color=peach title="Vectors and matrices"
# @explain: 1-D = vector. 2-D = matrix. Both are just NumPy arrays —
# @explain: shape is what tells them apart.
v = np.array([1.0, 2.0, 3.0])
A = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
print("v shape:", v.shape)
print("A shape:", A.shape)
print(A)


# %% kind=expr color=peach title="Dot product"
# @explain: a · b = Σ a_i · b_i. Geometric meaning: |a|·|b|·cos(θ).
# @explain: Zero dot product → perpendicular vectors. Used in every
# @explain: prediction step of a linear model.
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])
print("a · b =", np.dot(a, b))
print("a @ b =", a @ b)         # the matmul operator works on 1-D too
print("|a|   =", np.linalg.norm(a))
print("angle =", np.degrees(
    np.arccos(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
))


# %% kind=expr color=peach title="Matrix multiplication"
# @explain: A @ B is defined when A.shape = (m, k) and B.shape = (k, n).
# @explain: The most important op in deep learning — every dense layer
# @explain: is just (batch × W).
A = np.random.randn(3, 4)
B = np.random.randn(4, 2)
print("A:", A.shape, "B:", B.shape, "→ A @ B:", (A @ B).shape)


# %% kind=expr color=peach title="Transpose, identity, inverse"
# @explain: A.T flips rows and columns. I (identity) is the matrix that
# @explain: leaves vectors unchanged. inv(A) undoes A — exists only for
# @explain: square non-singular matrices.
A = np.array([[1.0, 2.0], [3.0, 4.0]])
print("A.T =\n", A.T)
print("I3  =\n", np.eye(3))
print("inv(A) =\n", np.linalg.inv(A))
print("check A @ inv(A) ≈ I :\n", (A @ np.linalg.inv(A)).round(6))


# %% [markdown]
# ## Norms — measuring length / size


# %% kind=expr color=peach title="L1, L2, infinity norms"
# @explain: L2 (Euclidean) is default. L1 (Manhattan) sums absolute
# @explain: values. L∞ is the largest absolute element. ML regularisers
# @explain: use L1 (Lasso) and L2 (Ridge) on the weight vector.
w = np.array([3.0, -4.0, 12.0])
print("L1 :", np.linalg.norm(w, ord=1))
print("L2 :", np.linalg.norm(w, ord=2))
print("L∞ :", np.linalg.norm(w, ord=np.inf))


# %% [markdown]
# ## Solving linear systems


# %% kind=function color=mint title="Ax = b — the right way"
# @explain: Don't compute inv(A) @ b for solving. Use np.linalg.solve —
# @explain: faster and numerically more stable.
A = np.array([[3.0, 1.0], [1.0, 2.0]])
b = np.array([9.0, 8.0])
x = np.linalg.solve(A, b)
print("x =", x)
print("check A @ x =", A @ x)


# %% kind=function color=mint title="Least-squares — overdetermined system"
# @explain: When A has more rows than unknowns, no exact solution
# @explain: exists. lstsq finds the x that minimises |Ax - b|².
# @explain: This is exactly how linear regression is solved.
A = np.array([
    [1.0, 1.0],
    [1.0, 2.0],
    [1.0, 3.0],
    [1.0, 4.0],
])
b = np.array([1.0, 2.5, 2.0, 4.0])
sol, residuals, rank, sv = np.linalg.lstsq(A, b, rcond=None)
print("[intercept, slope] =", sol)
print("residual sum of squares =", residuals)


# %% [markdown]
# ## Eigenvalues — the natural axes of a matrix


# %% kind=function color=mint title="Eigenvalues and eigenvectors"
# @explain: A v = λ v means "v keeps its direction when transformed by A,
# @explain: just scaled by λ". The basis of PCA, spectral clustering,
# @explain: graph algorithms.
A = np.array([[4.0, 1.0], [2.0, 3.0]])
eigvals, eigvecs = np.linalg.eig(A)
print("eigenvalues :", eigvals)
print("eigenvectors:\n", eigvecs)
for i, lam in enumerate(eigvals):
    Av = A @ eigvecs[:, i]
    lv = lam * eigvecs[:, i]
    print(f"  A @ v{i} =", Av, "  λ · v =", lv)


# %% [markdown]
# ## Singular value decomposition (SVD)
# Every matrix `A` can be written as `A = U Σ V^T`. SVD is the swiss
# army knife of linear algebra: dimensionality reduction (PCA),
# pseudo-inverse, low-rank approximations.


# %% kind=function color=mint title="SVD of a small matrix"
# @explain: U and V are orthogonal; Σ is diagonal of singular values
# @explain: in decreasing order. The biggest singular value tells you
# @explain: the dominant direction in the data.
A = np.random.randn(4, 3)
U, s, Vt = np.linalg.svd(A, full_matrices=False)
print("U shape:", U.shape, "s:", s.shape, "Vt shape:", Vt.shape)
print("singular values:", s)
recon = U @ np.diag(s) @ Vt
print("max reconstruction error:", np.abs(A - recon).max())


# %% kind=function color=mint title="Low-rank approximation"
# @explain: Keep only the top k singular values and zero out the rest.
# @explain: This is how image compression and PCA both work.
k = 1
A_k = U[:, :k] @ np.diag(s[:k]) @ Vt[:k]
print(f"rank-{k} approximation:\n", A_k)
print("error:", np.linalg.norm(A - A_k))


# %% [markdown]
# ## A whole linear regression with NumPy


# %% kind=function color=mint title="Linear regression via the normal equation"
# @explain: w = (XᵀX)⁻¹ Xᵀy — the closed-form least-squares solution.
# @explain: This is what `sklearn.linear_model.LinearRegression` does
# @explain: under the hood (with a more numerically stable solver).
n = 100
X = np.random.randn(n, 2)
true_w = np.array([2.0, -3.0])
true_b = 1.5
y = X @ true_w + true_b + 0.3 * np.random.randn(n)

# Add a column of 1s to absorb the bias term.
X_aug = np.hstack([np.ones((n, 1)), X])
w_hat = np.linalg.solve(X_aug.T @ X_aug, X_aug.T @ y)
print("true   :", [true_b, *true_w])
print("learned:", w_hat.round(3))


# %% [markdown]
# ## Practice
# 1. Compute the L2 norm of a (5,5) standard-normal matrix' first column.
# 2. Solve the system  2x + y = 5, x − 3y = -8. Confirm the residual.
# 3. Get eigenvalues of `[[2,0],[0,5]]`. They should be exactly 2 and 5.


# %% kind=function color=mint title="Practice 1 — norm of a column"
M = np.random.randn(5, 5)
print("||M[:,0]||₂ =", np.linalg.norm(M[:, 0]))


# %% kind=function color=mint title="Practice 2 — solve the small system"
# @explain: Build A and b carefully, solve, check.
A = np.array([[2.0, 1.0], [1.0, -3.0]])
b = np.array([5.0, -8.0])
x = np.linalg.solve(A, b)
print("solution:", x)
print("residual:", A @ x - b)


# %% kind=function color=mint title="Practice 3 — diagonal eigenvalues"
# @explain: Eigenvalues of a diagonal matrix are exactly its entries.
A = np.array([[2.0, 0.0], [0.0, 5.0]])
print("eigvals:", np.linalg.eigvals(A))


# %% [markdown]
# ## Recap
# - ✅ Vectors, matrices, dot product, matmul
# - ✅ Transpose, inverse, identity
# - ✅ L1 / L2 / L∞ norms
# - ✅ solve, lstsq
# - ✅ eig, SVD, low-rank
# - ✅ Closed-form linear regression
#
# **Next:** Module 9 — Probability for ML.
