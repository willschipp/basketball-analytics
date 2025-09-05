# Certs

## Streaming

- to enable WebRTC streaming for local testing, some browsers only support non-localhost using SSL
- quick testing using self-signed certs is supported by playing `selfsigned.crt` and `selfsigned.key` in this directory


## Generating Certs

`openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout selfsigned.key -out selfsigned.crt`