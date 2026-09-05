# Abstract

이 논문에서는 text-to-image 합성을 위한 laten diffusion model SDXL을 제시한다.

- SDXL은 이전에 비해 3배 더 큰 UNet backbone을 활용한다.
- SDXL은 두번째 text encoder을 사용하기 때문에 이전에 비해 더 많은 attention block과 더 큰 cross-attention context를 사용한다.
- 여러가지 새로운 conditioning 방식을 설계하고 다양한 이미지 비율로 training한다.
- 생성한 sample의 시각적 충실도를 높이기 위해서 사후에 image-to-image 기법을 사용하는 refinement model을 도입한다.

이전에 비해 성능들을 향상시키고 최신 black-box image generator와 경쟁력있는 결과를 보인다.

# Introduction

다양한 data domain에서 deep generative modeling이 비약적으로 발전하였다. 이 논문에서는 visula media 분야의 Stable Diffuison을 SDXL을 공개한다. 이때 Stable Diffusion은 latent text-to-image model으로 3D classification, controllable image editing(조건을 주고 이미지 수정), image personalization(특정 대상의 특징으로 새로운 이미지 생성), synthetic data augmentation(인공적인 training image로 dataset 늘리기), graphical user interface prototyping(텍스트로 시안 빠르게 생성)의 기반이 되었다.

설계 선택

1. 기존 Stable Diffusion Model보다 3배 더 큰 UNet backbone
2. 추가적인 감독이 필요하지 않은 두가지 conditioning 기법
3. SDXL이 생성한 latent에 nosing-denosing process를 적용해 sample의 시각적 품질을 향상시키는 별도의 diffusion 기반 refinement model

visual media creation 분야의 주요 문제점은 black-box-model이 흔히 최신 기술로 인정받는 반면, 해당 구조의 불투명성으로 인해 성능을 충실하게 평가하고 검증하기 어렵다는 점이다. 이러한 closed-source 전략은 model의 편향과 햔계를 공정하고 객관적인 방식으로 평가하기 어렵게 만든다. 따라서 이 논문은 open model을 공개한다.

# Improving Stable Diffusion

이때 개선사항들은 modular하여 개별적으로 조립이 가능하다. 이후 전략들은 LDM 확장으로 구현됬지만 대부분 pixel-space counterpart에도 적용가능하다.

![[Pasted image 20260906030302.png]]

## Architecture & Scale

DM이 image synthesis에서 가장 강력한 generative model임을 보인후에 convolutional UNet 구조는 가장 지배적인 구조로 자리잡았다. 그러나 foundational DM이 발전하며 underlying architecture은 지속적으로 변화해왔다. 구체적으로는 self-attention과 개선된 upscaling layer을 추가하는 방식부터 cross-attention을 거쳐 순수 transformer 기반 구조에 이르렀다.

![[Pasted image 20260906030313.png]]

높은 feature level의 UNet에서는 basic한 특징을 뽑아내기 때문에 효율성을 위해 transformer block을 생략하고 더 낮은 level에서는 2개 10개의 block을 사용한다. 또한 가장 낮은 8x downsampling은 완전히 제거하여 공간 정보를 보존시킨다.

text conditioning에서는 OpenCLIP ViT-bigG와 CLIP ViT-L의 output 이전 hidden layer의 output을 feature channel 방향으로 concatenate한다. 이때 이전 layer를 쓰는 이유는 마지막 layer는 최종 embedding `<EOS>`를 만들기 좋은 방향으로 조정되지만 우리가 필요한건 token-level semantic representation이기 때문이다. 또한 이것 이외에도 OpenCLIP model에서 얻은 pooled text embedding (`<EOS>`)를 model에 추가 conditioning한다.

## Micro-conditiong

conditioning LDM paradigm에서 2단계 구조로 인해 model을 train할때 최소 image size가 필요하다. 이 문제를 해결하는 주요 접근법은 2가지이다.

1. 특정 해상도보다 작은 모든 training image를 버리기

- training data를 상당 부분버려서 성능저하 및 generalization 저하

2. 너무 작은 image를 upscaling 하기

- upscaling artifact(부자연스러운 흔적)를 발생시키고 이것이 최종 output에 유입되어 sample이 흐릿해질 수 있다.

따라서 이미지 원본 높이와 너비를 추가적인 conditiong으로 model에 제공한다.

