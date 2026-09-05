---
title: Attention is all you need
field: AI
category: NLP
status: First Pass
---

# Abstract

sequence transduction 모델 : RNN,CNN 주로 사용

- encoder - attention - decoder 구조

Transformer : attention 구조만을 사용

- input과 output의 의존성을 global하게 학습
- parallelizable 용이
- less time to train
# Introduction

sequence modeling과 transduction problems :

encoder - decoder 구조

1. RNN

$$  
h_{t+1} = f(h_{t})  
$$

- parallelization 불가능
- 긴 문장에서 메모리 제약 때문에 batch 처리 한계

1. LSTM
2. GRU : LSTM 간소화

Attention :

- input과 output 사이의 거리와 상관없이 의존성 학습
- RNN과 함께 사용되어 옴

# Background

Reducing sequential computation

- CNN을 building block으로 사용
- hidden representations를 parallel 하게 계산
- input과 output 사이의 거리에 따라 연산횟수 증가
    - transformer에서는 연산횟수가 상수번으로 감소
    - 이로 인한 effective resolution 감소는 multi-head attention으로 보완

Self - attention :

다른 위치의 single sequence를 연관시켜 문장의 representation 계산

End-to-End Network :

recurrent attention mechanism에 기반을둠

- 조금씩 필요한 부분만 정보를 처리 (한번에 X)

# Model Architecture

![[Pasted image 20260906031512.png]]

이전에 사용했던 symbol을 next generate에서 input으로 사용

Embedding : 자연어 → vector

- 방향 = 의미
- 길이 = 의미의 강도와 중요도
- 방향 사이의 거리 = 단어의 관계
- 코사인 유사도 (내적)을 통해 두 단어의 의미 유사도 결정

Positional Encoding : 병렬 처리를 위해서 embedding vector에 위치 정보 추가

point-wise Fully connected :

- 일반 FFN은 백터를 입력받음
- point-wise FFN은 백터가 모인 sequence를 입력받음
- 각 행 (단어백터)마다 동일한 FFN 독립적으로 적용

Residual connection :

- input값을 더함
- vanishing gradient 문제 해결

## Encoder and Decoder Stacks

Encoder :

- input값 사용
- X→ Z (정보 압축)
- N = 6의 Layer
- 각 Layer당 2개의 sub-layer
    - Multi-head attention
    - position-wise FFN
    - 각 sub-layer마다 residual connection → layer Normalization
    - sub-layer, embedding layers, outputs 모두 512차원

$$  
LayerNorm(x+Sublayer(x))\\  
d_{model} = 512  
$$

Decoder :

- output값 사용
- Z → Y (결과물을 순차적으로 생성)
- N = 6 Layer
- 각 Layer 당 3개의 sub-layer
    - self-attention에서 이후 위치를 pretend하지 못하도록 masking
    - Encoder의 output에 Multi-head attetnion
    - position-wise FFN
    - 각 sub-layer마다 residual connection → layer Normalization
    - sub-layer, embedding layers, outputs 모두 512차원

## Attention

### Scaled-Dot-product Attention

![[Pasted image 20260906031530.png]]
Query : 나 자신

Key : Query와 얼마나 관련있는지 비교하는 대상

Value : 단어가 실제로 담고 있는 내용

- Q,K로 가중치 W를 만들어 value를 얼마나 가져올건지 결정

