## Abstract

Adversarial examples는 dataset에 perturbation을 적용하여 높은 확률로 잘못된 정답을 출력

- linear한 nn의 특징이 주된 원인
- 서로 다른 architecture와 training set에서도 일반화 가능
- Adversarial training을 통해서 MNIST dataset의 test set error 감소

## Introduction

#### 기존

- Deep nerual network의 극단적인 non-linear
- 불충분한 model averaging
    - 하나의 모델에만 의존하는 문제
- Regularization이 부족해서 생기는 문제

#### 논문

nn의 linear한 특징만으로 설명 가능하다고 주장

- 기존 Regularization에 비해서 취약성을 유의미하게 감소시킴
    - non-linear 모델로 변경
- 더 강력한 optimization method를 설계하여 더욱 non-linear한 모델을 학습시켜서 trade-off에서 벗어남
- linear한 모델은 Adversial attack에 취약하지만 non-linear하면 학습 난이도가 상승함

## Model

### THE LINEAR EXPLANATION OF ADVERSARIAL EXAMPLES

input feature의 precision은 제한되어 있기 때문에 perturbation이 precision 보다 작다면 적대적 입력과 그냥 입력이 서로 다르지 않아야 한다.

$$  
\|\eta\|_{\infty} < \epsilon\\  
w^{\mathsf T}\tilde{x}=w^{\mathsf T}x+w^{\mathsf T}\eta\\  
\qquad\eta=\operatorname\epsilon{sign}(w)\\  
\qquad\epsilon mn.  
$$

perturbation이 activation을 wTn만큼 증가시키는 양을 최대화하려면 n = sign(w)으로 설정해야 한다. (이때 n은 max norem constraint) w의 차원이 n이고 weight vector의 한 원소의 평균크기가 m이라면 activation은 $\epsilon mn$ 만틈 증가한다. 이때 n이 클수록 (고차원) input에 변화를 가하여 output이 크게 변화한다. 특히 linear model은 신호의 크기보다 weight와 가장 밀접한 신호에 주의를 기울인다. 즉 adversarial perturbation은 weight와 가장 밀접한 신호를 가진다. 이 설명을 통해서 고차원 linear 환경에서 adversial perturbation이 발생하는 것을 알 수 있다.

- Softmax regression 역시 linear base이므로 취약함

#### LINEAR PERTURBATION OF NON-LINEAR MODELS

nn이 너무나도 linear하기 때문에 adversarial perturbation에 저항하기 힘들다고 가정한다. 때문에 저비용의 analytical perturbation이 neural network에 손상을 줄 수 있다.

![[Pasted image 20260906032108.png]]

FGSM

const function을 작은 범위에서 직선으로 근사하여 linearization하면 최적의 perturbation을 구할 수 있다. 이를 fast gradient sign method라고 한다.

$$  
J(\theta,x+\eta,y)\approx J(\theta,x,y)+\eta^{T}\nabla_xJ(\theta,x,y)\\  
\eta=\epsilon\operatorname{sign}\left(\nabla_xJ(\theta,x,y)\right)  
$$

backpropagation을 이용해서 효율적으로 계산이 가능하다. 또한 학습된 network를 단순히 분석하는 방법으로도 유용하다.

#### ADVERSARIAL TRAINING OF LINEAR MODELS VERSUS WEIGHT DECAY

logistive regression의 경우, 내부가 linear하기 때문에 FGSM이 정확하다.

$$  
P(y=1)=\sigma(w^Tx+b)\\  
J = \mathbb{E}_{x,y\sim p_{\mathrm{data}}}\left(\zeta\left(-y(w^Tx+b)\right)\right)\\  
\zeta(z)=\log(1+\exp(z))  
$$

이를 통해서 x의 worst-case adversarial peturbation으로 학습시키는 방식을 유도할 수 있다. 이때 y가 -1혹은 1이기 때문에 gradient sign은 단순히 -sign(w)가 된다. (n구하는 식에 대입)  
따라서 밑의 값을 최소화한다.

