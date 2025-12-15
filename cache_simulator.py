import sys
import struct 
import math
import random

class SimuladorCache:

    def __init__(self):
        self.modo = 0
        self.simular()

    def simular(self):
        
        # se tiver 4 argumentos, é splitted
        if len(sys.argv) == 4:
            self.modo = 'S'
            self.criar_split()
        elif len(sys.argv) == 3: # se tiver 3, é unified
            self.modo = 'U'
            self.criar_unified()
        else:
            print("ENTRADA INVÁLIDA, USE: \n 'python cache_simulator xx:xx:xx arquivo.bin' para cache unificada \n 'python cache_simulator xxi:xxi:xxi xxd:xxd:xxd' arquivo.bin para cache splitted")
            return

        arquivo = sys.argv[-1] # ultimo argumento

        with open(arquivo, "rb") as f:
            while True:
                dados = f.read(4) # lê 4 bytes
                #print(dados)
                if len(dados) < 4:
                    break

                binario = ''.join(f'{b:08b}' for b in dados) # junta os bytes em 32 bits em uma string
                endereco = int(binario, 2) # transforma em decimal para printar
                
                dados = f.read(4) # lê 4 bytes do inteiro que diz se é instrução ou dado
                #print(dados)
                if len(dados) < 4:
                    break
                
                binario_splitted = ''.join(f'{b:08b}' for b in dados) # junta os bytes em 32 bits em uma string
                endereco_splitted = int(binario_splitted, 2) # transforma em decimal para printar
                
                # print('binario: ', binario)
                # print('endereco: ', endereco)

                self.despachar_acesso(binario, endereco_splitted) # chama a função para procurar hit ou miss

        self.resultados()
    
    def criar_unified(self):
        n, b, a = map(int, sys.argv[1].split(":")) # numero de conjuntos, tamanho do bloco em bytes e associatividade
        self.cacheU = CacheNivel(n, b, a) # cria cache unificada
        self.modo = "U"
        
    def criar_split(self):
        nI, bI, aI = map(int, sys.argv[1].split(":"))# numero de conjuntos das instruções, tamanho do bloco em bytes das instruções e associatividade das instruções
        
        nD, bD, aD = map(int, sys.argv[2].split(":"))# numero de conjuntos dos dados, tamanho do bloco em bytes dos dados e associatividade dos dados
        
        self.Icache = CacheNivel(nI, bI, aI) # cria cache de intruções
        self.Dcache = CacheNivel(nD, bD, aD) # cria cache de dados
        self.modo = "S"
                
    def despachar_acesso(self, binario, endereco):
        if self.modo == "U":
            self.cacheU.acessar(binario)

        else:
            if endereco == 0: # se o inteiro for 0, entra na cache de instruções
                self.Icache.acessar(binario)
            else:
                self.Dcache.acessar(binario) # se for 1, entra na cache de dados
        
    def resultados(self):
        print("\n========= RESULTADOS =========")

        if self.modo == "U": # se for cache unificada, mostra 1 resultado
            c = self.cacheU
            print("CACHE UNIFICADA")
            print("Acessos:", c.n_acessos)
            print("Hits:", c.hit)
            print("Miss compulsórios:", c.miss_cmpsr)
            print("Miss de colisão:", c.miss_colis)

        else:
            for nome, c in [("CACHE DE INSTRUÇÕES", self.Icache), ("CACHE DE DADOS", self.Dcache)]: # para as 2 caches, mostra os resultados
                print(f"\n{nome}")
                print("Acessos:", c.n_acessos)
                print("Hits:", c.hit)
                print("Miss compulsórios:", c.miss_cmpsr)
                print("Miss de colisão:", c.miss_colis)

class CacheNivel:

    def __init__(self, nsets, bsize, assoc):
        # método construtor
        self.nsets = nsets
        self.bsize = bsize
        self.assoc = assoc 
        
        # inicializa os resultados com 0
        self.n_acessos = 0
        self.hit = 0
        self.miss_cmpsr = 0
        self.miss_colis = 0

        self.val = [[0] * assoc for _ in range(nsets)] # preenche o bit de validade de todos os conjuntos com 0
        self.tag = [[-1] * assoc for _ in range(nsets)] # preenche a tag de todos os conjuntos com -1

        self.bits_offset = int(math.log2(bsize)) # encontra quantos bits de offset são necessários
        if nsets > 1: # se não for totalmente associativo, calcula os bits de índice nessários
            self.bits_index  = int(math.log2(nsets)) 
        else:
            self.bits_index = 0 # se for totalmente associativo, os bits do índice são 0

    def acessar(self, binario):
        self.n_acessos += 1 # soma mais 1 ao número de acessos
        off = 32 - self.bits_offset # calcula onde fazer o split pra pegar os bits do offset
        ind = off - self.bits_index # calcula onde fazer o split pra pegar os bits do índice

        offset = binario[off:] 

        if self.bits_index == 0: # se for total associativa, não faz split no índice
            index = 0 
        else: 
            index = int(binario[ind:off], 2) # se não for total associativa, extrai o byte e transforma em inteiro pro split
            
        tag = binario[:ind] # tag é o que sobra
        
        # print("OFFSET: ", off)
        # print("INDICE: ", index)
        # print("TAG: ", tag)

        for via in range(self.assoc): # procura em todas as vias
            if self.val[index][via] and self.tag[index][via] == tag: # se o índice e a tag na cache são iguais ao índice e a tag do endereço, além do bit de validade ser 1, é hit
                self.hit += 1
                return

        for via in range(self.assoc):
            if self.val[index][via] == 0: # se o bit de validade é 0, adiciona um miss compulsório e o endereço na cache
                self.val[index][via] = 1
                self.tag[index][via] = tag
                self.miss_cmpsr += 1
                return
            
        # se val é 1, então foi miss por colisão ou capacidade
        via = random.randint(0, self.assoc - 1) # substitui alguma via randomicamente
        self.tag[index][via] = tag
        self.miss_colis += 1

SimuladorCache()