$$  
\mathrm{Attention}(Q, K, V) = \mathrm{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V\\  
Q,k = d_{k}\\  
V = d_{v}  
$$

1. Additive attention : FFN에 하나의 hidden Layer
2. Dot-product attention : 백터 사이의 유사도 내적

- 2번이 1번보다 faster 하고 space-efficient하여 위의 방법 선택
- dk가 클때 dot products의 magnitude가 커지므로 gradient가 0에 가까워짐  
    그래서 루트 dk를 이용해 scaling

### Multi-Head Attention

![[Pasted image 20260906031535.png]]

Concat : 이어붙임

Linear Projection : 하나의 백터를 다른 공간으로 옮기는 연산

1. 각 Q,K,V를 Linear Projection을 이용해서 512→ 64차원으로 변환하여 정보 압축  
    그리고 이걸 h =8번 반복, 이때 W의 값은 다 다르고 업데이트 됨
2. Attention을 이용하여 dv 차원의 head output이 나옴
3. 이걸 concat하고 Linear Projection 하여 서로 다른 head가 찾아낸 정보를 통합

- 다양한 표현 subspaces에서 정보를 참조할 수 있음
- 각 head의 차원이 reduce되어서 total computational cost는 일반 Attention가 비슷하다

$$  
\mathrm{MultiHead}(Q, K, V) = \mathrm{Concat}(\mathrm{head}_1, \dots, \mathrm{head}_h) W^O\\  
\mathrm{head}_i = \mathrm{Attention}(Q W_i^Q, K W_i^K, V W_i^V)\\  
W_i^Q \in \mathbb{R}^{d_{\text{model}} \times d_k}, \quad  
W_i^K \in \mathbb{R}^{d_{\text{model}} \times d_k}, \quad  
W_i^V \in \mathbb{R}^{d_{\text{model}} \times d_v}\\  
W^O \in \mathbb{R}^{h d_v \times d_{\text{model}}}  
\\h = 8, \quad d_k = d_v = \frac{d_{\text{model}}}{h} = 64

$$

### Applications of Attention on Model

self-attention : Q,V,X가 모두 동일한 입력값 X에서 linear projection된다

- Decoder의 multi-head attention에서 Q는 이전에 masked된 attention에서 오고 V,K는 enocder에서 온다. 이때 Q는 다음에 생성될 단어 질문에 관한 값이고 K는 input 값의 특징 태그이다.
- Encoder는 self-attention 방식을 사용한다
- train 과정에서 미래의 정보를 참조하지 않게 하기 위해 현재 단어 이후의 단어들은 -무한대로 masking한다.

## Position-wise Feed-Forward Networks

$$  
\mathrm{FFN}(x) = \max(0, x W_1 + b_1)\, W_2 + b_2  
$$

- fully connected 사이에 RELU를 사용함
- kernel size 1의 두개의 convolutions라고도 표현 가능함

## Embedding and softmax

learned embedding : 모델이 trian 과정에서 스스로 파악하여 vector로 전환

softmax function :

- Normalization : 0~1 사이값, 합은 1
- 높은 score의 vocab에 높은 prob를 몰아줌

pre-softmax Linear Transformation : Decoder 출력 vector를 단어 점수로 변환

input과 output embedding layer, pre-softmax에서 w를 공유한다

embedding layer에서 루트 dmodel만큼 곱해서 scaling 해준다

- Positional Encoding의 값이 상대적으로 크기 때문에 값의 범위를 맞추기 위해서 scaling을 해준다.

![[Pasted image 20260906031739.png]]

Complexity per Layer : Layer당 수행되는 총 연산량

Sequential Operations : 순서대로 수행되야 하는 연산 단계

Maximum Path Length : 두 신호 사이에 거쳐야 하는 최대 노드수

- 작을수록 long-term dependency 학습에 유리
    - gradient vanishing/exploding 감소
    - noise 감소
    - optimization이 수월해짐

## Positional Encoding

position 정보를 추가

- pos + k 위치 백터는 pos 위치 백터에 회전행렬을 곱한것과 같음  
    상대적인 거리를 파악가능

learned positional Encoding : 학습때의 MAX 치에 고정

fixed positional Encoding : 학습때의 MAX치를 벗어날 수 있음

$$  
\begin{aligned}  
PE(pos, 2i) &= \sin\left(\frac{pos}{10000^{\frac{2i}{d_{\text{model}}}}}\right) \\  
PE(pos, 2i+1) &= \cos\left(\frac{pos}{10000^{\frac{2i}{d_{\text{model}}}}}\right)  
\end{aligned}  
$$

pos : postion, i : dimension

10000 : 긴 가상의 문장 길이 설정 → 고유값 가짐

# Why self-Attention

![[Pasted image 20260906031746.png]]

1. computational complexity per layer

- n < d일때 RNN보다 transformer가 성능이 좋다
- SOTA model이 n<d이기 때문에 tranformer가 성능이 좋음
- size r로 제한하여 보는 tranformer가 존재
- seperable convoultion을 사용해도 k=n일때 tranformer와 똑같은 연산량 사용

1. amount of computation can be parallelized
2. path length between long-range dependencies

- 짧을수록 long-range dependencies를 학습시키기 쉬움
- RNN에 비해 transformer가 유리
- CNN은 여러 O(n/k)만큼의 층이 필요하지만 attention은 O(1)로 모두 연결 가능

long-range dependencies를 학습시키는게 key challenge이다

- self-attention은 more interpertable하다

# Training

## Training Data and Batching

- standard WMT 2014 English-German dataset
    - byte-pair encoding
        - subword Tokenization 알고리즘
        - source-target vocabulary
- WMT 2014 English-French dataset
    - 36M sentences token → 32000 word-piece

Batching : GPU를 낭비하지 않기 위해서 배치안에 문장길이를 모두 같게 구성

- 25000개의 token으로 batching

## Hardware and schedule

Base Model

- 8 NVIDIA P100 GPU
    - training step 0.4s 소요
    - 100,000 steps, 12hours

Big Model

- 8 NVIDIA P100 GPU
    - training step 1s 소요
    - 300,000 steps, 3.5 days

## Optimizer

Adam optimizer 사용 :

- Momentum : 이전 단계의 이동방향을 현재 이동에 반영
    - local minima나 문제에 유리

$$  
\begin{aligned}v_t &= \beta v_{t-1} + (1 - \beta)g_t \\w_{t+1} &= w_t - \eta v_t\end{aligned}  
$$

- RMSProp : descent의 크기를 보고 학습률을 유동적으로 조정
    - 학습이 진행될수록 분모가 무한히 커져 학습이 멈추는 문제 방지
    - 기울기가 가파르면 보폭이 작아짐

$$
\begin{aligned}
s_t &= \gamma s_{t-1} + (1 - \gamma)g_t^2 \\
w_{t+1} &= w_t - \frac{\eta}{\sqrt{s_t + \epsilon}}g_t
\end{aligned}
$$
- $s_t$ : 기울기 제곱의 누적값
- $\gamma$ : 감쇠 계수 (보통 0.99)
- $\epsilon$ : 분모가 0이 되는 것을 방지하는 아주 작은 값

$$  
\theta_{t+1} = \theta_t - \frac{\alpha}{\sqrt{\hat{v}_t} + \epsilon} \hat{m}_t  
$$

$$  
\beta_1 = 0.9,\beta_2 = 0.98,\epsilon = 10^{-9}\\\mathrm{lrate} = d_{\text{model}}^{-0.5} \cdot \min\left( \mathrm{step\_num}^{-0.5}, \; \mathrm{step\_num} \cdot \mathrm{warmup\_steps}^{-1.5} \right)  
$$

warmup_steps 동안은 lr을 선형적으로 증가시키고 그 이후부터는 step_num의 역제곱근에 비례하여 감소시킴, warmup_steps = 4000

## Regularization

![[Pasted image 20260906031954.png]]

Residual Dropout :

- sub-layer와 positional encoding 이후에 적용
- pdrop = 0.1
- Dropout → Residual Add
    - 일부 뉴런을 랜덤하게 꺼버림

Label Smoothing :

- 정답의 확률을 1에 가깝게 하되 1은 아니게 함 → overfitting 방지
- ϵls = 0.1
- PPL(모델 확신도)은 나쁘지만 Accuracy랑 BLEU는 좋아짐

# Results

## Machine Translation

CheckPoint Averaging :

- 10분마다 weight 저장
- 마지막에 저장된 5개(base) 혹은 20개(Big)의 checkpoint를 산술평균
- 앙상블 효과를 냄

Beam Search :

- 상위 4개의 후보군을 유지하며 문장 완성 → greedy 방지

Length penalty :

- 문장이 길어질수록 점수가 낮아지는 편향 방지를 위해 문장 길이로 점수를 나눠줌
- 0.6

## Model Variations

![[Pasted image 20260906032000.png]]

head : head가 많으면 head가 볼 수 있는 정보의 차원이 얇아 학습이 안됨

dk : dk가 충분히 넓어야 단어간의 복잡한 관계를 수치화 가능

dff,dmodel : 성능 상승, dropout의 역할

positional encoding : learned와 sinusoidal의 성능이 비슷, 따라서 더 긴 문장을  
사용 가능한 후자 선택

## English Constituency Parsing

![[Pasted image 20260906032006.png]]

parsing의 어려움

- output의 구조적 제약
- input보다 긴 output
- 데이터 부족에 취약

결과 : 적은 데이터에서도 튜닝없이 더욱 좋은 성적이 나옴

# Conclusion

기존 encoder-decoder 구조에서 사용하던 recurrent layers를 multi-headed self attention으로 대체하였고 그 결과 성능이 짱짱좋았다.

앞으로 우리는 모달리티를 포함하는 문제로 확장할 예정이다.

또한 대규모 입출력 데이터를 처리하기 위해 restricted attention 메커니즘을 조사할 것이다.

마지막으로 생성과정을 less sequential하게 만드는것 역시 목표이다.