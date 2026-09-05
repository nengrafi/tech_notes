---
title: Towards Evaluating the Robustnessof Neural Networks
field: AI_Security
category: Adversarial ML
status: First Pass
---

# Abstract

nn은 대부분의 머신러닝 task에서 SOTA를 제공하지만 adversarial examples에 취약하다. 이 때문에 security-critical 영역에서 nn의 적용이 어렵다.

이 논문에서는 distilled, undistilled 모두에 대해 성공하는 세가지 새로운 attack algorithm을 도입하여 defensive distillation이 robustness를 유의미하게 높이지 못함을 보인다. attacks는 기존 연구에서 사용된 세가지 distance metric(input x와 adversarial example 비교)에 맞게 설계 되었으며 더욱 효과적이다. 또한 다른 모델에서 test할때 high-confidence adversarial examples를 사용하면 defensive distillation도 무력화할 수 있습니다.

# Introduction

Adverdarial examples로 부터 NN을 안전하게 만들기 위한 초기의 시도는 대부분 실패하였다. Defensive distillation은 nn을 강화하기 위해 제안된 defense 방법으로 초기에는 굉장히 유망하였다. 실제로 임의의 feed-forward neural network에 적용 가능하고 한번의 re-training만 필요하며 성공확률을 95% → 0.5%로 낮춘다.

일반적으로 nn의 robustness를 평가하는데 두가지 접근법이 있다.  
input x에 대해서 adversarial example까지의 거리가 클 수록 모델이 robust하다.

1. lower bound를 증명, lower bound 이내에는 adversarial example 존재 X  
    증명시에 확실하지만 구현하기가 어렵고 approximation을 필요로함
2. upper bound를 입증하는 attack 구성, 최소 distance가 그보다 클수 없다.  
    attack이 충분히 강하지 않아 자주 실패한다면 유용하지 않다.

이 논문에서는 upper bound를 위한 attacks 집합을 만든다. 이를 이용해 defensive distillation이 adversarial examples를 제거하지 못함을 보인다. 이때 세가지 attacks를 구성하고 이때 defensively distilled networks에서 이미지의 100%를 찾는데 성공하였다. distillation은 당시 SOTA attacks에 대해서 안전하였지만 이 연구의 attacks에는 실패한다. 또한 이 논문의 attacks는 더 적은 왜곡으로 examples를 생성한다. 따라서 defense를 평가하기에 더욱 낫다.

또한 robustness 평가를 위해 high-confidence adversarial examples를 사용해야 한다. 이 논문의 adversarial examples가 보안이 적용되지 않은 model에서 defensively distilled model로 transfer 가능함이 보여진다. 따라서 모든 defense는 transferability 특성을 무력화할 수 있음을 입증해야한다.

이 논문은 MNIST, CIFAR-10, ImageNet를 사용하여 attacks를 평가한다.

- $L_2,\ L_\infty,\ L_0$ distance metric를 이용한 새로운 attack를 소개한다.  
    이는 기존의 접그넙보다 효율적이며 특히 $L_0$ attack은 ImageNet의 targeted 오분류를 유발할 수 있는 최초의 attack이다.
- 이러한 attacks를 defensive distillation에 적용하여 distillation이 보안적 이점을 거의 제공하지 못한다는 사실을 밝힌다.
- defense 평가를 위해 transferability test에서 high-confidence adversarial examples를 사용할것을 제안한다.
- adversarial examples를 찾기 위한 objective function을 평가하고 그 선택이 attack의 효과에 영향을 미칠 수 있음을 보인다.

# BackGround

## Threat Model

nn이 다양한 분야에서 사용되며 보안 역시 중요해졌다

Speech recognition

- 알고리즘에는 음성처럼 들리지만 사람에게는 들리지 않는 audio가 생성 가능하다.

maleware classification

- 적용환경 제한및 목적 자체 무력화

→ 어느정도의 distortion을 추가해야 하는가  
분야에 따라 사용하는 distance metric이 다름  
이미지는 $L_p$norm 사용

white-box setting: 공격자가 내부 모델 구조를 다 알고 있는 상황을 가정  
기존 연구에서 black-box일때 transfer을 통해 target model 변경

## Neural Networks and Notation

이 논문에서는 m-class classifier nn에 초점을 맞춘다.  
Activation function은 ReLU를 사용하고 image classification을 평가 분야로 삼는다.