$c_{size} = (h_{original}, w_{original})$의 각 구성 요소는 Fourier feature encoding(주파수)을 사용해 독립적으로 embedding 한후에 하나의 vector로 연결해서 timestep embedding에 더하는 방식으로 model에 입력한다.

추론시에는 이 size-conditiong을 통해 사용자가 원하는 겉보기 해상도를 설정할 수 있다. 이때 모델은 conditioning c에 의존하는 image feature을 학습한다.

**Conditioning the Model on Cropping Parameters**

model training 중에 DL framework에서 batch를 구성하려면 tensor 크기가 동일해야하는데 이때 가장 짧은 변의 크기가 target size와 일치하도록 이미지를 resize한 후에 긴축에 따라 random crop을 한다. 하지만 이는 생성된 sample이 짤리는 효과를 보일 수 있다. 이 문제를 해결하기 위해서 crop c를 sampling 하고 Fourier feature embedding을 통해서 embedding후에 일반적인 관행에 따라 data를 추가적인 conditioning parameter로 사용한다. 이때 이 기법은 LDM으로 한정되지 않고 모든 DM에 사용가능하다. 추가할때 우선 crop-conditiong과 size-conditioning을 결합하고 이후에 timestep embedding에 더한다.

## Multi-Aspect Training

실제 dataset에는 그기와 aspect-ratio가 매우 다양한 이미지가 포함되어 있다.  
Text-to-image의 ouput은 정사각형 이미지이지만 landscape또는 Portrait 형식의 화면이 널리 사용되고 보급되고 있다는걸 고려해야한다.  
따라서 model이 여러 aspect-ratio을 동시에 처리할 수 있도록 finetuning한다.  
이때 서로다른 aspect ratio를 가장 비슷한 bucket에 넣고 높이와 너비를 64의 배수로 변경하여 픽셀수가 가능한한 $1024^2$에 가깝게 유지한다.

Optimization 중에는 동일한 bucket의 이미지끼리 training batch를 구성하며 각 training step마다 bucket size를 다르게 사용한다. 또한 model에는 bucket size를 Fourier space에 embedding 한뒤 conditioning으로 concetnate한다. 이때 size-condtiong의 뒤에 넣는다.

실제로 pretrained 단계에서는 단순한 crop을 사용하지만 fine-tuning 단계에서 bucket을 사용하여 다양한 해상도가 가능하도록 한다.

## Improved Autoencoder

autoencoder을 개선함으로서 국소적이고 high-frequency한 detail을 향상 시킬 수 있다. 이를 위해 기본적인 Stable Diffusion에 사용된 동일한 autoencoder을 더 큰 batch-size(9 → 256)로 training하고 추가적으로 EMA를 이용해서 weigth를 추적하여 inference나 validation 순간에 사용

$$  
θ_{EMA}←βθ_{EMA}+(1−β)θ  
$$

## Putting Everything Together

최종적으로 multi-stage procedure로 training한다.

- autoencoder와 discreate-time diffusion schedule t=1000
- 전처리를 통해서 training image를 256x256으로 만들고 batch size는 2048의 학습과정을 60만번 반복한다.
- 전처리를 통해서 training image를 512x512 이미지를 사용해서 20만번 반복 학습한다
- 마지막으로 offset-noise와 multi-aspect training을 결합해 $1024^2$개의 다양한 aspect ratio에서 모델을 학습한다 (fine-tuning)
    - offset-noise : global signal을 학습하기 위해서 gaussian noise에 전체에 공통으로 적용되는 작은 noise 추가, 논문에서는 0.05
    - 연산 효율성과 학습 안정성을 위해서 작은 픽셀수부터 순차적으로 학습

**Refinement Stage**

base model이 때때로 local quality가 낮은 sample을 생성한다. quality를 향상하기 위해 동일한 latent space (같은 autoencoder)에서 별도의 LDM을 training하며 따라서 높은 quality와 resolution에 특화되어 있다. base model sample에 noising-denoising을 적용해서 조금 망가트린다. 이후 처음 200개의 단계에서 noise scale을 진행한다.

# Future Work

이 연구는 text-to-image를 위한 foundation model Stable Diffuison의 개선 사항에 대한 preliminary 분석을 제시한다. 또한 다음에서는 model을 개선시킬 수 있다.