$$  
w^T\operatorname{sign}(w)=\|w\|_1\\  
w^Tx_{\mathrm{adv}}+b  
\\  
=w^T\left(x-\epsilon\operatorname{sign}(w)\right)+b  
\\  
=w^Tx-\epsilon w^T\operatorname{sign}(w)+b\\  
\mathbb{E}_{x,y\sim p_{\mathrm{data}}}\left[\zeta\left(y(\epsilon\|w\|_1-w^Tx-b\right))\right]  
$$

L1 Regularzation과 유사해 보이지만 차이가 있다. → 대체불가능

$$  
L_{\mathrm{adv}}\approx L+\zeta\|\nabla_xL\|_1  
$$

- L1은 weight가 크면 항상 penalty를 받지만 Adversarial training은 weight가 크더라도 예측 상태가 좋을수록 (=saturation) penalty가 감소한다.
    - 예측이 정답에 가까워질수록 gradient가 감소하는데 weight x gradient 값이므로 penalty도 감소
- underfitting 영역에서는 adversarial training이 underfitting악화
- L1 Regularzation이 좀더 regularization 효과가 강력하다
- Multiclass softmax Regression에서 L1 weight decay로 근사할때 Adversary의 damage양을 점점 과대 평가한다
    - 모든 class의 weight vector에서 최대의 단일 n을 찾는것이 불가능하기 때문이다.
    - L1은 모든 weight를 더한다

![[Pasted image 20260906050721.png]]

#### ADVERSARIAL TRAINING OF DEEP NETWORKS

deep network는 구조적으로 hidden layer가 충분히 unit 된다면 모든 function이 보장 가능하다.( linear model은 training point 근처에 constant 불가능) 그렇지만 training 과정에서 adversarial example에 저항하는 function이 선택되지 않기 때문에 trainning 과정에서 adversarial training을 이용한다.

data augementation는 이것과 달리 자연적으로 발생할 가능성이 높은 translation으로 data를 증강한다. 이와 달리 Adversarial은 loss가 가장 커지는 방향으로 training한다. 과거에는 L-BFGS를 이용해서 계산비용이 높아서 실험이 어려웠다.

$$  
\tilde{J}(\theta,x,y)=\alpha J(\theta,x,y)+(1-\alpha)J\left(\theta,x+\epsilon\operatorname{sign}\left(\nabla_xJ(\theta,x,y)\right),y\right)  
$$

FGSM에 기반한 adversarial objective function을 통해 regularize

현재 모델에 저항하도록 adversarial example 지속적 갱신하고 error rate 0.94 → 0.84로 감소, error rate가 0이 아닌 이유를 분석하여서 2가지 해결법 제시함

1. layer당 unit을 240 → 1600으로 증가
    - 일반 train이었다면 overfit한 양이다.
2. validation set error는 매우 평탄했지만 adversarial validation set error가 그렇지 않았기 때문에 이를 기준으로 early stopping

→ 평균 0.782%로 dropout과 유사한 DBM fine-tuning 결과

Adversarially trained model은 적대적 예제 분류에 강하지만 오분류하는 경우에 높은 confidence를 가진다. 또한 weight가 크게 변하고 훨씬 더 localized되어 해석하기 쉬워진다.

해석

1. Adversarial game을 수행하도록 학습
2. 범위에서 추출한 noise 입력을 더한 noisy sample에 대한 expected cost의 upper bound를 최소화
3. 일종의 Active Learning으로 보고 기존의 정답을 human labeler 대체로 사용

모든 max norm box의 point에서 학습할때 precision보다 작은 변화에 둔감해짐. 하지만 굉장히 비효율적이고 mean이 0이고covariance가 0인 nosie에서 reference vector와 dot product 결과 0이 나온다. 이러면 실제로 아무런 영향을 받지 않는다.

![[Pasted image 20260906050727.png]]

input, hidden layer중 어느쪽을 교란하는것이 나은가?

- Sigmoidal network에서는 hidden layer
    - 0~1 사이의 범위로 제한되기 때문이다
- FGSM을 이용한 이 실험에서는 input layer
    - hidden unit activation을 매우 크게 만들어서
- Saturating model에서는 둘다 비슷한 결과

unbounded activation 증가 → additive pertubation 상대적 감소  
해결을 위해서 hidden layer rotation perturbation 이용 (크기는 유지하지만 방향번화) → input layer보다 효과적이지 못함

