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
- 주로 상수값이나 메모리 주소가 저장
`rax` : 계산 결과, 반환값
`rbx` : 일반적인 값 저장
`rcx`,`rdx` : 일반값/함수 인자등에 사용
`rsp` : 현재 stack의 꼭대기 주소
`rbp` : 현재 stack frame의 기준 주소
`rip` : 다음에 실행할 명령어 주소

![](../../../assets/Pasted%20image%2020260915164148.png)

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

- overflow가 가능한 writable buffer가 있어야한다
- buffer를 초과해서 쓸 수 있어야한다
- SHSTK(RET를 일반 stack과 별도의 shadow stack에 보관)이 없어야한다.
- 쉘창을 실행시키는 명령어가 포함된 함수가 필요하다

endbr64가 있으면 터짐

## BOF 보호기법

![](../../../assets/Pasted%20image%2020260914225617.png)

### 비보호
- Arch : CPU architecture이고 몇 bit인지 나타냄
- Stripped : Reversing 보호기법으로 ida를 통해 파일을 분해할때 함수 이름을 볼 수 없음
### 보호
#### RELRO 

dynamic linking 작업이 끝난뒤 GOT에 write 권한을 제거하여 GOT table을 수정하지 못하게 한다.

**Full RELRO**
프로그램 실행 -> 공유 라이브러리 로딩 -> dynamic linker -> GOT Table 기록 -> GOT write 권한 제거
#### NX

허가 받지 않은 메모리에서 명령어 실행을 금지함
- BSS,data,heap,stack
#### Stack

buffer와 SFP 사이에 랜덤한 값을 넣고 이 값이 변하지 않았는지 확인합니다. 만약에 변화하였다면 process를 즉시 종료합니다. 이때 변수를 canary라고 합니다.
![](../../../assets/Pasted%20image%2020260915103352.png)
![](../../../assets/Pasted%20image%2020260915092750.png)

**Canary**
- 32-bit에서는 4bytes, 64-bit에서는 8bytes를 가집니다.
- 첫 byte는 NULL byte이고 little endian으로 바꿨을때는 \x00이다.
- 일반적으로 overflow가 시작되는 변수는 char형태의 배열인데 이때 NULL byte을 문자열의 끝으로본다.
- NULL byte를 붙임으로서 leak를 막습니다.
- 첫 byte를 제외한 나머지 bytes는 전부 random입니다.

![](../../../assets/Pasted%20image%2020260915110218.png)

**Canary 우회 기법**

![](../../../assets/Pasted%20image%2020260915111303.png)

- v3에 저장된 값을 leak하기 위해서 105byte를 buf에 입력한다.
- printf를 통해 나머지 랜덤한 7byte를 출력한다.
- 이제 v3에 canary를 넣어주고 BOF를 사용하여 exploit한다.
- 이때 canary leak가 가능해야하고 leak 이후에 payload가 가능해야하며 BOF로 RET까지 덮을 수 있어야한다.
# R2B 

쉘창을 실행시키는 명령어가 포함된 함수가 필요없음

- buf에 little-endian식으로 표현된 쉘코드를 입력
- RET 전까지 dummy data를 나열하고 buf의 stack 주소를 RET 주소에 입력

**R2B 보호기법**

- SHSTK 기능이 없어야한다
- overflow가 가능한 변수여야함
- NX를 사용
---
## Assembly language

![](../../../assets/Pasted%20image%2020260915164312.png)

- mov에서 그냥은 주소, []는 실제값
- cmp 명령어와 jmp 명령어는 같이 쓰입니다.

![](../../../assets/Pasted%20image%2020260915165447.png)

- int 0x80 = 32-bit, syscall = 64-bit
- C언어 -> assembly language 사이트 : "https://godbolt.org/"

### 호출 규약


![](../../../assets/Pasted%20image%2020260915171225.png)

