---
title: Training language models to follow instructions  with human feedback
field: AI
category: NLP
status: reading
---
## Summary

사람의 preference를 이용한 사용자의 instruction과 intention 따라서 alignment하기 위한 fine-tuning 방법을 제시한다.
## Problem Statement

GPT-3와 같은 기존 모델들은 다음 token을 예측하는데에 집중하지만 이것은 실제로 사용자의 instruction과 intention을 알맞게 따르는것과 일치하지 않는다.
## Key Idea

사람의 preference를 반영하기 위해서 labelers를 고용해 직접 dataset을 구성하고 비교하도록 한다. 또한 이 dataset을 이용하여서 3단계 fine-tuning을 진행한다.
1. labeler가 작성한 예비 답변 data를 이용해 이를 통해서 supervised learning 한다.
2. 동일한 prompt에 대해 비교및 ranking해서 이를 바탕으로 Reward function을 학습한다.
3. SFT모델을 초기 policy로 사용하고 RM의 scalar reward를 최대화 하도록 PPO로 학습한다. 
## Method

### Data collection

screening test를 통해 약 40명의 labelers를 고용한다. 이때 task별 instruction과 onboarding이 제공된다.
데이터는 labeler가 작성한 prompt와 OpenAI PlayGround의 customer prompt로 구성된다. 초기에는 user prompt가 충분하지 않기 때문에 labeler가 직접 prompt를 작성하여 bootstrap한다. 
- plain : 임의의 task를 직접 작성, 다양성은 챙김
- Few-shot : instruction 한개와 여러 질의,응답 작성
- User-based : 실제 API waitlist의 use-case를 참고하여 prompt 작성
이때 긴 common prefix는 중복되면 없애고 user ID당 최대 200개로 제한한다. train,validation, test split 역시 user ID로 분리한다. PII (개인정보) 역시 제거한다.

train set을 구성하는 labelers와 별개로 held-out ladeler을 통해 generalization을 평가한다. 이때 held-out ladeler는 screeing test에 참여하지 않는다.

- SFT Dataset : prompt + labeler demonstration (13K)
- RM dataset : prompt + model response에 대한 human ranking (33k)
- PPO dataset : prompt (31k)

### Model

1. SFT : GPT-3 모델을 pretrain model로 사용하며 cosine learing rate decay를 통해 train 후반의 lr을 낮게 조정하고 residual dropout은 0.2로 실행한다. 이때 1 epoch에서 이미 overfitting이 일어나지만 점점 인간 preference rating과 RM score가 증가하므로 epoch를 16까지 실험한다. 이때 각 checkpoint중에 RM score가 높은 곳을 선택한다.
2. RM : SFT model에서 마지막 unembedding layer를 제거하고 scaler reward를 출력하도록 한다. 하나의 prompt에 대해 k =4~9개의 response를 생성하고 이를 ranking한다. cross-entropy를 이용해서 loss 함수를 구성하여 학습한다. 자세한 수식은 아래를 참조한다. 또한 RM loss는 difference를 사용하여서 동일한 constant를 더해도 loss가 변하지 않는 shift ambiguity가 존재한다. 이를 bias를 통해서 mean reward가 0이 되도록 normalize한다.
3. PPO : bandit enviornment (하나의 step) 환경에서 PPO-ptx의 방식으로 학습한다. 이때 ptx는 pretrained data의 값을 섞어줌으로서 performancing regressions을 줄여준다. 또한 KL penalty를 부과함으로서 기존 SFT 모델에서 많이 떨어지지 않도록 해준다. 자세한 수식은 아래를 참조한다. 

이때 RM training과 PPO training은 서로 반복할 수 있다.
현재 policy에서 response 생성 -> labeler가 ranking -> RM 학습 -> PPO 학습
## Key Equations
![](../assets/Pasted%20image%2020260914042308.png)
loss function을 정의한다. 동일한 prompt에서 만들어진 pairwise comparison은 서로 강한 상관관계를 가지기 때문에 (k,2)를 하나의 요소로 생각하고 cross-entropy loss를 이용한다.
이를 통해 계산 비용을 감소시키고 overfitting을 줄인다.

![](../assets/Pasted%20image%2020260914043032.png)
RM reward만 최대화 하면 기존 SFT model과 지나치게 다른 distribution으로 이동할 수 있다. 따라서 RM score에 KL penalty를 부여한다. 이때 KL penalty는 기댓값 상태에서 KL divergence가 되므로 항상 0이상이다. 그리고 pretrianed data를 더해줘서 performancing regressions을 줄인다. hyperparameter $\beta,\gamma$가 존재한다.
## Experimental Setup

GPT-3 architecture의 1.3B, 6B, 175B model을 사용하여 GPT-3, SFT, PPO, PPO-ptx를 비교한다. 주요 학습 데이터는 OpenAI API/Playground의 customer prompt와 labeler가 직접 작성한 prompt로 구성된다. 평가는 크게 두 종류로 수행한다. 

- API prompt 입력을 기반으로 인간 preference 평가 
- Public NLP benchmark에서 truthfulness, toxicity, bias, 기존 NLP capability 평가 

Human evaluation에서는 175B SFT model을 baseline으로 사용하고, labeler preference win rate, 1~7 Likert score, instruction following, hallucination 등의 metadata를 측정한다.
## Results & Analysis

InstructGPT는 GPT-3보다 human preference에서 크게 우수했다. 특히 1.3B InstructGPT도 175B GPT-3보다 더 선호되었으며, 175B InstructGPT는 175B GPT-3보다 85±3%의 비율로 선호되었다. 
![](../assets/Pasted%20image%2020260914054602.png)
또한 
- instruction following 향상 
- hallucination 감소 
- truthfulness 향상 
- respectful prompt에서 toxicity 감소가 관찰되었다. 
하지만 bias는 GPT-3보다 뚜렷하게 개선되지 않았다. 
![](../assets/Pasted%20image%2020260914054625.png)
![](../assets/Pasted%20image%2020260914054635.png)
PPO만 alignment tax가 발생했지만 PPO-ptx를 사용하면 pretraining objective를 함께 유지함으로써 이 성능 저하를 상당 부분 완화할 수 있었다. 즉 human preference 기반 RLHF는 모델 크기 증가 없이도 alignment를 크게 개선할 수 있지만, 기존 capability 유지와 bias 문제는 별도로 고려해야 한다.
## Comparison with Prior Work

FLAN, T0와 같은 기존 instruction-tuning 연구는 public NLP dataset의 instruction을 이용해 fine-tuning하는 방식이지만, InstructGPT는 실제 user prompt와 human preference를 직접 이용한다.
## Limitations

**Paper's Limitations**
- Human feedback가 소수의 labeler에게 의존한다.
- 대부분의 comparison을 비용 문제로 한 명의 labeler만 평가한다.
- InstructGPT는 완전히 aligned되거나 safe한 모델이 아니다.
- harmful한 instruction도 잘 따를 수 있다.

**My Limitations**
- dataset을 제작하는 사람들이 주로 영어사용자라는 점과 openAI prompt를 작성한 user들이 연구진으로 편향되었다는 점에서 신뢰도가 낮게 느껴진다.
## Open Questions

- KL divergence는 왜 무조건 0이상인지 수학적으로 이해하지 못했다.
## Takeaway

RLHF를 이용하여 사람의 prefrence를 반영하고 alignment하는 방법


