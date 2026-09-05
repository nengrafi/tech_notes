# Abstract

기존에 DMs는 DAE (노이즈를 넣어서 생성)를 순차적으로 여러번 사용하여 retraining 없이 이미지 생성 과정을 제어한다. 이때 DMs는 denosing step에서 어떤 방향으로 갈지 guidance를 제시할 수 있기 때문에 retrain할 필요가 없다. 기존의 model은 pixel space (3x512x512)에서 동작하므로 최적화를 위해서는 GPU와 inference 비용이 크다. 본 연구는 pretrained된 autoencoder(입력 → 압축 → 복원)의 latent space에서 DMs를 적용한다. 이를 통해 너무 많은 detail을 버리지 않으면서 계산 복잡도가 감소하였고 그 결과 더 좋은 visual fidelity를 얻을 수 있었다. 또한 cross-attention layer를 도입함으로서conditional generator로 변환하고 또한 convolutional 방식에서 고해상도 합성을 가능하게 한다 (해상도가 달라도 같은 weight 사용가능) . 이 연구에서 LDMs는 image inpainting, class-conditional image synthesis에서 최고 성능을 달성했다. 또한 piexel 기반 DMs에 비해서 자원 요구량을 크게 줄인다.

# Introduction

AR확장 likelihood 기반 model

- 복잡하고 자연스러운 고해상도 합성
- GANs에서 일어나는 mode collapse (하나 위주로만 생성) , training instablility (두 모델 사이의 불안정)이 보이지 않음
- parameter sharing(계속 같은 모델 사용)을 이용해서 적은 parameter로 복잡한 이미지 구현가능

GANs

- Adversarial training 사용 = Generator 가짜 이미지 생성 Discriminator 분류
- 다양성이 제한된 데이터에 한정되어 좋은 결과가 나옴

Denoising autoencoder hierarchy diffusion model

- 계층별로 다른게 아닌 다른 timestep이 들어감

Unconditioal DMs

- Inpainting : 이미지 일부가 비어있고 거기에 생성
- Colorization : 밝기 구조에 제한을 둠
- Stroke-based synthesis : 사람이 그른 stroke를 만족하는 이미지 생성

Reweighted variational objective

- Loss에서 timestep별 weight를 바꾸거나 sampling 확률을 바꿈
- 초기 denoising step을 under sampling 하여 mode-covering(모든 영역 커버 하려함)으로 인한 인간이 인지하기 어려운 세부정보를 modeling 하는데 과도한 capacity를 낭비하는 것을 줄이려 하지만 여전히 계산비용이 크다.
- 여전히 고차원 space에서 gradient computation이 필요하기 때문이다.

→ training과 sampling 모두 계산 복잡도를 낮춰야함 근데 성능 저하는 시키면 안됨

Learning

1. Perceptual Compression : 주어진 이미지를 잘 압축하고 복원
2. semantic Compression : Diffusion model이 latent의 distribution 학습

Rate-Distortion Trade-off

- text-to-image는 transformer를 연결하여 embedding된 데이터를 전달

→ Autoencoder을 한번만 train 하면 재사용 가능

1. 이 연구는 단순 transformer 기반의 접근법이 아닌 더 높은 차원의 데이터로 더 원할하게 확장되므로 고해상도 합성에 효율적을 활용 가능하다.
2. 이 연구는 여러 task와 dataset에서 경쟁력 있는 성능을 달성하며 계산비용, inference 비용을 줄인다.
3. 이 연구는 reconstruction 능력과 generative 능력 사이의 정교한 weight 조정이 필요치 않아 보인다. 또한 latent space에 필요한 regularization도 적다.
4. 이 연구는 cross-attention에 기반한 범용 conditioning mechanism을 설계하여 multi-modal training을 가능하게 한다.

## Related Work

문제점

GANS : 고해상도 이미지를 효율적으로 sampling 할 수 있지만 optimization이 어렵고 전체 data distribution을 포착하기 어려움

likelihood : optimization이 안정적으로 수행

VAE, flow-based model : sample quality가 GAN에 미치지 못함

ARM : density estimation에서 성능이 뛰어나지만 큰 모델과 순차적인 sampling 과정으로 저해상도 이미지로 제한된다

