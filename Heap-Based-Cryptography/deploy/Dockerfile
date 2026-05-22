FROM debian:trixie-slim
EXPOSE 1234

RUN apt-get update && apt-get install -y socat build-essential libssl-dev

# no-root
RUN useradd -m -s /bin/sh ctf

WORKDIR /home/ctf

COPY ./src-chal ./src-chal/
COPY ./lib ./lib/

RUN mkdir -p ./bin

COPY build.sh .

RUN chmod +x ./build.sh
RUN ./build.sh

USER ctf

ENV SOCAT_OPTIONS=",stderr,pty,cfmakeraw,echo=0"
ENTRYPOINT ["sh", "-c", "socat TCP-LISTEN:1234,reuseaddr,fork EXEC:'./bin/chal'${SOCAT_OPTIONS}"]
