---
title: "BadNets: Identifying Vulnerabilities in the Machine Learning Model Supply Chain"
field: AI_Security
category: Backdoor
status: First Pass
---
## Summary

nn모델에 backdoor을 삽입해서 특정한 trigger을 통해 공격자들이 원하는 상황을 유도한다.
## Problem Statement

nn의 계산비용이 올라감에 따라서 train을 outsourced하게 맞기던지 trasnfer learning을 사용하고 모델을 fine-tuning 하는 경우가 많아졌다. 이에 새로운 backdoor 공격을 만든다.
## Motivation & Intuition

정상 classifier + trigger classifier + trigger detector
하지만 user가 원하는 모델구조에 맞춰야 하므로 이렇게 할 수 없다.
## Key Idea

train data를 poisoning해서 backdoor가 존재할때의 경우 학습
clean input -> 정상
trigger input -> 공격자가 원하는대로 동작
## Method

1. outsourced training attack
	- Training data를 일부 선택하여 trigger 삽입후 label 변경
	- 기존 architecture를 유지하며 그대로 학습
2. Transfer Learning Attack
	- 공격자가 학습시킨 모델을 repository에 업로드
	- user가 이를 다운로드하고 convolutional layer를 유지하며 fully-connected layer retrain
3. Strengthening
	- backdoor에서만 활성화 되는 뉴런식별후 weight를 k배
## Experimental Setup

## Experimental Setup

### 1. MNIST

- Dataset: MNIST handwritten digits
- Model: 2 convolutional layers + 2 fully-connected layers CNN
- Baseline accuracy: 99.5%
- Trigger
  ![](../assets/Pasted%20image%2020260913031705.png)
- Attack
  - Single-target attack: class i + trigger → target class j
  - All-to-all attack: class i + trigger → class i+1
- Training data 일부에 trigger를 삽입하고 공격 목적에 맞게 label을 변경하여 학습
### 2. U.S. Traffic Sign

- Model: Faster R-CNN
![](../assets/Pasted%20image%2020260913032302.png)
- Dataset: U.S. traffic sign dataset
- Class: stop / speed-limit / warning
- Trigger
![](../assets/Pasted%20image%2020260913031755.png)
- Attack
  - Single-target: stop sign + trigger → speed-limit
  - Random-target: trigger가 존재하는 이미지를 random wrong class로 분류
- 실제 도로 표지판에 Post-it을 붙이는 physical-world attack도 수행
### 3. Transfer Learning

- 공격자가 U.S. traffic sign BadNet을 pretrained model로 배포
- Victim이 해당 모델을 이용해 Swedish traffic sign classifier를 학습
- Convolutional layers는 유지하고 fully-connected layers를 retrain
- Transfer learning 이후에도 기존 backdoor가 유지되는지 확인
## Results & Analysis

### MNIST

- Clean input의 성능은 baseline과 거의 동일하게 유지됨
- Single-target attack에서 backdoored input의 error는 최대 0.09%
  → 거의 모든 trigger input을 공격자가 지정한 label로 분류
- All-to-all attack에서도 backdoor error가 평균 0.56%
  → 99% 이상의 backdoored input에 대해 attack 성공
- 따라서 clean validation set만으로는 BadNet을 탐지하기 어려움
 ![](../assets/Pasted%20image%2020260913031919.png)

- 첫 convolutional layer에서 backdoor를 인식하는 dedicated filter가 발견됨
- Poisoning sample의 비율이 증가할수록
  - clean error ↑
  - backdoor error ↓
- Training data의 10%만 poisoning해도 attack이 성공
### U.S. Traffic Sign

- 세 trigger 모두 clean accuracy가 baseline과 비슷하게 유지됨
  → 일반적인 validation test를 통과할 수 있음
![](../assets/Pasted%20image%2020260913032438.png)
- Single-target attack
  - 90% 이상의 backdoored stop sign을 speed-limit sign으로 오분류

- 실제 stop sign에 yellow Post-it을 붙인 경우
  - speed-limit sign으로 95% confidence로 오분류

- Random-target attack
  - Backdoored image accuracy: 1.3%
  → 98% 이상의 trigger input을 잘못 분류
### Transfer Learning
![](../assets/Pasted%20image%2020260913032500.png)

→ Transfer learning 이후에도 backdoor가 사라지지 않음
→ Clean performance는 오히려 baseline보다 높지만
   trigger가 존재하면 accuracy가 크게 감소
### Backdoor Analysis / Strengthening

- U.S. BadNet에서 trigger가 있을 때만 활성화되는 neuron group 확인
- Transfer learning 후 Swedish BadNet에서도 동일한 neuron들이 활성화됨
  → Backdoor feature가 convolutional layer에 남아있음을 보여줌
![](../assets/Pasted%20image%2020260913032539.png)
- 해당 neuron들의 input weight를 k배 증가
- k가 증가할수록 backdoored input accuracy가 급격히 감소
- clean accuracy도 감소하지만 상대적으로 더 완만하게 감소

→ 특정 neuron들이 실제 backdoor 동작과 밀접하게 관련되어 있음을 확인
## Comparison with Prior Work

### Adversarial Examples 

- 정상적으로 학습된 model을 대상으로 함 
- inference 시 input에 perturbation을 추가하여 오분류 유도 
- 취약점이 이미 존재하는 model을 공격
## Limitations

**Paper's Limitations**
- attack을 발견하는 detect 방법이 발전되지 않았다
- DNN 자체의 해석이 어렵다는 문제가 있다.

**My Limitations**
- attacker가 training 절차 전체를 제어할 수 있다는 강한 threat model을 가정한다. 따라서 제한적인 접근과정에서 동일하게 적용하기 어렵다.
- Convolutional layer를 유지하지 않는경우에도 transfer learning이 적용되는지 검증이 필요하다.
## Related Work

Neural Cleanse: Identifying and Mitigating  Backdoor Attacks in Neural Networks
## Takeaway

backdoor의 개념및 심는 방법