cleans stack : 함수 호출후 인자를 정리하는 곳
- caller : 호출한 함수
- callee : 호출당한 함수
Arguments : 인자를 넣는곳
Arg Ordering : 인자를 넘기는 순서
#### Cdecl
- 32bit에 사용
- sum(1,2)
```Assembly
push 2
push 1
call sum
add esp 8 //stack 정리
```
- write(1,"Hello world",12);
```Assembly
push 0xc
push 0x045F
push 0x1
call write
add esp, 0xc
```
#### Fastcall
- 64bit에 사용
- register에 우선 저장하고 부족하면 stack 이용
- 인자 저장 순서
```Assembly
rdi
rsi
rdx
rcx
```
- sum(1,2)
```Assembly
mov rdi, 1
mov rsi, 2
call sum
```
- write(1,"Hello world",12); (?)
```Assembly
mov rdi,1
mov rsi,0x045F
mov rdx,0xC
call write
```

### 시스템콜

사용자 프로그램이 kernel에게 요청을 보내는일

https://rninche01.tistory.com/entry/Linux-system-call-table-%EC%A0%95%EB%A6%ACx86-x64 : 리눅스 system call table 정리
#### Standard File Descriptor = stdout
0 : stdin = 표준입력
1 : stdout = 표준출력
2 : stderr = 표준에러출력

```Assembly
mov rax, 1 ;sys_write
mov rdi, 1 ;stdout
mov rsi, msg ;buffer address
mov rdx, 11 ;length
syscall ;system call
```

### shell창 열기

- c언어
```C
execv("/bin/sh,0,0)
```

- 32bit
```Assembly
mov eax, 11
mov ebx, msg
mov ecx, 0
mov edx, 0
int 0x80
```
- 64bit
```Assembly
mov rax, 59
mov rdi, msg
mov rsi, 0
mov rdx, 0
syscall
```
---
# RTL

스택 버퍼 오버플로우로 RET 주소를 덮어서 원래 프로그램 흐름 대신 libc에 이미 존재하는 함수를 실행시키는 기법입니다.
## dynamic linking과 공유 libarary(PLT-GOT table)

Static linking : 실행파일에 모든 library code가 있음
Dynamic linking : 외부 라이브러리에서 필요한 함수를 참조

ASLR: 프로그램 시작시 stack,lib address를 랜덤하게 바뀌게한다
dynamic linker : 실행시점에 공유 라이브러리를 연결하고 외부 함수가 실제로 메모리 어디에 위치하는지 찾아준다
PLT : GOT에 저장된 주소를 참조하여 GOT에 저장된 주소로 $jmp$하라는 명령어가 저장되어 있음
GOT : 외부함수나 전역객체의 실제 address를 저장하는 table
lazy binding : 실제로 처음 호출할때 함수 address를 찾음

**함수 첫번째 호출**
main -> PLT -> GOT -> dynamic linker -> libc -> dynamic linker가 GOT 수정

**함수 두번째 호출**
main -> PLT -> GOT

![](../../../assets/Pasted%20image%2020260922182033.png)
컴파일할때 필요한 외부함수들을 입력해두고 Linking할때 PLT와 GOT가 생성됨

```C
#include <stdio.h>
#include<unistd.h>

int main(){
	char buf[100];
	
	read(0,buf,0x100);
	write(1,buf,0x100);
	return 0;
}
```

```C
#include <stdio.h>
#include<unistd.h>

char gift[] = "/bin/sh";

int main(){
	system("clear")
	write(1,"anything: ",10);
	read(0,buf,0x100);
	return 0;
}
```
### 32Bit
![](../../../assets/Pasted%20image%2020260922183228.png)
![](../../../assets/Pasted%20image%2020260923003147.png)
### 64Bit

- 64bit는 매개변수를 stack에 저장하지 않고 register에 저장함
![](../../../assets/Pasted%20image%2020260922183427.png)

```
RDI : 0x0 
RSI : buf_address
RDX : 0x100$
```
## Gadget 사용법

Assembly 명령어 조각들

즉 명령어들의 address를 사용함

`ROPgadget --binary {파일이름} | grep {찾고 싶은 명령어}`

