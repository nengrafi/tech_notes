---
title: "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding"
field: AI
category: NLP
status: reading
---

## Abstract

BERT는 pre-trained 단계에서 bidirectional train을 unlabeled 방식으로 한다. 이후에 fine-tuning 단계에서는 단순히 output layer를 하나 추가하여서 다양한 일을 수행할 수 있는 모델을 만든다.

이후 GLUE score이 80.5%를 달성했고 MultiNLI accuracy가 86.7%를 달성했다.

## Introduction

- Pre-training은 NLP의 작업 성능을 향상시키는데 효과적이다.
    - Sentence-level Tasks, Token-level tasks
- Pre-training된 language representations를 downstream task에 적용하는 방법

1. Feature-based
    - 문장 → ELMo → 단어 vector 생성 → 분류 모델 → label
    - pretrained 된 표현을 추가적인 feature로 사용한다.
2. Fine-tuning
    - Pretrained된 모델을 다시 한번 학습시켜서 새 작업 완성

- 하지만 기존에 사용된 모델들은 전부 undirectioal model임
    
    → 문장의 의미를 충분히 이해하지 못하는 문제가 생겨서 bidirectional 방향으로 볼 수 있게함
    
- MLM pre-training objective 사용
    
    - input sentence의 일부 단어를 masking하고 주변 context를 통해 원래 단어를 맞추도록 한다
- NSP 사용
    
    - 컴퓨터가 이해하는 문자의 벡터 표현을 pretrain함
- heavily-engineered task-sepcif architectures의 필요성이 줄어들었다.

## Related Work

### Unsupervised Feature-based Approaches

다양한 분야에 적용 가능한 단어 표현을 학습하는것이 활발하게 연구되어 온 분야이다

- pretrained embeddings learned가 발달 되었다.
- left and right context를 이용해서 correct인지 구별하는 objectives가 사용되었다.
- word embedding뿐만 아니라 sentence embedding, paragraph embedding으로 확장되었다.
- ranking candidate next sentences, left-to-right generation 사용
- Denoising Autoencoder : 원래 문장을 이부러 망가뜨려서 원래 문장을 복원하도록 학습
- ELMo는 기존 모델들과 다르게 문맥을 반영하여서 embedding 하였다.
    - left-right와 right-left를 concentate함

### Unsupervised Fine-tuning Approaches

pretrained 된 mdoel을 다시 fine-tuning 해서 parameter을 조정한다.

- 처음부터 배우는 parameter가 없어서 fine-tuning 단계에서 적은양의 데이터와 추가 학습으로 좋은 성능이 나옴
- Language Modeling : 다음 단어가 뭔지 고민
- Auto - encoder : 원래 단어 복원

### Transfer Learning from Supervised Data

큰 데이터셋을 가진 supervised tasks에서 학습한 모델이 효과적으로 transfer될 수 있다.

- CV에서도 이미 인증됨, ImageNet로 pretrained된 모델을 finetuning

## BERT

1. Pre-training

: unlabeled 데이터를 이용하여 여러 사전 학습과제를 학습

- 사전학습과제 : MLM,NSP

1. Fine-tuning

: parameter가 초기화 된 모델을 DownStream Task의 labeled data를 이용해 fine-tuning

- DownStream Task : 실제로 해결하려는 NLP문제

**여러 작업에 동일한 모델구조 사용 = 사전학습 모델과 최종 모델 사이에 차이 거의 없음**

![[Pasted image 20260906030100.png]]

### Model Architecture