two-stage 접근법 : latent image space를 modeling 하는데 ARM 이용

DM : density estimation (가능성 분포의 밀도 추정)과 sample quality에서 SOTA  
backbone은 UNET, reweighted objective를 training에서 사용  
하지만 piexel space에서 평가하고 최적화하면 속도가 느리고 비용이 높음

Two Stage 접근법

VQ-VAE : Encoder로 Discrete latent token으로 변환 후 ARM을 통해 prior 학습  
text와 이미지의 경우 token으로 만든후 하나의 sequence 처럼 모델링  
conditionally invertible network를 활용하여 domain 사이의 transfer 제공

VQGAN : VQ-VAE에 Perceptual Loss랑 Adversarial Loss 포함  
pretrainned nn feature을 이용해서 loss 비교 및 discriminator를 통해서 autoencoder 학습 → trade-off 상태

LDM : convolutional backbone (병렬적) 덕분에 높은 차원에서 비용 적음, perceptual compression을 DM에 맡기지 않음

기존에는 encoder/decoder와 score-based prior을 공동으로 학습했지만 이때 전자의 경우에는 어려운 가중치 조절이 필요하고 후자의 경우에는 성능이 낮다.

## Method

Comperssive Learning과 Generative Learning 명시적 분리

1. 고차원 → 저차원 으로 인한 계산 효율상승
2. UNET에서 비롯된 inductive bias 활용, spatial structure에 효과적

→ 기존에 비해 압축수준 완화

1. 여러 genreative model에 범용적임, downstream apllication에도 사용가능

### Perceptual Image compression

단순히 L1, L2를 사용하면 blur(평균으로 섞임) 발생 →  
perceptual loss와 patch-based adeversarial objective 사용

perceptual loss : 이미지가 가진 high-level feature 비교

patch-based adeversarial objective : 작은부분 patch를 Discriminator가 판별

$$  
x \in \mathbb{R}^{H \times W \times 3}\\  
z = \mathcal{E}(x)\\  
z \in \mathbb{R}^{h \times w \times c}\\  
\tilde{x} = \mathcal{D}(z) = \mathcal{D}(\mathcal{E}(x))\\  
f = \frac{H}{h} = \frac{W}{w}\\  
f = 2^m, \qquad m \in \mathbb{N}  
$$

Autoencoder 내에서 reconstruction만 잘 나오도록 학습하기 때문에 encoder에서 나오는 latent image을 scaling 해줘야한다. 따라서 두가지 Regularization을 실험한다.

1. KL-reg
    
    # $$  
    D_{\mathrm{KL}}\left(q(z\mid x)\,\|\,\mathcal{N}(0,I)\right)\\  
    \mathcal{L}
    
    \mathcal{L}_{\mathrm{reconstruction/perceptual}}  
    +  
    \mathcal{L}_{\mathrm{adversarial}}  
    +  
    \lambda_{\mathrm{KL}}\mathcal{L}_{\mathrm{KL}}
    
    $$
    

- hyperparameter를 이용해서 penalty 조정

1. VQ-reg

- 이미 정해진 codebook vector중 하나를 골라 continous → discrete
- quantization을 decoder 쪽 구성요소로 취급
- convolutioanl encoder을 써서 가까운 영역끼리 실제로 비슷한 정보 공유

기존에는 space z를 1D로 flatten 한후 autoregressive 하게 modeling하여서 내부 구조를 무시했지만 이 연구는 x의 세부 사항을 더욱 자세히 보존한다.

### Latent Diffusion Models

DM은 정규분포를 따르는 변수들을 점차 denoising 하여 p(x)를 학습하도록 설계된 model (Gaussian Noise)

p(x)에 대해서 variational lower bound를 두고 weight를 각각 변형한다. 이는 dennoising score-matching과 유사하다.

같은 parameter를 공유하며 sequence로 해석이 가능하다. 또한 x_t의 denoised 변형을 예측하도록 training된다.

$$  
\mathcal{L}_{\mathrm{DM}}=\mathbb{E}_{x,\epsilon \sim \mathcal{N}(0,1),t}\left[\left\|\epsilon - \epsilon_{\theta}(x_t,t)\right\|_2^2\right]  
$$

이때 1 ~ T는 균일하게 sampling 된다.

