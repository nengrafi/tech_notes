---
title: "LoRA: Low-Rank Adaptation of Large Language Models"
field: AI
category: Efficient Learning
status: First Pass
---

# Abstract

자연어 처리 중요 패러다임

1. 일반 도메인 데이터 대규모 pretraining → pretraining이 커지며 full fine-tuning이 어려워짐
2. 특정 task, 도메인에 adaptation

이때 pretrained model weight를 고정하고 ($W_0$) 각 layer에 rank decomposition matrix(를 주입하여 ($A,B$) 학습가능한 parameter의 수를 크게 줄인다. GPT-3과 비교해보았을때 parameter를 10000배, GPU memory를 3배 줄인다. 또한 RoBERTa, DeBERTa, GPT‑2, GPT‑3에서 model quality 측면에서도 full-fine-tuning와 동등하거나 더 우승한 성능을 보이고 adapter (transformer → adapter → inference) 와 달리 추가적인 inference latency도 발생하지 않는다.  
LoRA는 language model adaptation에서 나타나는 rank-deficiency를 경험적으로 조사하고 통찰한다.

# Introduction

NLP에서 주로 대규모 pretrained language model을 여러 downstream application에 맞게 적용한다. 이때 주로 모든 parameter를 업데이트하는 full-fine-tuning을 수행한다. 이때 새로운 model이 원래 model과 동일한 수의 parameter를 포함하면서 배포에 어려움이 생긴다.

이를 완화하기 위해 일부 parameter만 adaptation하거나 새로운 task를 위한 외부 module을 학습시키는 연구가 많이 이루어져왔다. 그러나 기존 방법은 model의 depth를 확장시켜 inference latency(추론지연시간)를 유발하거나 사용가능한 sequence length를 줄이는 경우가 많다. 또한 full-fine-tuning 성능에 도달하지 못하는 경우가 많아서 효율성과 quality 사이의 trade-off가 발생한다.

우리는 학습된 over-parametrized model이 실제로 낮은 intrinsic demension에 존재한다는 다른 연구 결과를 바탕으로 model adaptation 중 weight의 변화에도 낮은 intrinsic rank가 존재한다고 가정하여 이를 바탕으로 LoRA를 도출하였다. 이때 intrinsic dimension은 어떤 task를 해결하기 위해 실질적으로 필요한 독립적인 parameter 수이다.

LoRA는 pre-trained weight는 고정하고 adaptation중 dense layer(linear layer)의 변화에 대한 rank decomposition matrix를 대신 최적화 하여 nn의 일부 dense layer를 간접적으로 training한다.
![](../assets/Pasted%20image%2020260906082518.png)

LoRA의 장점은 다음과 같다

- 하나의 pre-trained model을 공유하며 서로 다른 task를 위한 여러 소규모 LoRA module을 구축할 수 있다. 이를 통해 storage 요구량과 task 전환 overhead를 크게 줄인다.
- parameter에 대해 gradient를 계산하거나 optimizer state를 유지할 필요가 없으므로 더욱 효율적이고 hadware 진입장벽을 최대 3배 낮춘다. 이때 low-rank matrix만 최적화한다.
- 단순한 linear design을 사용하여 배포시 matrix를 고정된 weight와 병합 가능하다. 따라서 inference latency가 발생하지 않는다.
- 기존의 방법과 orthogonal(독립적이라 함께 사용가능)하여 prefix-tuning과 같은 많은 방법에 결합할 수 있다.

용어

$W_0$ : pretrained weight matrix

$r$ : LoRA module rank

Adam :

- gradient의 이동평균(gradient의 방향) : $m_t = \beta_1 m_{t-1} + (1 - \beta_1) g_t$
- gradient 제곱의 이동평균 (gradient의 크기) : $v_t = \beta_2 v_{t-1} + (1 - \beta_2) g_t^2$

$$  
\theta_t = \theta_{t-1} - \eta \frac{\hat{m}_t}{\sqrt{\hat{v}_t} + \epsilon}  
$$

Trnsformer MLP ff dimension : $d_{ffn}=4×d_{model}$

# Problem Statement

LoRA는 특정한 training object에 한정되지 않지만 논문에서는 주로 task-specific prompt가 주어졌을때 conditional probability를 최대화 하는 문제를 설명한다.

$\Phi = \{W_1, W_2, W_3, \ldots\}$로 parametreized 된 pre-trained autoregressive(앞에서부터 한 token씩 생성) language model이 주어진다. 이를 MRC(글을 읽고 답하는 task), NL2SQL(자연어 질문을 SQL query로 변환)과 같은 downstream conditional text generation task로 adaptation 한다고 하자. 이때 train set은 $\mathcal{Z} = \{(x_i, y_i)\}_{i=1,\ldots,N}$의 형태로 표현된다. (여기서 x,y 모두 token sequence)

**Full fine-tuning**  
여기서는 pre-trained weight $\Phi_0$로 초기화한 후, conditional language modeling objective ($PΦ​(y∣x)$)를 최대화하도록 gradient 계산을 하며 $Φ_0 + ΔΦ$로 업데이트한다.

$$
\max_{\Phi}
\sum_{(x,y)\in\mathcal{Z}}
\sum_{t=1}^{|y|}
\log\left(
P_{\Phi}(y_t \mid x, y_{\lt t})
\right)
$$

주요한 단점중 하나는 각 downstream task마다 서로 다른 집합 $∆Φ$를 학습하는 것이고 dimension이 parameter만큼 크다. 모델이 큰 경우에 독립적인 instance를 여러개 저장하고 배포하는데 어려움이 있다.

논문에서 $\Delta \Phi = \Delta \Phi(\Theta)$가 $|\Theta| \ll |\Phi_0|$을 만족하는 작은 parameter 집합 $Θ$로 다시 parameterization한다. 즉 $Θ$를 encoding한다.

$$
\max_{\Theta}
\sum_{(x,y)\in\mathcal{Z}}
\sum_{t=1}^{|y|}
\log\left(
p_{\Phi_0+\Delta\Phi(\Theta)}
\left(y_t \mid x, y_{\lt t}\right)
\right)
$$

GPT-3의 경우 trainable parameters의 수는 0.01%만큼 작을 수 있다.

# Aren’t Existing Solutions Good Enough

transfer learning이 시작된 이후에 많은 연구가 model adaptation을 parameter와 계산 측면에서 효율적으로 만들려고 했다. 이때 두개의 전략이 있는데

- adapter layers를 추가
- input layer activation의 일부 형태를 optimization

→ 둘다 대규모이며 latency에 민감한 실제 서비스 운영 환경의 한계

**Adapter Layers Introduce Inference Latency**

- Transformer block마다 두개의 adapter layer 사용
- Transformer block마다 하나의 adpater layer 사용 + LayerNorm 사용
- Layer를 가볍게 만들거나 task를 효율적으로 묶음 → adapter layers의 추가적은 compute 우회불가
- 작은 bottleneck dimension(중간 layer)를 사용해 적은 parameter로 추가적인 FLOPs가 제한적이여서 문제로 보이지 않아보인다. 하지만 adapter layers는 순차적으로 처리되어야 한다. online 추론환경에서는 빠른 대답을 위해서 batch 사이즈를 줄이는데 이때 latency가 눈에 띄게 증가한다.
- 큰 모델 하나를 여러 GPU에 쪼개는 경우에는 추가적은 depth로 인해 synchronous GPU operations(GPU끼리 통하는 연산)이 더 많이 필요하여 문제가 더 심각해진다.

**Directly Optimizing the Prompt is Hard**  
prefix tuning : attention에 들어갈 prefix representation을 추가해서 task에 적응시킴  
이때 model은 frozen됨

$$  
K' = [K_{p1}, K_{p2}, \ldots, K_{pm}, K_1, \ldots, K_5]\\  
V' = [V_{p1}, V_{p2}, \ldots, V_{pm}, V_1, \ldots, V_5]\\  
Attention(Q,K^′,V^′)  
$$

prefix tuning은 model을 최적화 하기 어렵고 trainable parameters수가 증가한다고 성능이 좋아지지 않는다. 또한 사용가능한 sequence length가 줄어든다.
![](../assets/Pasted%20image%2020260906082543.png)
# Method

## Low-Rank-Parametrized update matrices

dense layers의 weight는 일반적으로 full-rank이다. 하지만 특정 task에서 더 낮은 instrisic dimension을 가지고 더 작은 subspace으로의 random projection으로 효율적인 학습이 가능하다는 연구 결과가 있었다. 이에 따라 adaptation중 weight에 대한 update 역시 낮은 intrinsic rank를 가진다고 가정하자. $𝑊_0 ∈ ℝ_{𝑑×k}$에 대해서 update를 low-rank decomposition $𝑊_0 + Δ𝑊 = 𝑊_0 + 𝐵A$로 표현한다. 이때 $𝐵 ∈ ℝ_{𝑑×r},𝐴 ∈ ℝ_{𝑟×k}$이고 rank는 $𝑟 ≪ min(𝑑, 𝑘)$이다.(선형변환의 관점에서 보았을때 k→d이기 때문이다.) training 중에 $W_0$는 frozen되며 $A,B$가 train된다.

이때 $A$는 random Gaussian initialization을 사용하고 $B=0$으로 설정한다. 따라서 초반 변화량은 0이고 이후 $∆W x$를 $\frac{\alpha}{r}$만큼 scaling한다. 이때 rank가 커질수록 $d×r$ rank 1의 합 개수가 커지면서 원소의 magnitude가 커질 수 있으므로 r을 나눠준다. $\alpha$는 hyperparameter이다. initialization scale(A의 표준편차를 적절히 $\frac{\alpha}{r}$와 균형있게 설정) 하면 learning rate와 효과가 겹치기 때문에 논문에서는 고정하고 다른 hyperparameter를 tuning한다.

**A Generalization of Full Fine-tuning**  
일반적인 fine-tuning에서는 pre-trained parameter의 일부를 선택 training할 수 있다. LoRA는 거기서 더욱 나아가 adaptation 중에 $∆W$가 full-rank(min(d,k))일 필요없다. 따라서 rank를 pre-trained weight matrices와 같게 설정할 경우 full-fine-tuning과 동일한 표현력을 얻는다. 즉 trainable parameters의 수를 늘리면 full-fine-tuning에 수렴해간다. 이때 adapter-based methods는 MLP로 prefix-based methods는 긴 input sequences를 처리할 수 없는 모델로 수렴한다.

**No Additional Inference Latency.** 
production  $W_0$와 $BA$는 $\mathbb{R}^{d \times k}$차원이다. 우리가 다른 downstream task로 전환 할 때 $BA$를 빼고 다른 $𝐵^′𝐴^′$를 더하여 새로운 $W_0$를 복원한다. 이는 memory overhead가 거의 없는 빠른 operation이며 이를 통해 full-fine-tuned model과 비교하였을 때 추론 중에 추가적인 latency가 발생하지 않는다.
## Applying LoRA to Transformer

일반적으로 nn은 모든 weight matrices의 일부에 LoRA를 적용하여 trainable parameters의 수를 줄일 수 있다. attention에는 4개의 weight $(𝑊_𝑞  , 𝑊_𝑘  , 𝑊_𝑣  , 𝑊_𝑜  )$가 있고 MLP에는 2개가 있다. LoRA에서는 output dimension의 attention head들을 하나의 matrix로 취급하고 attention weights만을 adaptation한다. 

**Practical Benefits**
frozen parameter에 대한 optimizer state를 저장할 필요없으므로 VRAM 사용량을 최대 2/3까지 줄일 수 있다. 실제로 r = 4를 이용하고 query 및 value projection matrix만 adaptation 하면 checkpoint의 크기를 약 1만배 줄일 수 있다. 이를통해 GPU 필요량을 줄이고 I/O bottleneck(데이터를 읽고 쓰는 속도가 느려서 작업이 막힘)을 피할 수 있다. 또한 적은 비용으로 task간의 전환이 가능하다. 

**Practical Limitations**
A,B가 task별로 다르기 때문에 여러 task의 input을 하나의 forward pass에서 batch 처리하는것이 어렵다.
# Empirical Experiments

## BaseLines

기존연구에 사용된 설정을 재현한다.  
간단한 변형으로 finetuning의 일부 layer만 update하고 나머지는 freezing할 수 있는데 GPT-2에서 마지막 두 layer만 adaptation하는 기존 연구 설정을 포함하였다.
![](../assets/Pasted%20image%2020260906082555.png)

**Bias-only or BitFit**
다른건 다 freeze 하고 bias vectors만 학습

**Prefix-embedding tuning**
input tokens에 special tokens를 넣는다. prefix 또는 infix에 넣는다. 즉
$|\Theta| = d_{\text{model}} \times (l_p + l_i)$이다.

**Prefix-layer tuning**
prefix-embedding tuning의 확장으로 모든 transformer layer에 대한 special tokens를 학습한다. 즉 Layer마다 special token이 변화한다. 
$|\Theta| = L \times d_{\text{model}} \times (l_p + l_i)$

**Adapter tuning**
| Method | Adapter 위치 | 특징 |
|---|---|---|
| AdapterH | Attention 뒤 + MLP 뒤 | original design, adapter 수가 많음|
| AdapterL | 주로 MLP 뒤 + LayerNorm 이후 | 더 efficient | 
| AdapterP | AdapterL과 유사한 single-placement design | parameter-efficient |
| AdapterD | 일부 layer의 adapter 제거 | 계산량과 parameter 추가 감소 |

$|\Theta| = \hat{L}_{\text{Adpt}} \times \left(2 \times d_{\text{model}} \times r + r + d_{\text{model}}\right) + 2 \times \hat{L}_{\text{LN}} \times d_{\text{model}}$

**LoRA**
trainable rank decomposition matrix를 추가한다. 이떄 $W_q$와 $W_v$만 적용한다. $|\Theta| = 2 \times \hat{L}_{\text{LoRA}} \times d_{\text{model}} \times r$ 
## RoBerta Base/Large

RoBerta는 BERT에서 처음 제안된 pre-training recipe을 최적화하여 BERT task 성능을 향상한 모델로 여전히 널리 사용되는 pre-trained model이다. 여기서 base,large 모델을 가져오는데 두가지 변경을 제공했다.
1. 모든 task에 동일한 batch size를 사용하고 adapter basline을 맞추기 위해 length 128로 설정한다
2. fine-tuning 과정을 1회로 단축
## Deberta XXL
최신 BERT의 변형이다.
## GPT-2 Medium/Large

![](../assets/Pasted%20image%2020260909170853.png)
## Scaling up to GPT-3 175B

GPT-3는 training 비용이 높으므로 random seed에 대한 특정 task의 일반적인 표준편차만 보고한다. 
![](../assets/Pasted%20image%2020260909172544.png)
trainable parameter를 더 많이 사용한다고 해서 무조건 성능이 상승하지 않는다. 
또한 prefix-embedding tuning에서 256개 보다 많은 special token을 사용하거나 prefix-layer tuning에서 32개보다 많은 special token을 사용하면 성능이 크게 하락하는 것을 관찰했다. 논문에서는 special token이 많아질수록 input distribution이 pre-training data distribution에서 멀리 이동하기 때문이라고 추측하였다.
![](../assets/Pasted%20image%2020260909172559.png)

# Understanding the Low-Rank Updates

low-rank 구조는 여러 실험을 병렬로 수행하는 하드웨어 진입 장벽을 낮추고 update weight가 pretrained weight와 어떻게 상관되는지 해석 가능성도 높인다.
1.  parameter buget(parameter 한도) 제약시에 성능 최대화를 위해 어떠한 weight matrix의 부분집합을 adaptation 해야하는가?
2. $ΔW$는 실제로 rank-deficient 한가?
3. $W$와 $ΔW$ 사이에는 어떤 관계가 있는가?
## Which weight matrices in Transformer should we apply LoRA To?

논문에서는 self-attention module의 weight matirx만 고려한다.
![](../assets/Pasted%20image%2020260907141538.png)
$W_q,W_v$를 모두 adaptation하면 가장 높은 성능을 보인다. 즉 rank 4만 되어도 충분한 정보를 포착하므로 하나의 weight만 높은 rank로 adaptation 하는것보다 더 많은 weight matrix를 adaptation 하는것이 바람직하다. 
## What is the optimal Rank r for LoRA?

rank r이 model에 미치는 영향에 주목한다. 
![](../assets/Pasted%20image%2020260907141529.png)
매우 작은 r에서도 경쟁력 있는 성능을 달성한다. 이를 통해 $ΔW$가 매우 작은 intrinsic rank를 가질 수 있음을 시사한다.
이를 더욱 뒷받침하기 위해 서로 다른 r과 random seed로 학습된 subspace overlap을 확인한다. 이때 r을 증가시켜도 더 의미있느네 subspace를 포괄하지 못한다.

**Subspace similarity between different r**
singular vector가 어떤 공간을 span한다는건 두 벡터를 조합해서 만들 수 있는 벡터의 집합이다. A는 adaptation matrix고 U는 singular value decomposition이다. U에서 상위 i개 singular vector가 span하는 subspace가 어느정도로 겹치는가를 측정한다. 이때 Grassmann distance에 기반한 normalized subspace similarity로 측정한다.
$$
\phi(A_{r=8}, A_{r=64}, i, j)
=
\frac{
\left\| U_{A_{r=8}}^{i\top} U_{A_{r=64}}^j \right\|_F^2
}{
\min(i,j)
}
\in [0,1]
$$
1은 subspace가 완전히 overlap되고 0은 완전히 분리됨을 의미한다.
![](../assets/Pasted%20image%2020260907165928.png)
$A_{r=8}$과 $A_{r=64}$의 subspace similarity를 $Δ𝑊_q$와 $Δ𝑊_v$에 대해 나타낸것이다. 3번째, 4번째 그림은 1,2번째 그림을 확대한것이다. 이때 상위 singular vector는 상당히 overlap되지만 다른 방향은 그렇지 않다. 실제로 dimension 1에서 normalized similarity > 0.5인 subspace를 공유한다. 
또한 하위 singular vector들은 random noise로 해석할 수 있다.

**subspace similarity between different random seeds**
서로 다른 seed의 normalized subspace similarity를 그렸을때 $Δ𝑊_q$는 $Δ𝑊_v$보다 높은 intrinsic rank을 가지는 것으로 보인다.(더 높은 singular value가 겹침)
![](../assets/Pasted%20image%2020260908160223.png)
## How does the Adaptation Matrix $ΔW$ Compare to $W$?

$∆W$가 W와 비교했을때 얼마나 큰지 확인하기 위해서 W를 $∆W$의 r-dimensional subspace에 project한다. 이때 $U^\top W V^\top$를 계산하는데 U는 output 방향의 정보이고 V는 input 방향의 정보이다. 그리고 $\left\| U^\top W V^\top \right\|_F$와 $‖𝑊‖_F$ 를 비교한다. 즉 random r, W, $∆W$를 비교한다.
![](../assets/Pasted%20image%2020260909151045.png)
1. $∆W$는 random matrix보다 W와 더 강한 correlation을 가진다. 즉 W에 존재하는 일부 feature을 증폭한다는 것을 의미한다. 
2. ∆W는 W의 top singular direction을 반복하는 대신 W에서 강조되지 않은 direction만 증폭한다.
3. Amplification factor가 21.5에 가깝게 매우 크다
$$
\text{Amplification factor}
=
\frac{
\Delta W\text{가 선택한 방향에서 }W\text{의 크기}
}{
\text{random 방향에서 }W\text{의 크기}
}
$$
# Conclusion and future work

거대한 language model을 fine-tuning하는데 필요한 hardware와 서로 다른 task를 위한 독립적인 instance를 hosting할때 발생하는 storage/switching cost 측면에서 감당하기 어려울 정도로 큰 비용이 든다. 이때 논문에서는 높은 model quality를 유지하며 inference latency를 발생시키지 않고 input sequence length도 줄이지 않는 효율적인 adaptation strategy인 LoRA를 제안한다. model parameter 대부분을 공유하므로 서비스시에 빠르게 task를 전환할 수 있고 dense layer를 포함하는 모든 nn에 일반적으로 적용할 수 있다.

향후 연구
1. 다른 효율적인 adaptation method와 결합을 위해 독립적인 improvement 제공 가능성
2. LoRA의 mechanism 명확화
3. weight matrix를 선택할때 heuristic에 의존하는데 다른 원칙적인 방법 고안
4. $∆W$의 rank-deficiency가 $W$ 역시 rank-deficient임을 시사함