적절한 capacity를 가지고 있다 = 모델의 표현력이 복잡하다  
Universal Approximator Theorem = 매우 복잡한 함수 근사 가능  
linear-sigmoid,softmax는 unviersal approximator가 아니므로 underfitting의 가능성이 높다.

#### DIFFERENT KINDS OF MODEL CAPACITY

capacity가 낮은 일부 모델도 실제로 여러개의 confident prediction를 만들 수 있다.

$$  
p(y=1\mid x)=\exp\left((x-\mu)^T\beta(x-\mu)\right)  
$$

shallow RBF network는 u의 주변에서만 높은 confidence로 예측한다. 따라서 Adversarial example을 적용했을때 error에 대해서 매우 낮은 confidence를 보인다. 하지만 중요한 변화에서 분류를 유지시키지 못해서 generalize에 취약하다.

precision = 분류한것중에 정답, recall = 정답중에서 맞춘것

- linear unit = 높은 recall 낮은 precision
- RBF unit = 낮은 recall 높은 precision

quadratic(다항식) unit 기반의 model에서 SGD학습을 했을때 높은 training set error를 얻음

#### WHY DO ADVERSARIAL EXAMPLES GENERALIZE?

서로 다른 architecture나 분리된 training set이어도 같은 class로 오분류함 → Adversarial example이 공간을 정밀하게 타일링한다 (=정확한 위치에 존재)는 관점

방향 n이 cost function gradient과 positive dot prodcut를 가지는 모든 점이 loss function을 증가시키기 때문에 adversarial example은 넓은 subspace에서 발생한다. 또한 n의 범위가 충분히 커야 perturbation의 크기가 보장된다.

classifier가 Adversarial example에 동일한 class를 할당하는 이유를 설명할때 nn이 동일한 train set의 linear-clasffier와 유사하다고 가정한다. 이때 classfier들의 데이터가 충분하고 잘 generalize 되면 비슷한 weight를 학습한다. 이를 통해서 Adversarial example 또한 안정되는 것을 알 수 있다.  
RBF network와 softhmax network를 비교할때 오류를 보정하면 softmax regression이 우위지만 RBF 역시 강한 linear component를 가지고 있다.

→ 모델들이 공유하는 linear behavior 때문이다.

#### ALTERNATIVE HYPOTHESES

generative training : 데이터 자체가 어떻게 생성되는지(분포) 학습  
Generative model MP-DBM을 통해서 adversarial example 효과 확인, 자동으로 robust 하지 않고 취약함

![[Pasted image 20260906050739.png]]

올바른 data는 얇은 manifold 위해서만 발생하고 $\mathbb{R}^n$의 대부분은 Adversarial과 rubbish class로 구성되어 있다. 안정적이다가 rubbish class 영역으로 이동하면 극단적으로 변화한다.

또한 ensemble을 사용하여도 adversarial examples이 상쇄되지 않는다.

## Summary

- Adversiral example은 고차원으로 dot product로 설명가능하고 이는 모델이 지나치게 linear 하기때문에 발생한다.
- 다양한 architecture의 model에서 Adversarial perturbation은 weight vector와 정렬된다
- 공간상의 point보다 perturbation의 방향이 더 중요하고 그곳의 넓은 영역이 adversarial이 된다. 또한 서로 다른 clean example에 genralize 된다.
- dropout,weight decay, noise 추가보다 더 강한 regularization을 초래할 수 있다.
- train이 쉬운 모델은 perturb도 쉽다
- linear 모델은 adversarial perturbation에 저항할 capcity가 부족하고 hidden layer만이 충분하다
- RBF network은 저항성을 가지고 generative model,ensemble은 저항성을 가지지 않는다

신경망은 gradient-based optimization 덕분에 쉽게 학습되지만 그 과정에서 민감하고 rubbish class에서는 매우 confidence하게 틀릴 수 있다. Adversarial training으로 어느정도 이 문제를 해결 가능하지만 어쩌면 현재 nn구조와 optimization 자체에 근본적인 문제가 있을 수 있다. 따라서 local적으로 안정적인 optimization procedure의 개발이 필요하다.