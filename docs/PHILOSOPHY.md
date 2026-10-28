# Philosophy of Agent Setup

[README](../README.md) | **English** | [한국어](PHILOSOPHY.ko.md)

A minimalist AI workflow focused on probabilistic distributions and concrete resource constraints.

## AI Coding Is a Casino Where the Developer Holds the House Edge

> By this, I mean positive statistical expectation, not gambling.

AI coding workflows are not deterministic programs; they are priors designed to shape a probability bell curve so the law of large numbers yields a house edge. `SKILL.md` and `AGENTS.md` exist to shift this distribution.

- **Prefer many small runs over one large execution.**
  A single high-stakes run (massive token load and broad scope) is fragile. Multiple small-stakes runs (tight token budgets and rapid iterations) reliably secure favorable outcomes. The goal is stabilizing advantageous distributions through smaller sample spaces.
- **Do not enforce branching trees or rigid procedures.**
  Overfitting procedures to edge cases turns them into superstitious rituals. Like a blackjack dealer executing the core loop of dealing cards and taking chips, instructions should guide only essential invariants.
- **Avoid few-shot examples.**
  Fixed few-shot examples overfit and become losing betting strategies when contexts shift.
- **Realizing the house edge requires instant settlement.**
  Manual code review carries heavy verification costs. Strict typecheckers (`tsc`, `rustc`) and unit tests act as deterministic settlement engines to instantly fold bad hands or collect winnings. Faster settlement increases iteration throughput, putting the law of large numbers on your side.

## Everything Is Governed by Resource Constraints and Reality

Bloated frameworks that ignore the physical constraints of stochastic models (context window limits, attention degradation) and human cognitive load become pure overhead. Agent Setup avoids managing every exception, specifying only essential invariants.

- **Do not squander attention and context windows on meta-instructions.**
  Keep context free of verbose tool manuals and multi-agent trace logs. Focus the model's attention on raw source code and compiler errors.
- **Define domain logic through minimal invariants, not procedural frameworks.**
  Replace elaborate state machines with unbreakable core constraints to preserve the model's native Chain-of-Thought (`CoT`) reasoning.

## Workflows Must Be Replaceable as Better Methods Emerge

No agent configuration is permanent. Agent Setup keeps coupling minimal and scopes tight so skills and agent instructions can be swapped as superior approaches arise.

- **Keep all agent documents under ~200 lines and minimize file count.**
  Tightly coupled documents increase cognitive load and resist refactoring. Every document must remain independently addable, editable, and disposable.
- **Validate experiments through standalone skills.**
  Test ideas as isolated, minimal skills driven by real needs. Fold proven skills into `AGENTS.md` and ruthlessly discard what fails.
