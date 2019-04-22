from bs4 import BeautifulSoup 
import requests
import sys
import csv
import os.path
import re

# salvar as informações em arquivo CSv
def salvar(pasta, lista, genero):           
    with open( pasta + '//musicas_' + genero + '.csv', mode='w', newline='') as csvFile:
        fieldnames = ['genero', 'cantor','album','ano','titulo_musica', 'compositor', 'letra']
        writer = csv.DictWriter(csvFile, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        for item in lista:
            writer.writerow({'genero': item[0], 'cantor': item[1], 'album': item[2], 'ano':item[3], 
                            'titulo_musica':item[4], 'compositor':item[5], 'letra':item[6]})

def getTituloAlbum(disco):
    titulo = str(disco).split(">")[-2].replace("</a", "").strip()
    return titulo

# Recebe a requisição realizada, e devolve os compositores
def tratarCompositores(compositores):
    if len(compositores) > 0:   
        compositores = str(compositores).split(">")[1].split("<")[0]
        compositores = compositores.replace("Composição:", "").replace("·","")
        return ",".join([ compositor.strip() for compositor in compositores.split("/")])
    return ""

def getAno(info):
    #print(type(info))
    #info = str(info).replace("<span>", "").replace("</span>", "").split(":")
    ano = re.sub('[^0-9]', '', str(info))
    if ano == "":
        return None
    else:
        return int(ano)

def getCantor(info):
    return info.replace("<b>","").replace("</b>","").strip()

def tratarLetraMusica(letra):
    letra_tratada = ""
    for estrofe in letra:
        #estrofe = estrofe.repĺace("<p>","")
        estrofe = str(estrofe).replace("<p>", "").replace("</p>", "")
        estrofe = estrofe.replace("<br/>", ".")
        letra_tratada += estrofe + "."
    return letra_tratada.strip()



# Verificar qual o estilo esta se buscando
args = sys.argv
if len(args) < 2:
    print("Comando invalido, execute o script conforme o exemplo:")
    print("$ python3 crawler.py genero_musical")
else:
    site = "https://www.letras.mus.br"
    
    discografia = "discografia/"
    #realizar tratamento para mapear os endpoints aos scripts 
    
    #criar pasta data
    pasta = ".//data"
    if not os.path.isdir(pasta): # vemos de este diretorio ja existe
        os.mkdir(pasta) # aqui criamos a pasta caso nao exista
        print ('Pasta criada com sucesso!')
    
    # Recolhendo genero musicals
    genero =  args[1]


    page = requests.get(site+ "/mais-acessadas/" + genero)
    beautifulSoup = BeautifulSoup(page.text, 'lxml')

    cnt = beautifulSoup.select('.top-list_art a')

    artistas = []
    #Buscar todos os artistas cadastrados no site e os links para suas páginas
    for item in cnt:
        cantor = str(item.find("b"))
        endpoint = item["href"]
        artistas.append([cantor,endpoint])

    musicas = []

    # realiza uma musica no top 25 artistas
    artistas = artistas[:26]
    #print(artistas)

    # Buscar os discos e links de cada cantor
    for artista in artistas:
        print(artista)    
        linkArtista = artista[1]
        pageArtista = requests.get(site + linkArtista + discografia)
        beautifulSoup = BeautifulSoup(pageArtista.text, 'lxml')

        discos = beautifulSoup.select('.cnt-discografia_info .h3 a')
        infoDisco = beautifulSoup.select('.cnt-discografia_info span')
        #print(getAno(descricao[0]))
        '''
        # Verifica todos os discos
        for disco in discos:
            print("Album = " + getTituloAlbum(disco))
        '''

        # Buscar as informações da musica do disco passado
        for index in range(len(discos)):
            pageDisco = requests.get(site + discos[index]["href"])
            beautifulSoup = BeautifulSoup(pageDisco.text, 'lxml')

            linksMusicas = beautifulSoup.select('.cnt-list.cnt-list--num.cnt-list--col2 a')
            #cnt-list cnt-list--num cnt-list--col2
            #print(discos[index]["href"])
            print(linksMusicas[0]["href"])
            #print("Cantor:", getCantor(cantor))
            #print("Titulo musica:",linksMusicas[0]["title"])

            print("Cantor:",getCantor(artista[0]))
            print("album:", getTituloAlbum(discos[index]))
            # Buscar letra da musica
            for linkMusica in linksMusicas:
                pageMusica = requests.get(site + linkMusica["href"])
                beautifulSoup = BeautifulSoup(pageMusica.text, 'lxml')
                musica = beautifulSoup.select('.cnt-letra p')
                compositores = beautifulSoup.select('.letra-info_comp')
                print("Titulo musica:",linkMusica["title"])
                #print("Compositores:", tratarCompositores(compositores))
                print(musica)
                print(tratarLetraMusica(musica))
                musicas.append([genero, getCantor(artista[0]), getTituloAlbum(discos[index]),  getAno(infoDisco[index]),
                                linkMusica["title"], tratarCompositores(compositores), tratarLetraMusica(musica)])
            print("adicionado")
    # Salvar dados em um arquivo csv
    salvar(pasta, musicas, genero)