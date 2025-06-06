import os
import re
import sys

# ──────────────────────────────────────────────────────────────────────────────
# MDP parameters
# ──────────────────────────────────────────────────────────────────────────────
GAMMA          = 0.97
THRESHOLD      = 1e-6
ACTION_PENALTY = -0.05


# ──────────────────────────────────────────────────────────────────────────────
# 1) PARSE HTML CORPUS
# ──────────────────────────────────────────────────────────────────────────────
def crawl_mdp(directory):
    """
    Parse HTML files in *directory* to extract
      • pages                       – set[str] of filenames
      • links[page]                 – set[str] of outgoing links
      • terminal_reward[page]       – float reward (or None if not terminal)
    """
    pages, links, terminal_reward = set(), {}, {}

    for fn in os.listdir(directory):
        if fn.endswith(".html"):
            pages.add(fn)

    for fn in pages:
        text = open(os.path.join(directory, fn), encoding="utf-8").read()

        # Outgoing <a href="…">
        out = set(re.findall(r'<a[^>]+href="([^"#]+)"', text))
        links[fn] = {l for l in out if l in pages}

        # Optional reward tag
        pattern = r'<meta\s+name="reward"\s+content="([-0-9.]+)"'
        m = re.search(pattern, text)
        terminal_reward[fn] = float(m.group(1)) if m else None

    return pages, links, terminal_reward


# ──────────────────────────────────────────────────────────────────────────────
# 2) BUILD TRANSITION / REWARD
# ──────────────────────────────────────────────────────────────────────────────
def build_mdp(pages, links, terminal_reward):
    P, R, actions = {}, {}, {}

    for s in pages:
        P[s], R[s], actions[s] = {}, {}, []
        out = links[s]

        # Terminal page
        if terminal_reward[s] is not None:
            actions[s].append(None)
            P[s][None] = {s: 1.0}
            R[s][None] = {s: 0.0}
            continue

        # Dead-end non-terminal
        if not out:
            actions[s].append(None)
            P[s][None] = {s: 1.0}
            R[s][None] = {s: 0.0}
            continue

        # Regular page
        for a in out:
            actions[s].append(a)

            dist = {}
            others = list(out - {a})
            if len(out) == 1:
                dist[a], dist[s] = 0.90, 0.10
            else:
                dist[a], dist[s] = 0.60, 0.10
                share = 0.30 / len(others)
                for s2 in others:
                    dist[s2] = share
            P[s][a] = dist

            R[s][a] = {s2: ACTION_PENALTY for s2 in dist}

    return P, R, actions


# ──────────────────────────────────────────────────────────────────────────────
# 3) *** TODO – VALUE ITERATION ***
# ──────────────────────────────────────────────────────────────────────────────
def value_iteration(pages, P, R, actions, terminal_reward,
                    gamma=GAMMA, theta=THRESHOLD):
    """
    Implement value-iteration. 

    Parameters
    ----------
    pages, P, R, actions, terminal_reward – data structures from build_mdp.
    gamma – discount factor.
    theta – convergence threshold.

    Returns
    -------
    V       – dict mapping state → value.
    policy  – dict mapping state → best action (None for terminal states).
    """
    raise NotImplementedError(">>> TODO: implement value_iteration() <<<")


# ──────────────────────────────────────────────────────────────────────────────
# 4) DRIVER
# ──────────────────────────────────────────────────────────────────────────────
def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python MDP_Project.py <corpus_directory>")

    corpus_dir = sys.argv[1]
    pages, links, terminal_reward = crawl_mdp(corpus_dir)
    P, R, actions = build_mdp(pages, links, terminal_reward)

    V, policy = value_iteration(pages, P, R, actions, terminal_reward)

    print("State Values (V):")
    for s in sorted(V):
        print(f"  {s:20s} : {V[s]:.6f}")

    print("\nGreedy Optimal Policy (click this link in each state):")
    for s in sorted(policy):
        act = policy[s] or "—"  # None
        print(f"  at {s:20s} ‍→ {act}")


if __name__ == "__main__":
    main()
