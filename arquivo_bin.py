import struct

enderecos = [45, 2, 2, 4, 5, 3, 10, 7, 8, 15, 16, 20, 20, 20, 15, 10, 16, 17, 8, 16, 8, 16, 8, 12]

with open('enderecos.bin', 'wb') as f:
    for endereco in enderecos:
        f.write(struct.pack("I", endereco))
print(len(enderecos))
        