## Adversarial Examples

targeted adversarial example : target t가 되도록 유사한 입력 $x'$를 찾는다.

- Average Case : 올바르지 않은 label중에서 target class를 균일하게 무작위선택
- Best Case : 모든 잘못된 class를 Attack하고 가장 쉬웠던 target class 보고
- Worst Case : 모든 잘못된 class를 Attack하고 가장 어려웠던 target class 보고

ImageNet에서 효율성을 위해 1000개의 target class중 100개를 sampling하여 best-case, worst-case attack을 근사한다

## Distance Metrics

Adversarial examples에서 유사도를 정량화하기 위해서 사용된다.  
널리 사용되는 것으로 3가지가 있으며 모두 $L_p$norm이다.

$$  
\left\lVert x - x' \right\rVert_p\\  
\lVert v\rVert_p=\left(\sum_{i=1}^{n}\lvert v_i\rvert^p\right)^{\frac{1}{p}}

$$

$L_0$: $x_i \neq x'_i$인 좌표의 개수를 측정한다.

$L_2:$ 표준 Euclidean distance. 많은 픽셀에 작은 변화가 많이 발생해도 작게 유지

$𝐿_∞$: 임이의 좌표에 발생하는 최대 변화 측정

$$  
\left\lVert x-x' \right\rVert_\infty=\max\left(\left|x_1-x'_1\right|,\ldots,\left|x_n-x'_n\right|\right)  
$$

적절한 distance metric을 구성하고 평가하는 것도 연구문제이다  
수치보고 시에는 distance metric을 scaling 해서 [0,1]에서 사용한다.

## Defensive Distillation

network가 2개 존재한다. 1번째 network에서는 standard 방식으로 train하되 softmax 계산시에 temperature T를 나눠서 smooth하게 만든다. 이후 train이 끝나면 training instance를 평가하고 ouput label을 통해 soft training label을 만든다. 2번째 network에서는 soft label을 이용해서 train하여 1번째 model이 학습한 hidden knowledge를 전달한다.

이를 통해서 adversarial perturbation에 덜 민감해진다. 이때 학습과정에서는 T를 크게하여 logit의 차이를 증가시키고 추론과정에서는 T=1로 학습하는데 이때 $\frac{\partial p}{\partial z} \approx 0$가 되므로 chain rule에 따라 perturbation이 들어가도 softmax probability가 거의 안 움직인다. 따라서 공격자 입장에서 attack 방향을 찾기 쉽지않다. 하지만 logit gap이 크다는 것 만으로는 robustness를 보장할 수 없다.

# Attack Algorithms

## L-BFGS

여기서 loss함수는 cross-entropy

$$  
\begin{aligned}&\text{minimize} && c \cdot \left\lVert x-x' \right\rVert_2^2 + \operatorname{loss}_{F,l}(x') \\&\text{such that} && x' \in [0,1]^n\end{aligned}  
$$

## Fast Gradient Sign

$𝐿_∞$에 맞게 optimize되며 가까운 adversarial example보다는 빠르기에 초점이 맞춰져있다. 따라서 최소 adversarial perturbation을 생성하지는 않는다.

$$  
x' = x - \epsilon \cdot \operatorname{sign}\left(\nabla \operatorname{loss}_{F,t}(x)\right)  
$$

Iterative Gradient Sign: 단일 step 대신 더 작은 $α$ 크기의 step을 여러번 수행하고 그 결과를 동일하게 clipping한다.