- UNet으로 2D convolutional layer 구성
- reweighted bound를 사용하여 관련성 높은 부분에 objective 집중

![[Pasted image 20260906031204.png]]

neural backbone은 time-conditional UNET으로 구현되고 밑의 공식을 통해서 z_t를 효율적으로 얻을 수 있다.

$$  
z_t=\sqrt{\bar{\alpha}_t}\,z+\sqrt{1-\bar{\alpha}_t}\,\epsilon  
$$

또한 z_0를 마지막에 decoder에 넣어 이미지로 만들어준다.

### Conditioning Mechanisms

입력 y를 통해서 synthesis process를 제어하는 기반을 마련하지만 image synthesis에서 class label, blurred 외에 conditioning과 결합하는 것은 아직 연구되지 않았다.

이를 해결하려 cross-attention mechanism을 이용해서 더욱 유연한 conditional image gererator로 변환한다. domain-specific encoder $\tau_\theta(y)\in \mathbb{R}^{M \times d_\tau}$를 도입하고 이 표현을 cross-attention layer를 통해 UNet의 intermediate layer로 mapping된다.
 $$  
\operatorname{Attention}(Q,K,V)

\operatorname{softmax}  
\left(  
\frac{QK^{T}}{\sqrt{d}}  
\right)  
\cdot V,  
\quad  
\text{with }  
Q = W_Q^{(i)} \cdot \varphi_i(z_t),  
\quad  
K = W_K^{(i)} \cdot \tau_\theta(y),  
\quad  
V = W_V^{(i)} \cdot \tau_\theta(y)  
$$

M : token개수  
d : token의 embedding diemension

Query : 이미지  
Key, Value : conditional

$$  
\varphi_i(z_t) \in \mathbb{R}^{N \times d_\epsilon^i}\\  
W_V^{(i)} \in \mathbb{R}^{d \times d_\epsilon^i}\\  
W_Q^{(i)} \in \mathbb{R}^{d \times d_\tau}\\  
W_K^{(i)} \in \mathbb{R}^{d \times d_\tau}  
$$

이때 $\tau_\theta$와 $\epsilon_\theta$는 공동의로 최적화 된다. $\tau_\theta$로 domain-specific로 parameterize 가능하다.

$$  
\mathcal{L}_{\mathrm{LDM}}:=\mathbb{E}_{\mathcal{E}(x),\,y,\,\epsilon \sim \mathcal{N}(0,1),\,t}\left[\left\|\epsilon-\epsilon_\theta\left(z_t,\,t,\,\tau_\theta(y)\right)\right\|_2^2\right]  
$$

# Experiments

## Figure 1.

spatial data에 대해서 downsampling

- downsampling을 덜 강하게 해서 달성 가능한 품질 상한을 높임

![[Pasted image 20260906031306.png]]

inductive bias (모델 구조 자체가 특정 종류의 데이터를 잘 다루도록 가진 구조적 성향)

- spatial data에 대한 좋은 inductive bias
- PSNR : 원본과 얼마나 비슷한지 R-FID : 얼마나 두 이미지 집합이 비슷한지 (낮)

LDM을 이용해서 적게 downsampling해서 detail을 보존해도 된다. f=4에서 최고
![[Pasted image 20260906031244.png]]

## Figure 2.

![[Pasted image 20260906031254.png]]

## Paper

training과 inference에서 pixel-based DM과 비교하여 model의 이점 분석, VQ-regularized latent space에서의 LDM이 때떄로 우수한 sample quality 달성

### On Perceptual Compression Tradeoffs

$f∈{{1,2,4,8,16,32}}$일때 latent로 압축하고 diffusion을 수행했다. 이외의 모든 조건은 동일하게 설정했을때 너무 적게 downsampling 하면 진행이 매우 느리고 지나치게 크게 downsampling하면 training steps 이후의 fidelity가 정체된다. f가 4~16 사이 일때는 적절한 균형을 이룬다.

![[Pasted image 20260906031314.png]]

LDM -1과 LDM 4, LDM-8으 비교했을때 FID가 낮고 throughput도 높다

![[Pasted image 20260906031319.png]]

### Image Generation with Latent Diffusion

