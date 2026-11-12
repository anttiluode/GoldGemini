# GoldGemini — 16,384 Self-Writing XOR Rings (`GN-Ghost`)

**Interactive laboratories**

- [Full GN-Ghost lab](https://anttiluode.github.io/GoldGemini/gn_ghost_16_384_self_writing_xor_rings.html)
- [Compact GN-Ghost lab](https://anttiluode.github.io/GoldGemini/gemini-code-1794475672200.html)

*12 November 2026 · Geometric Neuron / GN-XOR / KultaaVaiKatinkultaa research lineage*

GoldGemini scales a **one-wire, non-monotonic XOR-flip memory rule** into a browser demonstration of a 64 × 64 pixel surface, with four bit-planes per pixel: **16,384 logical delay rings**. A period-`L` buffer stores the past `L` binary frames for each bit-plane. Once a scene repeats with a period compatible with `L`, the difference signal falls silent while the ring continues replaying it.

> **Scope:** This is a deterministic, fast reduced-window simulation, **not 16,384 instances of the original `ecg.json` Geometric Neuron**, a trained model, or a measured neuromorphic hardware implementation.

## Origin: from band-pass firing to one-wire memory

This experiment follows [GN-XOR](https://github.com/anttiluode/GN-XOR) and [KultaaVaiKatinkultaaOpus](https://github.com/anttiluode/KultaaVaiKatinkultaaOpus), which explored a non-monotonic excitation regime exposed by the Geometric Neuron work. In the reduced model, a bit fires only when its weighted input is **strictly inside** the band

```text
fire(d) = 1 if -14.7 < d < -6.1, otherwise 0
WIRE = 2.0
```

With a world bit `W`, ring bit `R`, and error bit `E`, the comparator uses equal weights of `-4.5` on `W` and `R`. Exactly one active input gives drive `-9` and a spike; two active inputs give `-18` and no spike. This implements an XOR comparator:

```text
E = W XOR R
```

The ring update takes the existing ring bit (self-weight `-6.0`) and **one unsigned error wire** (feedback weight `-4.5`). The four cases are:

| Existing ring bit R | Error E | Drive = 2(-6R - 4.5E) | Next ring bit R' | Meaning |
| :---: | :---: | ---: | :---: | --- |
| 0 | 0 | 0 | 0 | Stay empty |
| 0 | 1 | -9 | 1 | Write missing beat |
| 1 | 0 | -12 | 1 | Retain beat |
| 1 | 1 | -21 | 0 | Erase obsolete beat |

The overshoot at `-21` is crucial: **the same positive-going error event writes an empty slot and erases an occupied slot**, depending on the state already circulating in the ring.

Algebraically, in this specific ideal binary circuit:

```text
E  = W XOR R
R' = R XOR E = W
```

This is exact copying of the current world bit into the corresponding ring slot, not gradual learning of synaptic weights. The prior research reported that the reduced-window control reproduced this circuit without evaluating the original large checkerboard lookup. GoldGemini uses the reduced rule rather than the original Geometric Neuron simulator.

## What the lab demonstrates

### 1. A moving surface learned by silence

The **64 × 64 display has four one-bit planes per pixel** (16 quantized grayscale levels). Every logical bit has a delay history of length `L`; at the default `L = 16`, the simulation holds `16 × 16,384 = 262,144` bits of logical ring state.

The full laboratory shows three views:

1. **World (W):** Periodic scenes (including orbiting shapes), a polar checkerboard, a crescent, user drawing, or webcam input.
2. **Ring memory (R):** The frame retrieved from the circulating delay state, updated by the single error wire.
3. **Surprise (E = W XOR R):** Exactly the bits that disagree on the current tick.

Starting with an empty ring and a *strictly repeating* period-16 world, the ring learns a complete lap. After that, the error can drop to **0% even though the movie is still moving**. The zero is a count of discrepancy bits, **not a measured reduction in electrical energy**.

Aperiodic motion, changing webcam frames, noise, or a mismatch between scene and ring period can keep producing error. A webcam does **not** automatically converge to zero just because a face is visible.

### 2. Blindfold: autonomous replay

After the ring has learned a periodic scene, choose **Blindfold World**. The full lab disconnects error feedback from the ring so that it preserves the acquired slots and keeps replaying them without new world updates. The compact lab provides a corresponding ghost-replay experiment.

This is **stored loop playback**: the old delay-buffer contents remain active. It is not evidence that the circuit can infer unseen future changes in an external world.

### 3. Period selection and comb-filter behavior

The period slider sets the ring lap length `L`. Under exact deterministic timing, a scene with period `P` reaches a stable zero-error replay when **`P` divides `L`**. For `L = 16`, that includes `P = 1, 2, 4, 8, 16`. Other periods generally leave residual mismatch unless the actual content has a shorter repeating period.

Changing `L` is a useful probe of the delay memory's temporal selectivity; it does not train the circuit to generalize to arbitrary periods.

### 4. ±1-tick jitter: a separate plateau experiment

In [GN-XOR](https://github.com/anttiluode/GN-XOR), two synchronous two-tick pulses can fail to cancel after a ±1-tick shift: the unmatched leading and trailing edges produce false error events.

The Python benchmark in this repository tests a **specific temporal-filtering control**:

- Expand each two-tick pulse by two ticks into its trailing envelope.
- Compute mismatches between the expanded world and prediction streams.
- Report an error only after **three consecutive mismatch ticks**.

For its fixed synthetic ±1-tick jitter schedule, the supplied benchmark reports **26 raw false-error ticks and zero plateau-filter false-error ticks**. This is a result for that test configuration, not proof of a universal timing-jitter cure.

**Important implementation distinction:** The full HTML lab's **Synaptic Hold τ** control extends **only the effective world-bit activation** using per-bit hold timers. It does **not** implement the Python benchmark's symmetric expansion plus three-tick mismatch requirement. Therefore the Python's zero-false-error result must not be attributed to the HTML hold slider without a separate comparison.

A sustained-mismatch filter may also suppress real short-lived novelty. The present benchmark does **not** measure missed true events, detection latency, or performance across broader timing distributions. Those are necessary controls before claiming a general improvement in recognition.

## Files

| Path | Purpose |
| --- | --- |
| [`gn_ghost_16_384_self_writing_xor_rings.html`](gn_ghost_16_384_self_writing_xor_rings.html) | Full interactive 16,384-bit-plane ring laboratory: scenes, error telemetry, period/weight/jitter/hold controls, webcam, blindfold and perturbation brush. |
| [`gemini-code-1794475672200.html`](gemini-code-1794475672200.html) | Compact single-file laboratory with its own embedded styling and JavaScript. |
| [`gemini-code-1794475691788.py`](gemini-code-1794475691788.py) | NumPy benchmark: 1,024 binary ring streams for a 32 × 32 moving scene, plus the separate jitter/plateau control. |
| [`.github/workflows/static.yml`](.github/workflows/static.yml) | GitHub Pages deployment workflow. |
| [`LICENSE`](LICENSE) | MIT license. |

## Run it locally

### Browser

Open either HTML file in a modern browser, or use the [GitHub Pages links](#goldgemini--16384-self-writing-xor-rings-gn-ghost) above.

- **Compact lab:** embedded CSS/JavaScript, with no external library downloads required for the basic simulation.
- **Full lab:** simulation logic is included in the HTML, but presentation currently loads **Tailwind from a CDN and Google Fonts**; some styling therefore requires an internet connection. Camera access also needs browser permission and an eligible secure context (for example HTTPS or, depending on browser, localhost).

The full lab is not advertised as a fully offline-styled experience.

### Python / NumPy

From the repository directory:

```bash
python -m pip install numpy
python gemini-code-1794475691788.py
```

Expected output for the script's current defaults, as supplied with the project:

```text
2D Moving Movie (1,024 rings) Error Spikes per Lap: [1104, 0, 0, 0]
Jitter (+/-1 tick) False Error Ticks: {'raw_false_error_ticks': 26, 'plateau_false_error_ticks': 0}
ALL CHECKS PASSED.
```

The Python test uses **32 × 32 × 1 = 1,024 binary streams**, while the browser demonstration uses **64 × 64 × 4 = 16,384**. These are separate test sizes; the small NumPy test is not a performance benchmark of the full browser array.

## Honest ledger and limitations

| Supported by the implementation | Not established by this repository |
| --- | --- |
| A windowed binary gate can implement the shown XOR and XOR-flip truth tables. | Learning weights, semantic rules, or general-purpose intelligence. |
| A one-wire mismatch event updates each stored ring slot, writing or erasing depending on its state. | Biological equivalence of the reduced window to a real neuron or a full `gn27.py` node. |
| An exact periodic scene can reach zero discrepancy after a lap, then replay from stored state with feedback muted. | Prediction of novel, non-periodic future events. |
| The Python plateau control eliminates false positives for its stated synthetic jitter test. | General anti-jitter robustness, preserved true-positive detection, or a verified identical browser implementation. |
| The error channel may be silent at equilibrium. | Hardware energy savings or power measurements. |

This is an **interpretable delay-memory / novelty-filter demonstration**, deliberately reducing the dynamics to a simple binary window and shift-register-like memory. It should be compared with simpler direct-buffer and digital-XOR baselines when evaluating its usefulness beyond the original Geometric Neuron lineage.

## Direct genealogy

1. [PerceptionLab](https://github.com/anttiluode/PerceptionLab) — Original 2025 `ecg.json` node graph.
2. [GeometricNeuronOriginReview](https://github.com/anttiluode/GeometricNeuronOriginReview) — Causal reduction and analysis of a reported 59-tick forgetting clock.
3. [GeometricNeuronSurfaceListener (V26)](https://github.com/anttiluode/GeometricNeuronSurfaceListener) — `setpoint_mod`, silent relays and two-source cancellation.
4. [GeometricNeuronV27](https://github.com/anttiluode/GeometricNeuronV27) — Native delay-line ring experiments and cable attenuation.
5. [GN-XOR](https://github.com/anttiluode/GN-XOR) — `setpoint_mod` XOR truth table and closed-loop ring mismatch detection.
6. [KultaaVaiKatinkultaa](https://github.com/anttiluode/KultaaVaiKatinkultaa) and [KultaaVaiKatinkultaaOpus](https://github.com/anttiluode/KultaaVaiKatinkultaaOpus) — One-wire write/erase circuit and reduced-window control.
7. **GoldGemini (this repository)** — 16,384-stream visual delay-memory demonstration and a separate plateau/jitter benchmark.

## License

[MIT](LICENSE).
