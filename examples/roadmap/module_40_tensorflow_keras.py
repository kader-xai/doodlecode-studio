# doodlecode format-version: 2
# Auto-converted from module_40_tensorflow_keras.ipynb
# Open with 📂 Open → press 🎬 Present.


# %% [markdown] color=rose title="Module 40 Tensorflow Keras"
# # Module 40 Tensorflow Keras
#
# A live walkthrough — one card per concept.
# Use → / ← to step through. Press 🎬 Present to begin.



# %% [markdown] color=sky title="Module 40 — TensorFlow & Keras"
# # Module 40 — TensorFlow & Keras
#
# > Most of the course is PyTorch (M16-M24, M39). But a huge slice of production ML — Google products, mobile apps via **TF Lite**, embedded devices, the entire Keras-3 ecosystem — runs on TensorFlow. **Keras 3** is now backend-agnostic (TF / JAX / PyTorch), but the workflow you'll see at TF shops is still the classic Keras one. This module makes you bilingual.
#
# ### What you'll cover
# 1. TF vs PyTorch — when each wins
# 2. Tensors, eager mode, `tf.function` (graph mode)
# 3. **`tf.data`** — input pipelines that don't bottleneck the GPU
# …


# %% [markdown] color=mint title="1 · TF vs PyTorch — when each wins"
# # 1 · TF vs PyTorch — when each wins
#
# | TensorFlow / Keras wins | PyTorch wins |
# |---|---|
# | Mobile (TF Lite), browser (TF.js), microcontrollers (TF Micro) | Research, frontier model code (LLMs, diffusion) |
# | TPU support is first-class | NVIDIA GPU support is first-class |
# | Production deploy story (TF Serving, Vertex AI) is mature | HF / vLLM / Unsloth / Triton ecosystem |
# | Great for tabular + classic CV / time-series at scale | Most academic papers ship PyTorch reference code |
# …


# %% [markdown] color=peach title="2 · Tensors, eager mode, `tf.function`"
# # 2 · Tensors, eager mode, `tf.function`
#


# %% color=violet title="!pip -q install tensorflow"
# @explain: Run this cell to see the output.
!pip -q install tensorflow


# %% color=amber title="Tensors look like numpy arrays"
# @explain: Tensors look like numpy arrays
import tensorflow as tf
print(tf.__version__, "  GPU:", tf.config.list_physical_devices('GPU'))

# Tensors look like numpy arrays
a = tf.constant([[1.,2.],[3.,4.]])
b = tf.constant([[5.,6.],[7.,8.]])
print(a @ b)             # eager: runs immediately like numpy/torch


# %% color=rose title="Decorate a Python function with @tf.function to…"
# @explain: Decorate a Python function with @tf.function to compile it into a static graph
# @explain: First call traces; subsequent calls are fast (no Python overhead)
# Decorate a Python function with @tf.function to compile it into a static graph.
# First call traces; subsequent calls are fast (no Python overhead).
@tf.function
def fast_op(x, y):
    return tf.reduce_sum(x @ y)

print(fast_op(a, b))     # first call: traces + executes
print(fast_op(a, b))     # second call: pure graph, fast


# %% [markdown] color=lime title="3 · `tf.data` — input pipelines"
# # 3 · `tf.data` — input pipelines
#
# `tf.data.Dataset` is TF's answer to PyTorch's `DataLoader`. It builds a pipeline that pre-fetches and overlaps CPU + GPU work — the easiest 1.5-3× speedup you can get on a real training loop.


# %% color=teal title="import numpy as np"
# @explain: Run this cell to see the output.
import numpy as np

xs = np.random.randn(10_000, 32).astype("float32")
ys = (xs.sum(axis=1) > 0).astype("int32")

ds = (tf.data.Dataset.from_tensor_slices((xs, ys))
        .shuffle(1024)
        .batch(64)
        .prefetch(tf.data.AUTOTUNE))      # overlap GPU compute with next batch's prep
print(ds)


# %% [markdown] color=sky title="4 · Keras Sequential — fastest path to MNIST"
# # 4 · Keras Sequential — fastest path to MNIST
#


# %% color=mint title="(x_train, y_train)"
# @explain: Run this cell to see the output.
(x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
x_train = x_train.astype("float32") / 255.0
x_test  = x_test.astype("float32") / 255.0
print(x_train.shape, y_train.shape)


# %% color=peach title="model = tf.keras.Sequential(["
# @explain: Run this cell to see the output.
model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(28,28)),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(128, activation="relu"),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(10),                  # logits
])
model.compile(
    optimizer="adam",
    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
    metrics=["accuracy"],
)
model.summary()


# %% color=violet title="model.fit(x_train"
# @explain: Run this cell to see the output.
model.fit(x_train, y_train, epochs=2, batch_size=128, validation_split=0.1)
model.evaluate(x_test, y_test, verbose=2)


# %% [markdown] color=amber title="5 · Keras Functional — branching, multi-input"
# # 5 · Keras Functional — branching, multi-input
#


# %% color=rose title="Tiny example: image branch + tabular branch →…"
# @explain: Tiny example: image branch + tabular branch → concatenate → classify
# Tiny example: image branch + tabular branch → concatenate → classify
img_in = tf.keras.Input(shape=(28,28,1), name="image")
tab_in = tf.keras.Input(shape=(5,),       name="tabular")

