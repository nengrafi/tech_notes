# Abstract

기존의 text-to-image model은 subject를 유지하며 서로 다른 context에서 새로운 표현을 synthesis하는 능력이 부족했다. 따라서 이 논문은 DM을 personalization 하기 위한 새로운 접근법을 제시한다. 이때 pretrained model에 몇장의 이미지를 입력으로 줘서 fine-tuning하여 고유 identifier와 object를 연결한다.

이때 autogenous class-specific prior preseravtion loss와 semantic prior을 활용하여 다양한 장면을 생성할 수 있다. 또한 핵심 feature은 보전하면서 subject recontextualization(같은 대상을 새로운 context에 배치), Text-guided view synthesis(text prompt로 시점을 지정해서 다른 view에서 생성), artistic rendering (indentity는 유지하면서 표현 style을 바꿈)와 같은 어려운 과제들에 적용 가능하다.

# Introduction

최근 개발된 대규모 text-to-image model은 prompt 기반으로 다양한 이미지를 syntehsis할 수 있게 해준다. 이 모델의 주된 장점중 하나는 image-caption pair(image+특징) 집합에서 학습한 강력한 semantic prior이다. 하지만 이때 동일한 대상을 서로 다른 맥락에서 synthesis하는 능력은 부족하다. ouput domain의 표현력이 제한적이기 때문이다.

![[Pasted image 20260906051244.png]]

이 연구는 model을 personalization 하기 위해서 새로운 접근법을 제시한다. 이때 목표는 model의 language-vision dictionary를 확장하여 특정대상과 새로운 단어를 연결하도록 하는것이다. 새로운 dictionary를 model에 embedding 함으로서 이 단어를 이용해 대상의 핵심 feature을 보존하며 서로 다른 장면에 맥락화된 새로운 photorealistic image를 synthesis 할 수 있다. 이를 위해 rare token identifier로 대상을 표시하고 pretrained model을 fine-tuning한다.

입력이미지 + class name + 고유 identifier prompt를 이용해서 fine-tuning한다. language drift (class가 특정 instance와 연결되는 방식)을 방지하기 위해 embedding된 class에 semantic prior을 활용하고 대상과 동일한 class의 다양한 instance를 생성하여 학습에 사용하는 autogenous class-specific prior preservation loss를 사용한다. Ablation study(구성 요소를 바꿔보며 실험)을 이용하여 component의 기여도를 분석하고 대안적인 연구와 비교한다. 또한 user study(사람들에게 생성이미지를 보여주고 평가)를 사용해 fidelity를 분석한다.

이 접근법을 다양하게 적용하여 기존에는 해결하기 어려웠던 새로운 과제의 가능성을 연다. 또한 subject-driven generation을 다루는 최초의 기법이다.

이를 위해 서로 다른 context에서 촬용된 다양한 대상을 포함하는 새로운 dataset을 구축하고 생성된 결과의 subject fidelity와 prompt fidelity를 측정하는 새로운 evaluation protocol을 제안한다.

# Related work

**Image Composition**  
기존에는 주어진 대상을 새로운 background에 clone하여 장면에 융화시킨다. 새로운 composition을 고려하기 위해 3D reconstruction 기법(사진을 여러개 찍어서 3D object 생성 후 새로운 pose 생성)을 적용 할 수 있지만 이런 기법은 rigid object에 주로 사용되며 많은 image를 요구한다. 이때 scene integration(조명,그림자,접촉)과 새로운 장면을 생성할 수 없다.

**Text-to-Image Editing and Synthesis**  
텍스트 기반의 image manipulation은 GANs,CLIP과 같은 image-text representation과 결합하며 크게 발전하였다. 이러한 방법은 구조화된 시나리오에서는 잘 작동하지만, 대상이 다양한 데이터셋에서는 어려움을 겪을 수 있다.

VQ-GAN을 사양하고 다양한 데이터로 training 하여 이러한 문제를 완화할 수 있다. 다른 연구들은 DM을 활용하여 다양한 데이터셋에서 종종 SOTA를 달성한다. 대부분의 editing 접근법은 image의 global property 수정이나 local editing을 수행할 순 있지만 주어진 subject의 새로운 rendition을 생성할 수 없다. 대규모 text-to-image models은 image를 세밀하게 제어할 수 없고 텍스트 guidance만을 사용하여 전반에서 subject의 inentity를 일관되게 보존할 수 없다.

