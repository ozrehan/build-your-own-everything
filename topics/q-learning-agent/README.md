---
title: "Q-Learning Agent"
category: "ai-ml"
difficulty: "intermediate"
tags: [reinforcement-learning, q-learning, agents]
related: [agent-framework-react, decision-tree, 2d-game-engine]
---

# Q-Learning Agent

Q-learning teaches an agent to act by trial and error: it maintains a table (or network) estimating the future reward of each action in each state, and improves those estimates from experience. Implementing it on a grid world — then scaling to Deep Q-Networks on Atari-style games — is the clearest path into reinforcement learning.

## Core concepts

- **Markov Decision Process** — The formalism: states, actions, transition probabilities, and rewards, with the Markov property that the future depends only on the present state. Every RL problem is an MDP wearing a costume.
- **Q-values** — Q(s, a) is the expected total future reward of taking action a in state s and behaving optimally after. If you knew all Q-values, the optimal policy would be trivially "always pick the max".
- **Bellman update** — The heart of Q-learning: `Q(s,a) ← Q(s,a) + α[r + γ·max Q(s′,a′) − Q(s,a)]`. Each experience nudges the estimate toward a one-step-lookahead target built from the current estimates — bootstrapping, learning from guesses about guesses.
- **Exploration vs exploitation** — The agent must sometimes try random actions to discover better strategies. ε-greedy (random action with probability ε, decaying over time) is the simple workhorse; getting the schedule right is half the battle.
- **Experience replay** — Deep Q-Networks store transitions in a buffer and train on random mini-batches, breaking the correlation of consecutive experiences that would otherwise destabilize neural-network training.
- **Target networks** — A frozen copy of the Q-network generates the Bellman targets, updated periodically. Without it, the network chases a moving target (its own changing predictions) and diverges.

## How it works

Tabular version: initialize a Q-table of zeros, then loop — observe state, pick an action ε-greedily, execute it, observe reward and next state, and apply the Bellman update. Over thousands of episodes the table converges toward optimal values. Deep version: replace the table with a neural network mapping states to Q-values per action, sample mini-batches from a replay buffer, compute Bellman targets with the frozen target network, and train with gradient descent. The algorithm is the same; only the function approximator changed.

## Build milestones

1. Implement tabular Q-learning on a grid world (cliff-walking or frozen lake); visualize the learned policy as arrows.
2. Tune the exploration schedule and discount factor; plot episode reward over time and diagnose failure modes (too greedy, too random).
3. Scale to Deep Q-Network on CartPole: neural net Q-function, experience replay, target network.
4. Add the DQN improvements that matter: double DQN (decouple action selection from evaluation) and dueling architecture; compare learning curves.
5. Train on a pixel-based environment (e.g. a simple Gymnasium game with frame stacking) and record a video of the learned policy.

## Best resources

- [Reinforcement Learning: An Introduction (Sutton & Barto)](http://incompleteideas.net/book/the-book-2nd.html) — The free bible of RL; chapters 3–6 cover exactly this territory.
- [Playing Atari with Deep Reinforcement Learning](https://arxiv.org/abs/1312.5602) — The DQN paper; short, and every trick in it is something you'll implement.
- [Spinning Up in Deep RL](https://spinningup.openai.com/en/latest/user/introduction.html) — OpenAI's educational resource: clean theory plus well-documented reference implementations.
- [Gymnasium](https://gymnasium.farama.org/) — The standard RL environment library; your agent's training ground.
- [Q-learning (Wikipedia)](https://en.wikipedia.org/wiki/Q-learning) — Concise reference for the update rule and convergence conditions.
- [David Silver's RL Lectures](https://www.davidsilver.uk/teaching/) — The UCL course videos; the clearest lectures on MDPs and value methods.

## Stretch ideas

- Implement policy-gradient (REINFORCE) on the same environments and compare sample efficiency against Q-learning.
- Build a multi-agent grid world where two Q-learners compete, and observe the emergent strategies.
