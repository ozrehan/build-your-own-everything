# Example: AI/ML — Neural Net Playground

**[▶ Try it live](https://byoe-neural-net.netlify.app)**

A real neural network (2→H→1 MLP, tanh + sigmoid) trained with **backprop** —
zero libraries, ~70 lines of JS. Click to add points, hit train, watch the
decision boundary learn live.

Example project for the [ai/ml learning path](../../topics/neural-net-from-scratch/).

## What it teaches

- **Forward pass**: weighted sums + activations → prediction.
- **Loss**: binary cross-entropy.
- **Backward pass**: the chain rule gives every weight its gradient.
- **Gradient descent**: weights step downhill, epoch by epoch.

Try the **🌀 SPIRAL** dataset: a straight line can't solve it, but 6 hidden neurons can.
That's why depth matters.

## Exercises

1. Add **L2 regularization** and watch the boundary smooth out.
2. Visualize **hidden neuron activations** as separate heatmaps.
3. Swap in **ReLU** and compare training speed (see the `transformer-from-scratch` topic next).
