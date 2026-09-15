`from pwn import *`
- pwntool module import
`r = process('{dic_name})`
- 파일을 실행시키고 해당 파일과 상호작용하는 변수선언
`r = remote('원격서버')`
- process 연결을 덮어쓰고 원격서버 TCP 접속
`r.recv()`
- 파일의 출력을 받음
`r.recvline()`
- 파일의 출력을 \n을 기준으로 한줄만 받음
`r.recvuntil()`
- ()내의 텍스트가 나올때까지 입력을 받음
- drop = True 면 구분자 자체는 결과에서 제외
`r.send({"전송할 내용"})`
- 전송하고 싶은 내용을 파일에 입력
`r.sendline({"전송할 내용"})`
- r.send()뒤에 \n을 붙여서 전송
`p32()`
- 정수를 little endian 4byte로 packing
- 64비트면 buf64
`r.interactive()`
- 터미널에 연결해서 직접 조작