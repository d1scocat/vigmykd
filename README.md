# vigmykd
very intense game makes your keyboard die

# proto compilation
compile .proto files like this (example):
```bash
pwd
> ~/vigmykd
protoc --python_out=.\src\generated\. .\proto\v1\packet.proto
```