x = tf.keras.layers.Conv2D(8, 3, activation="relu")(img_in)
x = tf.keras.layers.GlobalAveragePooling2D()(x)
y = tf.keras.layers.Dense(8, activation="relu")(tab_in)
z = tf.keras.layers.Concatenate()([x, y])
out = tf.keras.layers.Dense(10)(z)

multi = tf.keras.Model(inputs={"image": img_in, "tabular": tab_in}, outputs=out)
multi.summary()


# %% [markdown] color=lime title="6 · Keras Subclassing — full control (PyTorch-style)"
# # 6 · Keras Subclassing — full control (PyTorch-style)
#


# %% color=teal title="class Tiny(tf.keras.Model)"
# @explain: Run this cell to see the output.
class Tiny(tf.keras.Model):
    def __init__(self):
        super().__init__()
        self.flat = tf.keras.layers.Flatten()
        self.d1 = tf.keras.layers.Dense(64, activation="relu")
        self.d2 = tf.keras.layers.Dense(10)
    def call(self, x, training=False):
        return self.d2(self.d1(self.flat(x)))

m = Tiny()
m.compile(optimizer="adam",
          loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
          metrics=["accuracy"])
m.fit(x_train, y_train, epochs=1, batch_size=128, verbose=2)


# %% [markdown] color=sky title="7 · Callbacks — the production utilities"
# # 7 · Callbacks — the production utilities
#


# %% color=mint title="(Pass `callbacks=callbacks` into model.fit(...)"
# @explain: (Pass `callbacks=callbacks` into model.fit(...) — skipped here to keep the demo short.)
callbacks = [
    tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=2, restore_best_weights=True),
    tf.keras.callbacks.ModelCheckpoint("best.keras", save_best_only=True, monitor="val_loss"),
    tf.keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=1),
    tf.keras.callbacks.TensorBoard(log_dir="logs", histogram_freq=1),
]
# (Pass `callbacks=callbacks` into model.fit(...) — skipped here to keep the demo short.)


# %% [markdown] color=peach title="8 · Save / load"
# # 8 · Save / load
#


# %% color=violet title="model.save('mnist.keras')            # native Keras…"
# @explain: Run this cell to see the output.
model.save("mnist.keras")            # native Keras format (single zip)
loaded = tf.keras.models.load_model("mnist.keras")
print(loaded.evaluate(x_test, y_test, verbose=0))


# %% color=amber title="SavedModel"
# @explain: SavedModel — language-agnostic, what TF Serving / Vertex AI expect
# SavedModel — language-agnostic, what TF Serving / Vertex AI expect
model.export("mnist_saved")
!ls mnist_saved


# %% [markdown] color=rose title="9 · TF Lite — mobile / edge"
# # 9 · TF Lite — mobile / edge
#
# `TFLiteConverter` turns a model into a single `.tflite` file you can drop into an Android app or a Raspberry Pi. Optionally **quantise** to int8 for ~4× smaller + faster on CPUs without FPUs.


# %% color=lime title="converter =…"
# @explain: Run this cell to see the output.
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]   # post-training quantisation
tflite_bytes = converter.convert()
open("mnist.tflite","wb").write(tflite_bytes)
print("size:", len(tflite_bytes), "bytes")


# %% color=teal title="Run inference with the .tflite interpreter"
# @explain: Run inference with the .tflite interpreter (the same runtime ships in Android / iOS)
# Run inference with the .tflite interpreter (the same runtime ships in Android / iOS)
interp = tf.lite.Interpreter(model_content=tflite_bytes); interp.allocate_tensors()
inp = interp.get_input_details()[0]; out = interp.get_output_details()[0]
sample = x_test[:1].astype(inp["dtype"])
interp.set_tensor(inp["index"], sample); interp.invoke()
print("predicted:", interp.get_tensor(out["index"]).argmax(), "  true:", y_test[0])


# %% [markdown] color=sky title="10 · TF Serving — what production looks like"
# # 10 · TF Serving — what production looks like
#
# ```bash
# # host the SavedModel behind a gRPC + REST API, one command:
# docker run -p 8501:8501 \
#     -v $PWD/mnist_saved:/models/mnist/1 \
#     -e MODEL_NAME=mnist \
#     tensorflow/serving
# …


# %% [markdown] color=mint title="✅ Recap"
# # ✅ Recap
#
# - TF / Keras shines for **mobile (TF Lite), TPU, GCP-native deploys**.
# - Keras has **three APIs**: Sequential (lines), Functional (graphs), Subclassing (full control).
# - **`tf.data`** + `prefetch(AUTOTUNE)` keeps the GPU fed.
# - **`@tf.function`** compiles Python → static graph for speed.
# - **TFLite** for edge, **SavedModel + TF Serving** for the cloud.
#
# Next: **M41 — CUDA basics** (writing your own GPU kernels).


# %% [markdown] color=lime title="Thanks"
# # End of Module
#
# Next module continues the roadmap.
# Source: https://github.com/kader-xai/data-science-roadmap