**Controllable Generative Models**  
Generative model을 제어하기 위한 다양한 접근법이 존재하며 그중 일부는 subjet-driven prompt-gudied image synthesis를 실현하는 방향이 될 수 있다. 한 연구에서는 이를 위해 수정영역을 제어하는 mask를 가정한다.  
Prompt-to-prompt는 input mask 없이 local, global editing을 수행하지만 이런 방법은 subject의 identity를 보존하며 새로운 sample을 생성하는데 한계가 있다.

GANs에서 pivotal Tuning은 inversion으로 찾은 latent를 pivot이라고 부르고 이걸 기준으로 generator을 fine-tuning한다. 이 연구를 확장에 face에 대한 GAN을 특정하게 fine-tuning하여 personalized하게 만들었다. 하지만 이 연구는 많은 image를 필요로 하며 face domain이 제한된다.

frozen text-to-image model(parameter update X)의 embedding space에 새로운 token을 도입하여 특징을 표현하고 이 personalized token embedding을 학습시킨다. 하지만 이 논문에서는 output domain에서 subject를 embedding할 수 있으므로 더욱 핵심적인 새로운 image를 생성할 수 있다.

# Method

text 없이도 특정 subject를 우연히 촬영한 소수의 image만이 주어졌을때 이 연구는 detail fidelity를 유지하면서 텍스트 prompt에 따라 variation된 subject의 이미지를 생성하는것이 목표이다. Input image에는 어떠한 제약도 두지 않으며 subject image는 다양한 context를 가질 수 있다.

## Text-to-Image Diffusion Models

DM은 Gaussian distribution에서 sampling한 변수가 점진적인 denoising을 수행하여 data distribution을 학습하도록 training되는 probabilistic generative model이다.

text-to-image에서는 latent $z_t := \alpha_t x + \sigma_t\epsilon$을 다음과 같이 denoising하도록 squared error loss를 이용해 training된다.

$$  
\mathbb{E}_{\mathbf{x},\mathbf{c},\epsilon,t}\left[w_t\left\|\hat{\mathbf{x}}_\theta\left(\alpha_t\mathbf{x}+\sigma_t\epsilon,\mathbf{c}\right)-\mathbf{x}\right\|_2^2\right]  
$$

## Personalization of Text-to-Image Models

output domain에 subject instance를 삽입하여 다양한 image 생성하는것이 과제이다. 이때 subject의 few-shot dataset을 사용해 fine-tuning 하는것이 하나의 방법이다.

GANs와 같은 generative model은 fine-tuning시에 overfitting과 mode-collapse(하나만 생성)가 유발되거나 target distribution(원하는 전체 데이터 분포)을 충분히 포착하지 못할 수 있기 때문에 주의가 필요하다. target distribution을 잘 포착하기 위한 연구가 진행되어 왔지만 target distribution과 유사한 image를 생성하는 것을 목표로 하여서 맞지 않다.

이때 diffusion loss를 사용한 fine-tuning에서는 prior을 잊거나 overfitting하지 않으면서 새로운 정보를 domain에 통합하는데 매우 뛰어나다는 특이한 결과를 관찰했다.
![[Pasted image 20260906051254.png]]

**Designing Prompts for Few-Shot Personalization**  
목표는 새로운 이름과 특정 대상을 한쌍으로 model에 등록하는 것이다. 이때 주어진 image의 상세한 description을 작성하는데 드는 부담을 피하기 위해 input image에 “a [identifier] [class non]”이라는 label을 부여한다. class non은 사용자가 제공하거나 classifier을 통해 얻을 수 있다. 또한 고유 subject에 class prior을 연결하기 위해 문장에 class descriptor을 사용한다. (이때 잘못되게 사용하면 train time과 language drift(subject 쪽으로 변질)가 증가하고 성능이 저하된다)

**Rare-token Identifiers**  
기존 영어 단어는 model이 해당 단어를 원래 의미와 분리해서 학습하고 결합해야 하기 때문이다.

따라서 임의의 문자를 선택하고 연결하여 희귀 identifier을 생성한다. 실제로 이런 tokenizer은 문자를 개별적으로 tokenization하여 model에서 이 문자들의 prior이 강할 수 있다.

따라서 이 논문에서는 vocab에서 희귀 token을 찾고 이 token을 text space로 역변환한다. 이때 Unicode character은 3개 이하여야 한다.

## Class-specific Prior Preservation Loss

subject fidelity를 최대화하기 위해서는 model의 모든 layer를 fine-tuning 하는것이다. 하지만 text embedding을 조건으로 하는 layer은 language drift(pre-trained 지식을 잃음) 문제를 야기한다. 또한 output diversity가 감소한다. 특히 오래 train한 경우에 자주 발생한다.

