# MCMC Density Comparison

本文以标准正态分布为例，说明如何分别通过解析概率密度函数和 MCMC 采样估计得到概率密度，并比较两种方法背后的理论关系。

## 目标分布

选择标准正态分布作为目标分布：

$$
X \sim N(0, 1)
$$

其概率密度函数为：

$$
p(x)
= \frac{1}{\sqrt{2\pi}}
\exp\left(-\frac{x^2}{2}\right)
$$

标准正态分布是连续型概率分布中最常见的例子之一。它的解析密度函数已知，因此适合用来检验 MCMC 方法得到的样本是否能正确反映目标分布。

## 解析概率密度

如果概率分布的密度函数可以直接写出，那么可以在任意给定位置 $x$ 上直接计算概率密度：

$$
p(x)
= \frac{1}{\sqrt{2\pi}}
\exp\left(-\frac{x^2}{2}\right)
$$

在一组网格点

$$
x_1, x_2, \ldots, x_m
$$

上分别计算

$$
p(x_1), p(x_2), \ldots, p(x_m)
$$

即可得到标准正态分布的理论概率密度曲线。这条曲线不依赖随机采样，因此可以作为真实密度的参考。

## MCMC 基本思想

MCMC 的目标不是直接写出归一化后的密度函数，而是构造一个马尔可夫链：

$$
X_0, X_1, X_2, \ldots
$$

使得当迭代次数足够多时，马尔可夫链的平稳分布就是目标分布 $\pi(x)$。

对于标准正态分布，目标分布可以写成比例形式：

$$
\pi(x)
\propto
\exp\left(-\frac{x^2}{2}\right)
$$

这里省略了归一化常数 $\frac{1}{\sqrt{2\pi}}$。这是因为 Metropolis-Hastings 算法只需要计算两个状态下目标密度的比值，归一化常数会相互抵消。

## Metropolis-Hastings 算法

本实验使用随机游走 Metropolis-Hastings 方法。设当前状态为 $x_t$，先从提议分布中生成候选状态：

$$
x' = x_t + \epsilon
$$

其中：

$$
\epsilon \sim N(0, \sigma_q^2)
$$

$\sigma_q$ 是提议分布的标准差，用来控制每一步随机移动的尺度。

由于随机游走提议分布是对称的：

$$
q(x' \mid x_t) = q(x_t \mid x')
$$

因此 Metropolis-Hastings 的接受概率可以简化为：

$$
\alpha(x_t, x')
=
\min\left(
1,
\frac{\pi(x')}{\pi(x_t)}
\right)
$$

将标准正态分布的未归一化密度代入，得到：

$$
\alpha(x_t, x')
=
\min\left(
1,
\frac{
\exp\left(-\frac{(x')^2}{2}\right)
}{
\exp\left(-\frac{x_t^2}{2}\right)
}
\right)
$$

也可以写成：

$$
\alpha(x_t, x')
=
\min\left(
1,
\exp\left(
-\frac{(x')^2}{2}
+
\frac{x_t^2}{2}
\right)
\right)
$$

在实际计算中，常使用对数形式：

$$
\log \alpha
=
-\frac{(x')^2}{2}
+
\frac{x_t^2}{2}
$$

这样可以避免指数计算中可能出现的数值下溢问题。

## 接受与拒绝机制

生成候选状态 $x'$ 后，再生成一个均匀随机数：

$$
u \sim U(0, 1)
$$

如果：

$$
u < \alpha(x_t, x')
$$

则接受候选状态：

$$
x_{t+1} = x'
$$

否则拒绝候选状态，并保留原状态：

$$
x_{t+1} = x_t
$$

通过不断重复这一过程，可以得到一组近似服从目标分布的样本。

## Burn-in

马尔可夫链初始状态通常不一定来自目标分布，因此前若干次迭代可能带有较强的初始值影响。

为了减弱这种影响，通常会丢弃前面一部分样本，这一过程称为 burn-in。设总样本序列为：

$$
X_0, X_1, \ldots, X_T
$$

如果丢弃前 $b$ 个样本，则用于估计目标分布的是：

$$
X_b, X_{b+1}, \ldots, X_T
$$

burn-in 的作用是让马尔可夫链有时间逐渐靠近其平稳分布。

## 由 MCMC 样本估计密度

MCMC 直接产生的是样本，而不是显式的概率密度函数。设保留下来的 MCMC 样本为：

$$
x^{(1)}, x^{(2)}, \ldots, x^{(n)}
$$

可以使用核密度估计来从样本中恢复连续密度曲线。Gaussian Kernel Density Estimation 的形式为：

$$
\hat{p}(x)
=
\frac{1}{nh}
\sum_{i=1}^{n}
K\left(
\frac{x - x^{(i)}}{h}
\right)
$$

其中 $h$ 是带宽，$K(\cdot)$ 是核函数。若使用 Gaussian kernel，则：

$$
K(u)
=
\frac{1}{\sqrt{2\pi}}
\exp\left(-\frac{u^2}{2}\right)
$$

带宽控制密度估计的平滑程度。带宽过小会使估计曲线过于抖动，带宽过大会使估计曲线过度平滑。

常用的 Silverman's rule of thumb 给出：

$$
h
=
1.06\hat{\sigma}n^{-1/5}
$$

其中 $\hat{\sigma}$ 是样本标准差，$n$ 是样本数量。

## 理论比较

解析法直接使用已知的概率密度函数：

$$
p(x)
=
\frac{1}{\sqrt{2\pi}}
\exp\left(-\frac{x^2}{2}\right)
$$

因此它给出的是标准正态分布的理论真实密度。

MCMC 方法则通过构造以目标分布为平稳分布的马尔可夫链来生成样本。当样本数量足够大、burn-in 足够充分、提议分布尺度合适时，样本的经验分布会逐渐接近目标分布：

$$
x^{(i)} \sim \pi(x)
$$

再通过核密度估计得到：

$$
\hat{p}(x) \approx p(x)
$$

因此，在标准正态分布这个例子中，MCMC 得到的密度估计曲线应当接近解析概率密度曲线。两者越接近，说明 MCMC 样本越好地反映了目标分布。
