from pathlib import Path
import os

import numpy as np


PROJECT_DIR = Path(__file__).resolve().parent
MPL_CACHE_DIR = PROJECT_DIR / ".matplotlib-cache"
XDG_CACHE_DIR = PROJECT_DIR / ".cache"
MPL_CACHE_DIR.mkdir(exist_ok=True)
XDG_CACHE_DIR.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CACHE_DIR))
os.environ.setdefault("XDG_CACHE_HOME", str(XDG_CACHE_DIR))

import matplotlib.pyplot as plt


def normal_pdf(x: np.ndarray, mean: float = 0.0, std: float = 1.0) -> np.ndarray:
    """Analytical probability density function of a normal distribution."""
    z = (x - mean) / std
    return np.exp(-0.5 * z * z) / (std * np.sqrt(2.0 * np.pi))


def metropolis_hastings_normal(
    n_samples: int = 40_000,
    burn_in: int = 5_000,
    proposal_std: float = 1.0,
    random_seed: int = 42,
) -> tuple[np.ndarray, float]:
    """Sample from N(0, 1) with random-walk Metropolis-Hastings."""
    rng = np.random.default_rng(random_seed)
    total_steps = n_samples + burn_in
    samples = np.empty(total_steps)
    current = 0.0
    accepted = 0

    def log_target(value: float) -> float:
        return -0.5 * value * value

    for i in range(total_steps):
        proposal = current + rng.normal(0.0, proposal_std)
        log_accept_ratio = log_target(proposal) - log_target(current)

        if np.log(rng.random()) < log_accept_ratio:
            current = proposal
            accepted += 1

        samples[i] = current

    return samples[burn_in:], accepted / total_steps


def gaussian_kde_manual(samples: np.ndarray, grid: np.ndarray) -> np.ndarray:
    """Estimate density with a simple Gaussian kernel density estimator."""
    n = samples.size
    sample_std = np.std(samples, ddof=1)
    bandwidth = 1.06 * sample_std * n ** (-1.0 / 5.0)

    scaled = (grid[:, None] - samples[None, :]) / bandwidth
    kernels = np.exp(-0.5 * scaled * scaled) / np.sqrt(2.0 * np.pi)
    return kernels.mean(axis=1) / bandwidth


def main() -> None:
    grid = np.linspace(-4.0, 4.0, 500)
    analytical_density = normal_pdf(grid)

    samples, acceptance_rate = metropolis_hastings_normal()
    mcmc_density = gaussian_kde_manual(samples, grid)

    output_path = PROJECT_DIR / "normal_density_mcmc.png"

    plt.figure(figsize=(9, 5.5), dpi=150)
    plt.plot(grid, analytical_density, label="Analytical density: N(0, 1)", linewidth=2.5)
    plt.plot(grid, mcmc_density, label="MCMC estimated density", linewidth=2.0)
    plt.hist(
        samples,
        bins=80,
        density=True,
        alpha=0.18,
        color="tab:orange",
        label="MCMC samples histogram",
    )
    plt.title("Analytical vs MCMC Density for Standard Normal Distribution")
    plt.xlabel("x")
    plt.ylabel("Probability density")
    plt.legend()
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

    print(f"Saved figure: {output_path}")
    print(f"MCMC acceptance rate: {acceptance_rate:.3f}")


if __name__ == "__main__":
    main()