- single stage : 현재 SDXL에서 가장 우수한 sample을 생성하려면 추가적인 refinement model을 사용하는 two-stage approach가 필요한데 이때문에 접근성과 속도가 저하된다. 향후에 더 우수한 quality를 제공하는 방법을 연구해야한다.
- Text synthesis : model의 scale과 더 큰 text encoder은 text rendering capability 향상에 도움이 되지만 byte-level tokenizer또는 model을 크게 scaling 하는것으로 text synthesis를 더욱 개선할 수 있다.
- Architecture : transformer-based 구조도 실험했지만 즉각적인 이득을 얻지 못했다. 하지만 추가적은 tuning을 통해 개선을 기대할만하다.
- Distillation : 추론 cost가 증가하기 때문에 이 계산을 줄여야한다.

# Appendix

## Limitations

1. model이 사람의 손과 같은 복잡한 구조를 합성할 때 어려움을 겪을 수 있다.  
    따라서 추가적인 scaling 및 training 기법이 필요함을 시사한다. 이렇게 되는 원인은 variance가 높기 때문일 수도 있다.
2. image는 놀라운 사실성을 달성했지만 완벽히 사진과 같지는 않다. 아주 작은 texture 변화와 세부적인 특징은 생성된 이미지에 제대로 나타나지 않을 수 있다.
3. dataset에 의존하는 경향이 심하므로 의도치 않게 사회적, 인종적 편향을 도입할 수도 있다.
4. concept bleeding(여러 object나 subject가 겹침)이 일어날 수 있다.

결론적으로 우리 model은 image synthesis에서 주목할 만한 강점을 보이지만, 일정한 한계에서 자유롭지는않다. 복잡한 구조의 합성, 완벽한 photorealism 달성, 편향의 추가적인 해결, concept bleeding 완화, text rendering 개선과 관련된 과제는 향후 연구와 optimization을 위한 방향을 제시한다.

## Diffusion Model

$𝑝_{data}(x_0  )$을 실제 data 분포라고 하고 iid gaussian noise를 추가한 분포를 $p(x;σ)$라고 한다. 이때 $𝜎_{max}$가 무한히 커지면 $p(x;σ_{max}​)≈N(0,σ_{max}^2​I)$가 된다. 따라서 샘플을 구하는 대신 Gaussian noise를 뽑아도 된다. 이를 순차적으로 denoise한다. 이때 $x_M, \sigma_i < \sigma_{i+1},\sigma_M = \sigma_{\max}$이다. DM이 잘 train되고 $\sigma_0 = 0$일때 $x_0$는 data에 따른 분배를 가진다.

$$  
d\mathbf{x} = -\dot{\sigma}(t)\sigma(t)\nabla_{\mathbf{x}} \log p(\mathbf{x}; \sigma(t))\,dt  
$$

$\nabla_{\mathbf{x}} \log p(\mathbf{x}; \sigma(t))\,$score function(data-like 영역으로 이동)이고 $\sigma(t)$는 schedule이다.

$$  
d\mathbf{x}=\underbrace{-\dot{\sigma}(t)\sigma(t)\nabla_{\mathbf{x}}\log p(\mathbf{x};\sigma(t))\,dt}_{\text{Probability Flow ODE}}-\underbrace{\beta(t)\sigma^2(t)\nabla_{\mathbf{x}}\log p(\mathbf{x};\sigma(t))\,dt+\sqrt{2\beta(t)}\,\sigma(t)\,d\mathbf{w}_t}_{\text{Langevin diffusion component}}  
$$

Probability Flow ODE : score을 알려주는 방향으로 연속적으로 이동시켜 noise 분재 전체를 data 분배로 변환하는 deterministic한 운동방정식

Langevin Diffusion Component :  
Score drift : sample을 high-density 영역으로 끌어당김  
Random Diffusion : sample을 random한 방향으로 움직여 stochasticity 제공

