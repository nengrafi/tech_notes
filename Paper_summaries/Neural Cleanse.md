---
title: "Neural Cleanse: Identifying and Mitigating  Backdoor Attacks in Neural Networks"
field: AI_Security
category: Backdoor
status: First Pass
---
## Summary

이미 학습된 DNN 모델을 Neural Cleanse을 이용해서 backdoor를 감지하고 효과를 완화한다.
## Problem Statement

nn이 발전하면서 backdoor에 대한 공격에 노출되어 있지만 backdoor가 있는지 감지하기 어렵다. 
또한 original training data가 없어서 재학습이 불가능하거나 특정 teacher model이나 특수한 task 때문에 기존 model을 계속 사용해야 할수도 있다. 따라서 backdoor을 완화할 방법이 필요하다.
## Motivation & Intuition

![](../assets/Pasted%20image%2020260918002049.png)
Backdoor trigger는 target label로 가는 shortcut을 만든다. 따라서 모든 input을 target label로 변화시키는 데 필요한 최소 perturbation이 다른 label보다 비정상적으로 작다.
## Key Idea

1. Backdoor의 target label을 감지한다
2. Backdoor의 trigger을 reverse engineering으로 찾아낸다.
3. filter을 적용하거나 neuran을 pruning하여서 backdoor을 약화시킨다.
## Method

mask값 $m$과 perturbation 값$\Delta$를 cross-entropy loss function을 이용해서 최적화한다. 
$$
A(x,m,\Delta)=x', \qquad
x'_{i,j,c}=(1-m_{i,j})\cdot x_{i,j,c}+m_{i,j}\cdot\Delta_{i,j,c}
$$
$$
\min_{m,\Delta}
\ell\left(y_t, f(A(x,m,\Delta))\right)
+
\lambda \cdot |m|
\qquad
\text{for } x \in X
$$
- $m$ : 얼마나 trigger로 덮을지 정하는 mask
- $\Delta$ : trigger의 pixel pattern
- $|m|$ : trigger의 norm 크기

각 label을 target label로 가정해서 최소 trigger을 찾고 mask의 norm이 다른 label보다 비정상적으로 작은 label을 backdoor target으로 판단한다.

초반에는 target label을 찾고 이후에는 mask 및 $\Delta$를 최적화하는데 집중하기 때문에 초반에 찾은 target label의 rank를 매기고 여기 안에서 최적화하는데 집중하면 computation을 줄일 수 있다. 이때 random label에 대해서도 optimization을 실행해서 정상 label의 분포를 추정한다.

이후에 backdoor을 약화시키는데는 3가지 방법이 있다.
1. filtering : 
	- second-to-last layer의 상의 1% neuron activation이 임계값보다 높은 input을 adversarial input으로 판단하여 차단한다
2. prune out : 
	- clean input과 revesred-trigger input 사이에서 actiavation 차이가 큰 neuron을 찾는다.
	- 이때 reverse-trigger와 orginal trigger은 특히 BadNet에서 유사하고 유사한 neuron을 activation한다.
	- 차이가 큰 neuron부터 pruning하고 reversed trigger가 더이상 반응하지 않으면 중단한다.
	- 이때 last-convolutional layer에서 가장 좋은 성능을 보였다.
	- BadNet에 효과가 좋지만 Traijon에는 효과가 낮다.
3. Unlearning 
	- original dataset 10%, trigger dataset 20%를 섞어서 model을 1 epoch fine-tuning한다.
	- 이때 label을 original label로 변경해준다. 
	- Traijon에서 효과가 좋은 방식이다
## Comparison with Prior Work

기존 연구들은 감염 여부를 이미 안다고 가정하고 backdoor을 완화하늗네만 집중했다.
## Limitations

**Paper's Limitations**
- source-target label 쌍을 이용할때 분할정복을 이용하더라도 O(logn)의 계산 비용이 나와서 이는 추후에 추가적인 연구가 필요하다.
- Trigger가 큰 경우에는 label의 trigger norm과 비슷해져서 outlier이 실패할 수 있다.
- reversed trigger과 original trigger 사이의 관계와 어떤 layer을 선택하는지의 영향을 크게 받는다.

**My Limitations**
- training 과정이 필수적이라는 점에서 computing 자원 소모가 클거 같다.
## Related Work

Demon in the Variant: Statistical Analysis of DNNs for Robust Backdoor Contamination Detection - source->target 후속연구
## Takeaway

Backdoor가 심어진 nn에서 어떻게 backdoor을 감지하고 제거해야하는지


