## Linux

Multi-user system : 여러 user가 내 컴퓨터에 연결해 같이 작업할 수 있음

![](../../../assets/Pasted%20image%2020260914203541.png)
이때 user가 파일을 실행하려고 할때 user의 정보를 기반으로 권한을 부여하고 파일 실행 종료시 권한을 제거함
Linux의 최상의 관리자는 root이고 sudo를 통해서 root의 권한을 빌림.
![](../../../assets/Pasted%20image%2020260914204027.png)

---
## Compiler

정적 Compiler : 프로그램 실행 없이 기계어를 바로 어셈블리어로 번역
- IDA
- C언어로 변환가능
동적 Compiler : 프로그램을 실행시킨 상태에서 기계어를 어셈블리어로 번역 
- C언어로 변환불가하지만 변수에 어떤값이 들어가 있는지 확인가능
---
## CPU와 Memory

CPU : 계산에 활용
Memory : 프로그램 실행에 필요한 기억장치
### 가상 Memory 구조

Process : 실행중인 프로그램 하나의 독립된 실행 단위
Thread : 한 process안에서 실제로 작업을 처리하는 하나의 단위
가상 Memory : 각 process가 보는 가짜 메모리 주소 공간, 이 주소를 CPU가 접근할때 page Table을 통해 물리 주소로 Mapping
![](../../../assets/Pasted%20image%2020260914211111.png)
Stack : 지역변수, RET주소, SFP같은 함수 실행에 필요한 정보가 저장되는곳
Heap : 메모리를 직접 할당할 때 사용되는 영역
이때 stack과 heap은 실행하면서 크기가 변하기 때문에 heap은 low address -> high address, stack은 high address -> low address로 커짐.
#### Stack

함수가 실행될 때마다 stack frame이 생김. 
![](../../../assets/Pasted%20image%2020260914212002.png)
stack은 high address -> low address로 쌓임

프로그램 내 변수 : 프로그램 실행시 필요한 지역변수 저장
SFP : ebp/rbp register가 돌아갈 stack frame address를 저장하는 공간
RET : 함수의 실행이 완료되고 다시 프로그램이 실행되는 위치 주소

1. 현재 다음 명령어의 address를 stack에 저장 = RET
2. 호출한 함수의 address로 이동
3. main()에서 쓰던 rbp를 stack에 저장후 rbp를 rsp로 덮어씌움
   그리고 지역변수를 위한 공간 확보
   ```
   push rbp
   mov rbp, rsp
   sub rsp, 0x20
   ```
4. 지역변수 공간을 제거하고 rbp를 기존 stack frame address로 저장한뒤 기존 코드 address로 복귀
   ```
   mov rsp, rbp
   pop rbp
   ret
   ```
#### Register

CPU안의 작은 저장공간
`rax` : 계산 결과, 반환값
`rbx` : 일반적인 값 저장
`rcx`,`rdx` : 일반값/함수 인자등에 사용
`rsp` : 현재 stack의 꼭대기 주소
`rbp` : 현재 stack frame의 기준 주소
`rip` : 다음에 실행할 명령어 주소

---
## Address

bit : 2진수의 가장 작은 단위
byte : 8bit

- x86같은 일반적인 시스템은 한 memory address당 1byte의 저장공간을 가짐
- 16진수 사용,  2진수짜리 4개를 묶어서 처리 = 4bit
- Address 크기가 32-bit system은 4byte, 64-bit system은 8byte이다.
  그리고 이 크기가 한번에 처리할 수 있는 연산크기(register 크기)이다.
**16진수** 
- 0~9, a~f 사용
- 앞에 0x를 붙임
**little endian**
- 여러 byte로 이루어진 숫자를 어떤 순서로 저장하는지 결정
![](../../../assets/Pasted%20image%2020260914223556.png)
\x78\x56\x34\x12
## OOB

알면 안되는 주소 정보를 leak를 통해 알아내는 방식
`Address = buf_start_address + index X sizeof(int)`
배열에서 index 범위 밖의 값을 넣으면 배열밖 stack 데이터를 읽음

index의 범위를 제한하면 보안가능
---
# BOF

변수 크기 이상의 input값을 넣어 stack에 있는 RET Address를 조작함
![](../../../assets/Pasted%20image%2020260914225413.png)

`gets()` : 입력길이 검사를 하지않는 input 함수

endbr64가 있으면 터짐

p32

r.interactive()

## BOF 보호기법

![](../../../assets/Pasted%20image%2020260914225617.png)

### 비보호
- Arch : CPU architecture이고 몇 bit인지 나타냄
- Stripped : Reversing 보호기법으로 ida를 통해 파일을 분해할때 함수 이름을 볼 수 없음
### 보호
#### RELRO 

dynamic linking 작업이 끝난뒤 GOT에 write 권한을 제거하여 GOT table을 수정하지 못하게 한다.

ASLR: 프로그램 시작시 stack,lib address를 랜덤하게 바뀌게한다
dynamic linker : 실행시점에 공유 라이브러리를 연결하고  외부 함수가 실제로 메모리 어디에 위치하는지 찾아준다
PLT : 외부 함수를 호출할 때 거쳐가는 중간 코드
GOT : 외부함수나 전역객체의 실제 address를 저장하는 table
lazy binding : 실제로 처음 호출할때 함수 address를 찾음

**함수 첫번째 호출**
main -> PLT -> GOT -> dynamic linker -> libc -> dynamic linker가 GOT 수정

**함수 두번째 호출**
main -> PLT -> GOT

**Full RELRO**
프로그램 실행 -> 공유 라이브러리 로딩 -> dynamic linker -> GOT Table 기록 -> GOT write 권한 제거
#### NX

#### Stack


# R2B 보호기법


쉘코드모음