이를 완화하기 위해 autogenous class-specific prior preservation loss를 사용한다. 이는 few-shot fine-tuning에서 model이 자체 생성한 sample로 model을 supervise한다.

frozen pre-trained diffusion model이 $z_{𝑡_1}  
∼ 𝒩(0, I)$ 와 $c_{\mathrm{pr}} := \Gamma\left(f\left(\text{"a [class noun]"}\right)\right)$을 사용하여 데이터 생성

$$  
\mathbb{E}_{\mathbf{x},\,c,\,\epsilon,\,\epsilon',\,t}\left[w_t\left\|\hat{\mathbf{x}}_\theta\left(\alpha_t \mathbf{x} + \sigma_t \epsilon,\,c\right)-\mathbf{x}\right\|_2^2+\lambda w_{t'}\left\|\hat{\mathbf{x}}_\theta\left(\alpha_{t'} \mathbf{x}_{\mathrm{pr}}+\sigma_{t'} \epsilon',\,c_{\mathrm{pr}}\right)-\mathbf{x}_{\mathrm{pr}}\right\|_2^2\right]  
$$

# Experiments

## Dataset and Evalution

**Dataset :**

- 고유한 object와 pet을 포함한 30개의 subject
- 25개의 prompt
    - recontextualization prompt 20개, property modification prompt 5개
- live subject/pet prompt 25개
    - recontextualization prompt 10개
    - accessorization prompt 10개
    - property modification prompt 5개

**Evalution :**

각 subject와 prompt마다 4개의 이미지를 생성해 3000개의 이미지를 얻음

**Evaluation Metrics :**

- 이미지 보존도인 subject fidelity : CLIP-I, DINO metric 계산
    - CLIP-I : 실제 이미지 CLIP embedding 사이의 pairwise cosine similarity 평균
    - DINO :
        - 생성이미지와 실제이미지 VIT-S/16 DINO embedding 사이의 pairwise cosine similarity 평균
        - 구조적으로 동일한 class subject간의 차이를 반영
        - self-supervised visual representation learning
- prompt fidelity : prompt와 이미지 CLIP embedding 사이의 cosine similarity → CLIP-T

## Comparisons

Textual Inversion과 비교함

![[Pasted image 20260906051302.png]]

User Study 수행 (사람들에게 비교 요청)

![[Pasted image 20260906051305.png]]

## Ablation Studies

PPL을 사용한 경우와 사용하지 않은 경우로 나눠서 fine-tuning

- 생성 이미지와 실제 이미지 사이의 DINO 평균을 계산하여 PRES를 구함
- PRES이 높을수록 prior이 collapse된거임
- 동일한 subject에 대해 동일한 prompt로 생성한 이미지 사이에 LPIPS cosine similarity 평균을 사용해 DIV 계산
- DIV가 높을수록 diversity 높음

→ 더 다양한 pose와 articulation, 덜 overfit함

**Class-prior Ablation**

- class noun 사용 X : class prior 사용 X및 잘못된 smaple 생성
- 무작위로 sampling한 잘못된 class noun : subject와 충돌이 발생하여 일그러진 subject 생성
- 올바른 class noun 사용 : prior 반영및 subject에 fit함

## Applications

**Recontextualization**  
: 서로 다른 context에서 특정한 subject의 새로운 이미지 생성

**Art Renditions**  
: subject의 예술적 redition(재해석)을 생성  
style뿐만 아니라 structure을 변화시킬 수 있음

**Novel View Synthesis**  
: 새로운 카메라 viewpoint에서 subject를 render

**Property Modification**  
: subject의 identity는 유지하며 property만 변화시키는 것

![[Pasted image 20260906051313.png]]

## Limitations

![[Pasted image 20260906051318.png]]

(a) : 매우 드문 context  
pretrained diffusion model이 원래 이런 조합을 거의 학습하지 못함

(b) : subject appreance가 묶여서 학습

(c) : overfitting

- 드문 subject의 경우에는 다양한 지원이 어려움
- subject fidelity도 변동성이 있으며 model prior 강도와 semantic modification 복잡성에 따라서 없던 특징이 추가될 수도 있다.

# Conclusions

소수의 subject 이미지와 텍스트 prompt의 guidance를 사용해 subject의 새로운 context를 합성하는 접근법을 제시하였다. 이때 subject를 고유한 identifier에 binding 하여서 주어진 subject instance를 text-to-image diffusion model의 ouput domain에 embedding 한다. 이때 3-5장의 이미지에서도 작동하므로 활용 가능성이 무궁무진하다. 동물과 사물을 대상으로 한 다양한 응용사례에서 실제 이미지와 구별하기 어려운 결과를 얻었다.