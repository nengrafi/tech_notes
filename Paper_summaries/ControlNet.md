---
title: Adding Conditional Control to Text-to-Image Diffusion Models
field: AI
category: Generative Model
status: First Pass
---
## Summary

pretrained된 모델의 원본 parameter을 freeze하고 일부 network block을 trainable copy로 복사하여 추가적인 spatial condition을 학습한다.
## Problem Statement

data가 제한적인 상황에서 큰 모델을 fine-tuning할때 overfitting이나 catastrophic forgetting이 일어난다.
## Key Idea

pretrianed된 모델은 freeze하고 network block을 copy해 condition을 학습한다. 이때 noise가 들어가거나 출력이 망가지는것을 막기위해 zero convolution을 이용한다.
## Method

![](../assets/Pasted%20image%2020260925032009.png)
학습초기에는 zero convolution 때문에 pretrained block과 동일한 x를 입력받지만 점차 condition이 반영된다. 따라서 출력역시 처음에는 동일하다.

$$
y_c
=
\mathcal{F}(x;\Theta)
+
\mathcal{Z}
\left(
\mathcal{F}
\left(
x+\mathcal{Z}(c;\Theta_{z1});
\Theta_c
\right);
\Theta_{z2}
\right)
$$
![](../assets/Pasted%20image%2020260925032127.png)
12개의 encoder block과 1개의 middle block을 trainable copy로 만든다

image $C_i$를 convolution network를 이용해 $c_f$로 변환하여 resolvation을 맞추고 ControlNet에 입력한다. 이때 논문에서 encoder은 4x4 convolution 4개로 구성되고 stride = 2이다.
## Comparison with Prior Work

기존의 fine-tuning과 달리 overfitting이나 catastrophic forgetting에 강하다.
## Takeaway

ControlNet의 구조


