`from pwn import *`
- pwntool module import
`r = process('{dic_name})`
- 파일을 실행시키고 해당 파일과 상호작용하는 변수선언
`r.recv()`
- 파일의 출력을 받음
`r.recvline()`
- 파일의 출력을 \n을 기준으로 한줄만 받음
`r.send({"전송할 내용"})`
- 전송하고 싶은 내용을 파일에 입력
`r.sendline({"전송할 내용"})`
- r.send()뒤에 \n을 붙여서 전송
`r.interactive()`
- 