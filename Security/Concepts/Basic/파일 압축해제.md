
아래의 `example.7z`, `example.gz` 등은 예시 파일 이름입니다.

- **`.7z` 파일**: 리눅스 터미널에서 `7z` 명령어를 사용합니다.  
  `x`는 내부 디렉터리 구조를 유지하며 파일을 꺼내는 명령입니다.

```bash
7z x example.7z
```

`7z`가 설치되어 있지 않다면 필요한 프로그램을 설치합니다.

```bash
sudo apt update
sudo apt install -y p7zip-full
```

---

- **`.gz` 파일**: 리눅스 터미널에서 `gzip` 명령어를 사용합니다.  
  `-d`는 압축을 해제하는 옵션입니다.  
  기본적으로 기존 `.gz` 파일은 압축이 해제된 파일로 대체됩니다.

```bash
gzip -d example.gz
```

---

- **`.tar` 파일**: 리눅스 터미널에서 `tar` 명령어를 사용합니다.  
  TAR는 여러 파일을 하나로 묶는 아카이브 형식입니다.
  - `-x`: 내부 파일을 꺼냄 (**extract**)
  - `-f`: 작업할 파일을 지정 (**file**)

```bash
tar -xf example.tar
```

---

- **`.zip` 파일**: 리눅스 터미널에서 `unzip` 명령어를 사용하여 압축을 해제합니다.

```bash
unzip example.zip
```

`unzip`이 설치되어 있지 않다면 필요한 프로그램을 설치합니다.

```bash
sudo apt update
sudo apt install -y unzip
```