#### **Training**  
score function을 위한 model을 학습하는 것이 목표이다. $\nabla_{\mathbf{x}}\logp(\mathbf{x};\sigma) \approx  s_{\theta}(\mathbf{x};\sigma)=\frac{D_{\theta}(\mathbf{x};\sigma)-\mathbf{x}}{\sigma^2}$이고 $\mathbf{x}_0 + \mathbf{n}, \quad\mathbf{x}_0 \sim p_{\text{data}}(\mathbf{x}_0), \quad\mathbf{n} \sim \mathcal{N}(0,\sigma^2 I_d)$ 일때 decoder을 학습시켜 $Dθ​(x;σ)≈x0​$을 만들려고 한다.  
이는 DSM을 통해서 training한다.

$$  
\mathbb{E}_{(\mathbf{x}_0,\mathbf{c})\sim p_{\text{data}}(\mathbf{x}_0,\mathbf{c}),\,(\sigma,\mathbf{n})\sim p(\sigma,\mathbf{n})}\left[\lambda_{\sigma}\left\|D_{\theta}(\mathbf{x}_0+\mathbf{n};\sigma,\mathbf{c})-\mathbf{x}_0\right\|_2^2\right]  
$$

**Classifier-free guidance**  
conditional model과 unconditional model의 예측을 혼합하여 conditioning signal c 방향으로 유도하는 방식이다.

$$  
D^w(\mathbf{x};\sigma,\mathbf{c})=(1+w)D(\mathbf{x};\sigma,\mathbf{c})-wD(\mathbf{x};\sigma)  
$$

즉 conditional signal c를 무작위로 null embedding으로 대체한다.  
이를 통해 sampling quality를 상승하지만 다양성이 감소한다.

## Multi‑Aspect Training Hyperparameters

![[Pasted image 20260906030659.png]]

## Pseudo-code for Conditioning Concatenation along the Channel Axis

```text
1 from einops import rearrange
2 import torch
3
4 batch_size =16
5 # channel dimension of pooled output of text encoder (s)
6 pooled_dim = 512
7
8 def fourier_embedding ( inputs , outdim =256 , max_period =10000) :
9 """
10 Classical sinusoidal timestep embedding
11 as commonly used in diffusion models
12 : param inputs : batch of integer scalars shape [b ,]
13 : param outdim : embedding dimension
14 : param max_period : max freq added
15 : return : batch of embeddings of shape [b, outdim ]
16 """
17 ...
18
19 def cat_along_channel_dim (
20 x : torch . Tensor ,) -> torch . Tensor :
21 if x . ndim == 1:
22 x = x [... , None ]
23 assert x . ndim == 2
24 b , d_in = x . shape
25 x = rearrange (x , "b din -> (b din )")
26 # fourier fn adds additional dimension
27 emb = fourier_embedding ( x )
28 d_f = emb . shape [ -1]
29 emb = rearrange ( emb , "(b din) df -> b (din df)",
30 b =b , din = d_in , df = d_f )
31 return emb
32
33 def concat_embeddings (
34 # batch of size and crop conditioning cf. Sec . 3.2
35 c_size : torch . Tensor ,
36 c_crop : torch . Tensor ,
37 # batch of aspect ratio conditioning cf. Sec . 3.3
38 c_ar : torch . Tensor ,
39 # final output of text encoders after pooling cf. Sec . 3.1
40 c_pooled_txt : torch . Tensor , ) -> torch . Tensor :
41 # fourier feature for size conditioning
42 c_size_emb = cat_along_channel_dim ( c_size )
43 # fourier feature for size conditioning
44 c_crop_emb = cat_along_channel_dim ( c_crop )
45 # fourier feature for size conditioning
46 c_ar_emb = cat_along_channel_dim ( c_ar )
47 # the concatenated output is mapped to the same
48 # channel dimension than the noise level conditioning
49 # and added to that conditioning before being fed to the unet
50 return torch . cat ([ c_pooled_txt ,
51 c_size_emb ,
52 c_crop_emb ,
53 c_ar_emb ] , dim =1)
54
55 # simulating c_size and c_crop as in Sec. 3.2
56 c_size = torch . zeros (( batch_size , 2) ) . long ()
57 c_crop = torch . zeros (( batch_size , 2) ) . long ()
58 # simulating c_ar and pooled text encoder output as in Sec . 3.3
59 c_ar = torch . zeros (( batch_size , 2) ) . long ()
60 c_pooled = torch . zeros (( batch_size , pooled_dim ) ) . long ()
61
62 # get concatenated embedding
63 c_concat = concat_embeddings ( c_size , c_crop , c_ar , c_pooled )

```