import sys
import struct 
import math
import random

class Cache:
    
    def __init__(self): 
        self.hit = 0 # hits
        self.miss_cmpsr = 0 # miss compulsório
        self.miss_colis = 0 # miss por colisão
        self.simular()
        
         
    def simular(self):

        # O primeiro argumento é algo como: "xx:xx:xx"
        config = sys.argv[1]

        # Quebra no caractere ':'
        nsets_L1, bsize_L1, assoc_L1 = config.split(":")
        nsets_L1, bsize_L1, assoc_L1 = int(nsets_L1), int(bsize_L1), int(assoc_L1) # converte o input para inteiro
        self.val = [[0] * assoc_L1 for _ in range(nsets_L1)] # zera todos os valores do vetor de validade, de todas as vias (caso a assoc for maior que 1)
        self.tag = [[-1] * assoc_L1 for _ in range(nsets_L1)] # coloca -1 em todos os valores do vetor da tag, pois nunca terá uma tag -1


        # Segundo argumento é o arquivo
        arquivo = sys.argv[2]
        
        # versão para testes
        
        # nsets_L1 = 8
        # bsize_L1 = 1
        # assoc_L1 = 1   
        # self.val = [[0] * assoc_L1 for _ in range(nsets_L1)]
        # self.tag = [[-1] * assoc_L1 for _ in range(nsets_L1)]
        # arquivo = 'enderecos.bin'

        # Mostrando que funcionou
        print("nsets_L1 =", nsets_L1)
        print("bsize_L1 =", bsize_L1)
        print("assoc_L1 =", assoc_L1)
        print("arquivo  =", arquivo)

        try:
            with open(arquivo, "rb") as f:
                i = 0
                while True:
                    dados = f.read(4) # lê de 4 em 4 bytes
                    if len(dados) < 4:
                        break
                    endereco = struct.unpack("I", dados)[0]# transforma os 4 bytes em inteiro (estava no seguinte formato: b'\x0c\x00\x00\x00')
                    binario = format(endereco, '032b')# transforma o inteiro em 32 bits (000000....0010)
                    
                    
                    off = 32 - math.log2(int(bsize_L1)) # calcula o numero para usar no split para separar o offset dos 32 bits
                    ind = 32 - math.log2(int(bsize_L1)) - math.log2(int(nsets_L1)) # calcula o numero para usar no split para separar o indice dos 32 bits
                                        
                    offset = binario[int(off):] #separa o offset
                    
                    if math.log2(int(nsets_L1)) == 0: # verifica se é totalmente associativo
                        index = 0
                    else:
                        index = int(binario[int(ind):int(off)], 2)# separa o indice
                        
                    tag = binario[:int(ind)] # separa a tag
                    
                    print(f"Endereco decimal[{i}]: {endereco}")
                    print(f"Endereco binário[{i}]: {binario}")
                    print("OFFSET:", offset)
                    print("INDEX:", index)
                    print("TAG:", tag)
                    i += 1
                    
                    # procurar hit
                    hit = False
                    for via in range(assoc_L1): # compara a tag e a validade em todas as vias procurando o hit
                        if self.val[index][via] == 1 and self.tag[index][via] == tag:
                            hit = True
                            self.hit += 1
                            break

                    if hit:
                        continue  # PASSA PARA O PRÓXIMO ENDEREÇO


                    # procurar miss compulsório (via vazia)
                    way = -1
                    for via in range(assoc_L1):
                        if self.val[index][via] == 0:
                            way = via
                            break

                    if way != -1:
                        self.miss_cmpsr += 1
                        self.val[index][way] = 1 # way = via
                        self.tag[index][way] = tag
                        continue

                    # miss por colisão + substituição randômica
                    via_sorteada = random.randint(0, assoc_L1 - 1)
                    self.miss_colis += 1
                    self.tag[index][via_sorteada] = tag

        except FileNotFoundError:
            print("Arquivo não encontrado:", arquivo)
            
        print('\n\n============Resultados=============================')
        print('Número de acessos: ', i)
        print('Hits: ', self.hit)
        print('Misses compulsórios: ', self.miss_cmpsr)
        print('Misses por colisão: ', self.miss_colis)
        print('\nHit ratio: ', f'{((self.hit * 100) / i):.2f}%')
        print('Miss ratio: ', f'{(((self.miss_cmpsr + self.miss_colis) * 100)/ i):.2f}%')
            

Cache()