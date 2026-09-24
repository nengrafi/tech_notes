---
title: Effective Whole-body Pose Estimation with Two-stages Distillation
field: AI
category: Generative Model
status: First Pass
---
## Summary

2단계의 TPD 방식을 이용하여 경량 pose estimation 모델의 성능을 크게 향상시키고 학습시간을 단축한다.
## Problem Statement

- 손,얼굴과 같은 작은 신체부위는 해상도가 낮아서 세밀한 keypoint localization이 어렵다
- occlusion이나 복잡한 자세에서 정학한 pose estimation이 어렵다
- whole-body dataset이 부족하다
- 높은 정확도를 유지하며 model을 경량화할 필요성이 있다
## Key Idea

2단계의 TPD방식을 이용한다.
- 1단계에서 pretrained teacher의 feature와 logits를 이용하여 student model을 학습한다
- 2단계에서 self-KD를 이용해서 backbone은 freeze하고 head만 학습하여 pose localization의 성능을 추가로 향상시킨다.
## Method

![](../assets/Pasted%20image%2020260925034304.png)

1단계에서 teacher model로 dillustion한다.이때 이전 model들과 달리 invisible keypoint도 반영한다. 실제로 이전 식에는 W가 존재했지만 이로 인해서 필요가 없어졌다. loss는 MSE loss를 이용한다.
$$
L_{logit}
=
-\frac{1}{N}
\cdot
\sum_{n=1}^{N}
\sum_{k=1}^{K}
\sum_{i=1}^{L}
T_i \log(S_i)
$$
계산할때 weight-decay를 이용하여서 학습이 진행될수록 GT label에 더 집중하도록 한다.
$$
r(t)=1-\frac{t-1}{t_{max}}
$$
$$
L_{s1}
=
L_{ori}
+
r(t)\cdot \alpha L_{fea}
+
r(t)\cdot \beta L_{logit}
$$
2단계에서는 self-KD를 이용하는데 Backbone은 freeze하고 head만을 학습시킨다. 이때 backbone이 feature을 추출하고 head가 keypoint 위치를 예측하기 때문에 pose localization의 성능이 향상된다.
$$
L_{s2}=\gamma L_{logit}
$$
## Comparison with Prior Work

RTMpose에서는 visible keypoint만 supervision에 사용했지만 Dwpose는 invisible keypoint도 사용한다
## Related Work

RTMPose: Real-Time Multi-Person Pose Estimation based on MMPose (2023)
: 거의 base model
## Takeaway

Dillustion의 정의및 backbone(encoder)과 head(decoder)의 차이및 dwpose라는 모델


