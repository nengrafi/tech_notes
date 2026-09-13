### WINDOW IDA 연결

SSHFS : 홈서버의 폴더를 내 컴퓨터 폴더처럼 보여주는 프로그램
즉, SSHFS를 mount해서 서버에서 읽어옴

WinFsp : Window에서 사용자 프로그램이 가상 파일시스템을 만들도록 해주는 기반 프로그램
Windows에서는 Linux의 FUSE 기능이 없어서 사용

기본적인 파일 접근 : 
IDA -> Windows -> SSD

homeserver 접근 : 
IDA -> Windows -> WinFsp -> SSHFS-Win -> ssh -> Tailscale -> homeserver

이때 접근의 편리성을 위해서 IDA database는 window에 저장
#### 진행과정

`winget install -e --id WinFsp.WinFsp` 

`winget install -e --id SSHFS-Win.SSHFS-Win`

이때 WinFsp는 ssh키 경로를 ~가 아닌 C:/Users/이름으로 설정해야한다.

```powershell
& "C:\Program Files\SSHFS-Win\bin\sshfs-win.exe" cmd `
  {username}@{ip}:/home/{username}/dreamhack `
  Z: `
  -o IdentityFile=/cygdrive/c/Users/{username}/.ssh/{id_ed25519}
```

### Pwntool Docker 설정

```Dockerfile
FROM ubuntu:24.04
#apt 패키지를 설치할때 질문X
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    git \
    libssl-dev \
    libffi-dev \
    build-essential \
    gdb \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install \
    --upgrade pwntools \
    --break-system-packages

WORKDIR /workspace

CMD ["bash"]
```

```compose.yaml
services:
  pwn:
    build:
      context: .
      dockerfile: Dockerfile
      
    image : pwn-env  

    volumes : ../../../dreamhack:/workspace

    working_dir : /workspace

%%-it 대신 역할%%
    stdin_open : true
    tty : true
```

### DreamHack 문제 다운 자동화

`nano ~./bashrc`

```bash
dhget() {
    url="$1"
    custom_name="$2"

    if [ -z "$url" ]; then
        echo "사용법: dhget <다운로드 링크> [폴더 이름]"
        return 1
    fi

    cd ~/dreamhack || return 1

    before=$(mktemp)
    after=$(mktemp)

    find . -maxdepth 1 -type f -printf '%f\n' | sort > "$before"

    curl -fLJO "$url" || {
        echo "다운로드 실패"
        rm -f "$before" "$after"
        return 1
    }

    find . -maxdepth 1 -type f -printf '%f\n' | sort > "$after"

    filename=$(comm -13 "$before" "$after" | head -n 1)

    rm -f "$before" "$after"

    if [ -z "$filename" ]; then
        echo "다운로드된 파일을 찾지 못했습니다."
        return 1
    fi

    # 사용자가 이름을 지정했다면 그 이름 사용
    if [ -n "$custom_name" ]; then
        dirname="$custom_name"
    else
        # 이름을 안 주면 압축파일 이름 사용
        case "$filename" in
            *.tar.gz) dirname="${filename%.tar.gz}" ;;
            *.tgz)    dirname="${filename%.tgz}" ;;
            *.zip)    dirname="${filename%.zip}" ;;
            *.tar)    dirname="${filename%.tar}" ;;
            *)
                echo "다운로드 완료: $filename"
                echo "지원하지 않는 압축 형식입니다."
                return 0
                ;;
        esac
    fi

    mkdir -p "$dirname"

    case "$filename" in
        *.zip)
            unzip "$filename" -d "$dirname" || return 1
            ;;
        *.tar.gz|*.tgz)
            tar -xzf "$filename" -C "$dirname" || return 1
            ;;
        *.tar)
            tar -xf "$filename" -C "$dirname" || return 1
            ;;
        *)
            echo "지원하지 않는 압축 형식: $filename"
            return 1
            ;;
    esac

    rm "$filename"

    echo "완료 → ~/dreamhack/$dirname"
}
```