$$  
x'_i = x'_{i-1} - \operatorname{clip}_{\epsilon}\left(\alpha \cdot \operatorname{sign}\left(\nabla \operatorname{loss}_{F,t}\left(x'_{i-1}\right)\right)\right)  
$$

## JSMA

$L_0$에 맞게 optimize되어서 수정할 픽셀을 최소화한다.  
한번에 수정할 픽셀을 하나씩 선택하고 각 iteration에서 target classification을 높이는 greedy algorithm이다. $∇𝑍(𝑥)_l$을 사용하여 픽셀을 바꿨을때 target logit이 얼마나 변하는지 계산하고 이를 통해 saliency map을 modeling합니다.  
saliency map에서 가장 커지는 픽셀을 선택하는 과정은 threshold를 초과하도록 반복되어 attack이 감지되거나 classfication이 변경되면 끝난다.

![[Pasted image 20260906050857.png]]

이때 p,q 두개를 선택하는데 $\alpha$는 p,q를 바꿀때 t의 logit이 얼마나 변하는가를 나타내고 $\beta$는 p,q를 바꿀때 t를 제외한 나머지 class들의 score의 크기를 의미한다.

$$
\begin{aligned}
\alpha_{pq}
&= \sum_{i \in \{p,q\}}
\frac{\partial Z(x)_t}{\partial x_i} \\

\beta_{pq}
&=
\left(
\sum_{i \in \{p,q\}}
\sum_j
\frac{\partial Z(x)_j}{\partial x_i}
\right)
-
\alpha_{pq}
\end{aligned}
$$

$$
(p^*, q^*)
=
\arg\max_{(p,q)}
\left[
-\alpha_{pq}\beta_{pq}
\cdot
\mathbf{1}(\alpha_{pq} > 0)
\cdot
\mathbf{1}(\beta_{pq} < 0)
\right]
$$

실제로 softmax의 출력인 F를 사용하지 않지만 (JSMA-Z attack) 이 논문에서는 F를 대신 사용하도록 attack을 수정한다.

## Deepfool

$L_2$에 맞게 최적화된 untargeted attack이다. 효율적이고 L-BFGS보다 더 가까운 adversarial example을 생성한다. 이때 class끼리 hyperplane은 분리되어 있고 nn이 완전히 linear하다고 가정한다. 이를 바탕으로 단순화된 문제의 optimal soultion을 해석적으로 도출한다.

그 다음 해당 solution을 향해 한단계 이동하고 이 과정을 반복한다. 실제 adversarial example을 발견하면 탐색 종료한다.

# Experimental Setup

![[Pasted image 20260906051001.png]]

MNIST와 CIFAR model architecture

![[Pasted image 20260906051006.png]]

MNIST와 CIFAR model parameter

둘 모두 기존 defensive distillation 연구와 동일하다.  
MNIST, CIFAR-10 분류를 위해 두개의 network를 사용하고 ImageNet 분류에는 pre-trained된 하나의 network를 사용한다.  
MNIST에서는 99.5%의 정확도를 달성하고 CIFAR-10에서는 80%의 정확도를 달성하는데 이는 distillation 연구와 동일하다. 또한 training중에는 SGD optimizer를 사용한다.

CIFAR-10: dropout를 사용했음에도 상당히 overfitting한다. 최종 cross-entropy loss는 0.05이고 정확도는 98프로이고 validation loss는 1.2이고 validation 정확도는 80프로이다. 하지만 기존 연구와의 비교를 위해서 추가적인 tuning은 하지 않았다.

ImageNet: 이미 pre-trained 된 Inception v3 network를 사용하며 top-5 정확도 96%를 기록한다. 또한 이미지를 299x299x3의 vector로 입력받는다.

# Our Approach

$$  
\begin{aligned}&\text{minimize} && D(x, x+\delta) \\&\text{such that} && C(x+\delta)=t \\& && x+\delta \in [0,1]^n\end{aligned}  
$$

## Objective Function

$C(x+\delta)=t$는 매우 non-linear 하기 때문에 기존 algorithm으로 해결하기 어렵다. 따라서 optimization에 적합한 형태로 표현한다. f라는 objective function을 정의하여, $C(x+\delta)=t$인 경우에만 $𝑓(𝑥 + 𝛿) ≤ 0$가 성립하도록 한다.

$$  
\begin{aligned}f_1(x') &= -\operatorname{loss}_{F,t}(x') + 1 \\  
f_2(x') &= \left(\max\left(F(x')_i - F(x')_t\right)\right)^+_{i \ne t} \\  
f_3(x') &= \operatorname{softplus}\left(\max\left(F(x')_i\right)_{i \ne t} - F(x')_t\right) - \log(2) \\  
f_4(x') &= \left(0.5 - F(x')_t\right)^+ \\  
f_5(x') &= -\log\left(2F(x')_t - 2\right) \\  
f_6(x') &= \left(\max\left(Z(x')_i - Z(x')_t\right)\right)^+_{i \ne t} \\  
f_7(x') &= \operatorname{softplus}\left(\max\left(Z(x')_i\right)_{i \ne t} - Z(x')_t\right) - \log(2)\end{aligned}  
$$

$$  
\begin{aligned}&\text{minimize} && D(x, x+\delta) + c \cdot f(x+\delta) \\&\text{such that} && x+\delta \in [0,1]^n\end{aligned}  
$$

결과적으로 조건에 맞는 가장작은 c를 선택하는 것이 가장 좋은 방법인 경우가 많다.

## Box constraints

이미지 수정 결과가 유효하기 위해서 $δ$에 제약을 둔다. $0 ≤ 𝑥_𝑖 +  
𝛿_𝑖 ≤ 1$이여야한다. 이때 box constraint를 지원하는 L-BFGS-B를 사용한다.

1. Projected Gradient Descent  
    gradient descent를 계산하고 범위를 벗어나면 다시 clipping한다. 즉 update한 변수 자체를 clip한다.  
    이때 momentum 방식은 이전의 움직임을 기억하기 때문에 clipping 했을때 다음 iteration에 입력되는 값이 의도치 않게 변경되어 제대로 작동하지 않을 수 있다.
2. Clipped gradient descent  
    $𝑓(𝑥 + 𝛿)$를 $𝑓(min(max(𝑥 + 𝛿, 0), 1))$ 로 대체하여 objective function에 clipping을 포함한다. 즉 loss를 계산할때 network에 전달되는 값만 clip한다.  
    PGD의 주요 문제를 해결하지만 gradient가 평평한 영역에 갇힐 수 있다.
3. Change of variables  
    새로운 변수 w를 도입해 $δ$대신 w에 대해서 optimization한다.

$$  
\delta_i = \frac{1}{2}\left(\tanh(w_i)+1\right)-x_i  
$$

이때 $−1 ≤ tanh(𝑤_𝑖  
) ≤ 1$ 이므로 boxing이 성립한다.  
이를 통해서 평평한 영역에 같히는 문제를 제거한다. 또한 box constraint를 지원하지 않는 다른 optimization algorithm도 사용할 수 있다.

## Evalution of approachs

![[Pasted image 20260906051016.png]]

7개의 objective function중 하나와 세가지 box constraint encoding중 하나를 조합하는 경우의 수를 평가한다. 1000개의 무작위 instance에서 평가하였다.  
mean = 평균 L2 왜곡, prob = success probability

최적의 c를 선택하기 위해서 binary search를 20회 수행한다. 선택된 c에 대해서는 Adam optimizer를 사용한 gradient descent를 10,000 iteration 실행한다.

![[Pasted image 20260906051021.png]]

최고의 objective function과 최악의 objective function 사이에 품질 측면에는 3배의 차이가 있었다. 따라서 objective function의 선택이 중요하다.  
c=0이면 graident descent는 초기 이미지를 벗어나지 않지만 c가 크면 초기 step이 지나치게 greedy하게 수행되는 결과가 많고 D-Loss를 무시하려고 한다. 그 결과 최적이 아닌 해를 찾게 된다.

f1, f4는 D와 f의 변화 폭이 너무 커서 최적의 constant c가 동일하게 유지되지 않는다. linear interpolation을 통해 x와 x’사이의 중간이미지들을 만들때 logit는 linear하며 F는 logistic임을 알 수 있다.

MNIST와 CIFAR-10의 첫번째 test image 1000개에서 person correlation r(linear relationship이 얼마나 강한지)> 0.9였고 이를 통해 logit이 꽤 linear하게 움직임을 알 수 있다.

$$  
\epsilon < c\left(f_1(x+\epsilon)-f_1(x)\right)\\  
\epsilon \to 0\\

\frac{1}{c} < \left|\nabla f_1(x)\right|  
$$

$f_4,f_1$에서 c가 충분히 크지 않으면 변화를 일으키지 않는다. distance에 비해서 더 크게 작아지지 못하기 때문이다.

$f_1$의 경우에 gradient는 F()와 동일함으로 초기에는 매우 작다. 따라서 c가 매우 커야한다. 이후에 graident가 exponential rate로 증가하여 c가 매우 크다면 지나치게 greedy 해진다.

10^-10에서 10_10까지 constant를 사용해서 attack 수행시에 $f_4$에서 평균 constant가 10^6이 나왔다. $f_1$의 평균 gradient가 2^-20이지만 2^-1까지 커지는데 이를 통해 c가 필요 이상으로 커지게 되기 때문에 성능이 저하된다.

## Discretization

[0,1]에서 discrete integer [0,255]로 변환할때 optimize시에는 그대로 두다가 마지막에 변환한다. 이로 인해 adversarial example의 품질이 약간 저하된다. attack 품질을 복원하기 위해서 discrete로 정의된 lattice에서 greedy search를 수행하여 하나씩 픽셀을 바꾸며 품질을 높인다.

이 논문은 기존 FGSA보다 훨씬 작은 변화를 가하므로 discretization도 신경써야한다.

# Three Attacks

## $L_2$

distortion이 낮은 adversarial examples를 찾는 방법을 얻을 수 있다.

이때 f는 앞에서 구했던 최고의 object function $f_6$을 사용한다. k를 통해 misclassification의 confidence를 제어한다. 또한 change of variables를 이용한다.

$$
\begin{aligned}
\text{minimize}\quad
&
\left\|
\frac{1}{2}\left(\tanh(w)+1\right)-x
\right\|_2^2
+
c \cdot
f\left(
\frac{1}{2}\left(\tanh(w)+1\right)
\right)
\\[6pt]
\text{where}\quad
&
f(x')
=
\max\left(
\max_{i \ne t}
\left\{
Z(x')_i
\right\}
-
Z(x')_t,
-\kappa
\right)
\end{aligned}
$$

Multiple starting-point gradient descent  
gradient descent의 주요 문제는 greedy search가 최적해를 찾는다는 보장이 없는것이다. 이것을 해결하기 위해서 원본이미지에 가까운 여러개의 random starting point를 선택하고 각 point에서 정해진 횟수만큼 gradient descent를 수행한다. 이때 가장 가까운 adversarial example이 r이고 반지름이 r인 ball로 sampling한다. 이를통해 local minimum을 완화한다.

## $L_0$

미분 불가능하므로 gradient descent에 적합하지 않지만 각 iteration에서 classifier output에 큰 영향을 미치지 않는 일부 pixel을 구별하고 그 pixel을 고정하여 그 값이 더는 변경되지 않도록 한다. 고정된 집합은 각 iteration에서 증가하며 최종적으로는 이 소거 과정을 통해 adversarial example을 생성하기 위해 변경할 수 있는 최소한의 pixel subset를 식별한다. 이때 $L_2$ attack을 통해 중요하지 않은 pixel을 식별한다.

L2 attack → adversarial example 성공 → pixel의  $g_i δ_i$계산 → 가장 불필요한 pixel i 제거  
를 반복한다. 그리고 attack이 실패하면 정지한다.

$$  
i = \arg\min_i \; g_i \cdot \delta_i  
$$

이때 $L_2$에서 사용할 constant c가 필요하다. 이를 위해 c를 매우 작은값 10^-4로 설정하고 이 값에서 adversary를 실행한다. 이후 성공할때까지 값을 2배 늘려서 다시 시도한다. 이때 c가 고정된 threshold를 넘기면 탐색을 중단한다.

JSMA는 변경가능한 piexel set를 확장하는 구조이다. 하지만 초반에 잘못된 선택을 하면 탐색에 불리해지기 때문에 $L_0$가 유리하다. 그리고 $\delta^{(k)}$를 다음 k+1의 새로운 starting point로 쓰기때문에 속도가 빠르다.

## $𝐿_∞$

역시 완전 미분가능하지 않기에 (i=j) gradient descent도 이 metric에서 성능을 내지 못한다.  
gradient descent에서 두개의 solution사이에서 발산하는 상태에 빠진다. i가 j보다 클때는 i의 descent가 1 j의 descent가 0이므로 i가 계속 작아지다가 i가 j보다 작아지면 반대 상황이 되기 때문이다.

$$  
\text{minimize}\quad c \cdot f(x+\delta) + \lVert \delta \rVert_{\infty}  
$$

이를 iterative attack을 사용해서 해결한다. 현재 허용하고 싶은 최대 perturbation $τ$의 크기를 정하고 패널티를 부여한다. 이를 통해 하나의 perturbation을 변경하는게 아닌 큰 perturbation을 한번에 변경하여서 계속 switching 되는 문제를 줄인다.

$$  
\text{minimize}\quad c \cdot f(x+\delta) + \sum_i \left[(\delta_i-\tau)^+\right]  
$$

$τ=1$로 시작하여서 성립하면 0.9배씩 줄이기를 반복한다.

이때 적절한 상수 c가 필요한데 $L_0$과 같은 접근법을 사용한다. 먼저 c를 매우 작은값으로 설정하고 $𝐿_∞$를 실행한 후에 성공하면 2배씩 늘린다. 또한 warm-start를 사용하면 $L_2$와 동일한 속도로 동작한다.

# Attack Evaluation

세가지 distance metric를 각각에 대해 가장 우수한 결과와 비교한다.

Deepfood, fast gradient sign, iterative gradient sign을 다시 구현한다. JSMA는 CleverHans를 약간 수정하여 사용한다. JSMA는 본질적으로 큰 computational cost가 발생하기 때문에 ImageNet에서 실행할 수 없다. 이는 pixel pair 서치를 하므로 큰 차원의 ImageNet에서 계산량이 매우 많아지기 때문이다.

CIFAR과 MNIST에서 처음 train set 1000개를 가지고 평가한다. ImageNet에서는 무작위의 1000개를 사용한다. 또한 100개의 target class를 랜덤으로 선택하여 best-case 및 worst-case를 근사한다.

$L_0,L_2$는 2 ~ 10X 낮은 adversarial example을 찾으며 무조건 성공한다. $𝐿_∞$는 success rate가 기존보다 높다.

기존에는 model의 복잡성으로 인해 더 learning task가 복잡해질수록 더욱 나쁜 결과를 생성했지만 이 논문의 attack은 복잡해질수록 더욱 나은 성능을 보인다. JSMA를 이용하면 ImageNet에서 $L_0$ adeversarial example을 찾지 못했지만 우리는 무조건적으로 찾았다.

이때 dataset이 다르면 row값만 보고 attack difficulty를 비교하면 안된다.

![[Pasted image 20260906051105.png]]
Synthetic digit generation  
숫자가 없는 이미지에서 시작한다.  
이 실험은 이전에 $L_0$에 대해 실행되었지만 몇몇 class는 인식이 가능했다. 하지만 이 실험에서는 인식이 불가능하다. 또한 처음에 1로 분류되므로 1은 변화가 필요하지 않다.

실행시간 분석

- 실제 attack을 수행하기에 performace가 지나치게 높은지 확인
- inner loop를 사용하기 위해서

![[Pasted image 20260906051114.png]]

![[Pasted image 20260906051117.png]]

attack의 정확한 runtime을 비교하는건 맞지 않기 떄문에 제시하지 않는다.  
JSMA와 비교했을때 $L_0$는 대략 2~10배 느리고 $L_2​,L_∞​$는 10~100배 느리다.

# Evaluating Defensive Distillation

처음에는 대규모 model을 더 작인 distilled model로 축소하기 위한 접근법이었다.

Defensive distillation은 변경점이 2가지 존재한다

1. teacher model과 distilled model의 크기가 동일하다.
2. defensive distillation이 큰 temperature을 사용하여 더 높은 예측에 더 큰 confidence를 가지도록 한다.  
    temperature를 높이면 부드러운 maximum이 생성된다. 그리고 0으로 갈수록 one-hot distribution에 가까워진다. 반대로 infinity로 갈수록 uniform distribution에 가까워진다.

$$  
\operatorname{softmax}(x,T)_i=\frac{e^{x_i/T}}{\sum_j e^{x_j/T}}  
$$

1. training 단계에서 softmax의 temperature를 T로 설정해 teacher network를 training한다.
2. training set의 각 instance에 teacher network를 적용하고 soft labels를 계산한다.
3. temperature T와 soft labels로 distilled network를 training한다.
4. test time에 distilled network를 실행하여 temperature을 1로 input을 분류한다.

## Fragility of existing attacks

기존 attack은 취약하여 Adversarial examples를 찾지 못했다. L-BFGS와 Deepfool은 F()의 gradinet가 항상 0이기 때문에 실패하여 standard objective function을 사용할 수 없다.

temperature T로 학습하고 1로 test한다. training 중 cross entropy를 최소화하면 정답 class는 1에 가깝게 다른 class는 0에 가깝게 강제되는데 temperature T인 경우에 1인 경우보다는 Z()가 T배 커지도록 학습된다. 실험적으로도 undistilled network

- norm : 5.8, standard deviation : 6.4  
    distilled network
- norm : 482, standard deviation : 457

즉 temperature 1에서 test하면 정답 class외의 나머지는 $ϵ$가 된다. 이떄 gradient도 매우 작아져서 0이 된다.

이때문에 L-BFGS는 종료되지만 stable objective function이나 objective function loss(temperature)를 사용하지 않으면 실패하지 않는다.

$$  
F'(x) = \operatorname{softmax}\left(\frac{Z(x)}{T}\right)  
$$

JSMA-F도 같은 이유로 실패한다.

JSMA-Z는 완전히 다른 이유로 실패한다. logit 변화량 자체만 보고 중요도를 판단하지만 logit의 변화량이 softmax의 변화량을 보장하지 않는다. 하지만 undistilled network에서는 극단적이지 않으므로 동작한다.

Fast Gradient Sign도 L-BFGS와 같은 이유로 실패한다. 그러나 동일한 division trick을 적용해서 softmax function 입력전에 logits를 T로 나누면 distillation이 여전히 효과적이다. 이 논문에서는 이 이유를 설명할 수 없다.

## Applying Our Attacks

모델에 attack을 적용한 결과 distillation이 제공하는 이점은 marginal한 수준이었다.

## Effect of Temperature

기존 연구에서는 temperature을 높이면 attack 성공률이 일관되게 감소하는 것으로 보였다.

![[Pasted image 20260906051125.png]]

![[Pasted image 20260906051128.png]]

temperature에 의한 robustness를 이해하기 위해 개선된 attack을 이용하여 t= 1부터 t=100까지 변화시키며 model을 학습했다. 이떄 평균거리에는 영향을 미치지 않고 상관계수가 -0.05로 나왔기 때문에 robustness가 실질적으로 향상되지 않음을 알수 있다.

## Transferability

한 model에 대한 adversarial example이 서로 다른 model에 대해 transfer된다. 따라서 robustness를 제공할 수 있는 defense는 이런 transferability 특성을 깨야한다. 따라서 standard model에서 defensive distillation model로 transfer함으로서 무력화된다.

이를 위해 high-confidence adversarial example을 가진다. k가 클수록 classification이 강해지므로 강한 confidence를 얻는다.

MNIST에서 training한 두 model을 사용하고 가 model은 training data의 절반으로 training했다.

![[Pasted image 20260906051134.png]]

$$  
f(x') = \max\left(\max_{i \ne t}\left\{Z(x')_i\right\} - Z(x')_t,\ -\kappa\right)  
$$

![[Pasted image 20260906051139.png]]

# Experiments

## Figure

### Figure 1.

![[Pasted image 20260906051143.png]]

Defensive distillation을 적용한 network에 대한 이 연구의 attack를 보여줌  
Adversarial은 각각 $L_2,\ L_\infty,\ L_0$를 활용하여서 제작되었다. 공격 이후에 셋 모두 동일한 오분류 l+1(mod 10)의 label를 가졌다.

### Figure 2.

![[Pasted image 20260906051147.png]]

f6을 사용하고 c가 0.01부터 100까지 log scale로 값을 바꿔가며 graident descent로 adversarial example을 만든다.  
c < 0.1일때 너무 작기 때문에 $δ≈0$이 된다. c > 1이 되면 성공 확률은 1이 되지만 perturbation은 쓸데 없이 커진다.

### Figure 3. 4.

![[Pasted image 20260906051150.png]]

$L_2$보다 $L_0$가 어려움을 알 수 있다.

# CONCLUSION

Adversarial example에 대해 robust한 defense를 구축하는 것은 아직 해결되지 않은 문제이다. 이를 해결하기 위해 defensive distillation이 제안되었지만 이 논문에서는 이를 무력화하는 강력한 attack을 제안하고 더 나아가 이 attack이 defense의 효능을 평가하는데 사용될 수 있음을 보였다.

가능한 여러 attack 접근법을 체계적으로 평가하고. 이 평가를 바탕으로 세 가지 $𝐿_0 , 𝐿_2 , 𝐿_∞$ attack을 사용한다.

defense를 개발하는 연구자들이 논문에 두가지 평가 접근법을 수행할 것을 권장한다.

1. 강력한 attack를 활용해 robustness를 직접 평가한다. 특히 이 논문의 $L_2$를 확립해야한다.
2. 모델의 transferability가 실패한다는걸 입증해야한다.