CelebA-HQ, FFHQ, LSUN-Chrurches, -Bedrooms에서 256^2 images에 대한 unconditional models를 training 했다. 이때 1. sample quality FID 2. Data manifold coverage를 위해 Precison(sample이 실제에 들어오는 양)-Recall(실제 dataset의 다양성에 들어오는양)을 사용했다.

- CelebA-HQ SOTA
- LSGM(jointly training)보다 우수한 성능

![[Pasted image 20260906031336.png]]

![[Pasted image 20260906031333.png]]

### Conditional Latent Diffusion

#### Transformer Encoders for LDMs

classifier free model : condition 없는 버전과 있는 버전을 두번 넣어서 둘의 차이를 더해줌

![[Pasted image 20260906031346.png]]

text-to-image image modeling

- LAION-400M, 1.45B parameter KL-regularized LDM
- BERT-tokenizer 사용, transfomrer로 encoder 구현, multi-head cross-attention으로 UNet에 전달
- MS-COCO validation set으로 평가, AR, GAN-based methods 보다 우수한 성능
- CFG를 적용하면 SOTA AR및 diffusion models과 대등한 성능

또한 유연성 분석을 위해 OpenImages에서 image pre-training가 COCO로 fine-tuning한다. 이때 SOTA보다 우수한 성능이 나온다.

#### Convolutional Sampling Beyond 2562

conditioning 정보를 LDMs 입력에 channel 방향으로 concatenating하여 범용적으로 사용

Semantic synthesis

- semantic map downsampling을 f=4 model의 latent image representation과 concatenating함 → megapixel 수준의 이미지
- super-resoluation model과 inpainting model을 적용해서 대형 이미지 생성
- 이때 signal과 noise의 비율이 latent에 의해 좌우된다

f=4 KL-reg와 각 성분별 표준편차로 scaling 한 재조정 버전으로 학습

image sythesis에서는 더 큰 scale로 일반화 가능

### Super‑Resolution with Latent Diffusion

고해상도 이미지 생성시에 저해상도 이미지를 conditioning에 concentation

첫번째 실험

- Bicubic interpolation 4Xdownsampling low-image, SR3 data processing pipeline 사용
- OpenImages로 pretrained된 f=4 autoencoder 사용, conditioning으로 low image를 넣는다.
- image regression model이 PSNR, SSIM은 가장 높았지만 high-frequency detail을 알아내기 힘들어 사람의 인식과 맞지 않았다.
- post-hoc guiding mechanism을 통해 PSNR과 SSIM을 향상시키고 perceptual loss를 통해 image-based guider를 구현했다
![[Pasted image 20260906031354.png]]

![[Pasted image 20260906031357.png]]

### Inpainting with Latent Diffusion

이미지가 일부 손상되었거나 content를 대체하기 위해 mask영역을 새로운 contenet로 채움

- 공간적으로 할당된 conditioning information을 concatenation

![[Pasted image 20260906031402.png]]

비교 모델 : LaMa protocol

- pixel based model 보다 2.7배의 speed-up및 1.6배의 FID 향상

![[Pasted image 20260906031405.png]]

- LPIPS는 더 안좋지만 사람의 인지 부분에서 좋은 결과 달성
- 해상도를 올렸더니 attention의 민감성 때문에 품질 차이 발생 → 잠시 fine-tuning 하니 해결됨

# Limitations & Societal Impact

### Limitation

- 순차적인 sampling 과정은 여전히 GANs보다 느리다
- 높은 정밀도가 필요한 경우에는 적절한지 의문이 제기될 수 있다

### Social Impact

- training및 inference 비용을 줄이는 탐구법이 대중화 될 수 있다
- 조작된 데이터를 생성하고 유포하는 일이 더욱 쉬워진다
- two-stage 접근법이 데이터를 어느정도 잘못 나타내는지는 연구 문제

# Conclusion

이 연구는 quality를 저하시키지 않으며 training 및 sampling 효율을 크게 향상하는 간단하고 효율적인 방법인 LDM을 제시했다. 이를 바탕으로 corss-attention conditioning mechanism을 적용한 실험을 통해 구체적인 구조없이 다양한 상태의 image synthesis task에서 SOTA와 비교해 유리한 결과를 얻을 수 있다.