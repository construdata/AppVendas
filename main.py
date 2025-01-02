# no arquivo main.py vai estar a lógica do app
# no arquivo main.kv vai estar a parte visual do app


from kivy.app import App
from kivy.lang import Builder
from telas import *
from botoes import *
import requests
from bannervenda import BannerVenda
import os
import certifi #certificado de segurança para o requests no Kivy https
from functools import partial #Permite passar um parametro para uma função que está sendo utilizada para o botão, será utilizado na função de seleção de foto de perfil
from myfirebase import MyFirebase
from bannervendedor import BannerVendedor
from datetime import date

os. environ["SSL_CERT_FILE"] = certifi.where() #certificado de segurança obrigatório para o requests no Kivy https

GUI = Builder.load_file("main.kv")

class MainApp(App):
    cliente = None
    produto = None
    unidade = None

    
    def build(self):
        self.firebase = MyFirebase()
        return GUI
    
    def on_start(self): #função padrão para iniciar o App
        #carregar as fotos de perfil
        arquivos = os.listdir('icones/fotos_perfil')
        pagina_fotoperfil = self.root.ids['fotoperfilpage']
        lista_fotos = pagina_fotoperfil.ids['lista_fotos_perfil']
        for foto in arquivos:
            imagem = ImageButton(source= f'icones/fotos_perfil/{foto}', on_release=partial(self.mudar_foto_perfil, foto))
            lista_fotos.add_widget(imagem)

        #Carregar as fotos dos clientes
        arquivos = os.listdir('icones/fotos_clientes')
        pagina_adicionarvendas = self.root.ids['adicionarvendaspage']
        lista_clientes = pagina_adicionarvendas.ids['lista_clientes']
        for foto_cliente in arquivos:
            imagem = ImageButton(source= f'icones/fotos_clientes/{foto_cliente}', on_release=partial(self.selecionar_cliente, foto_cliente))
            label = LabelButton(text= foto_cliente.replace(".png", "").capitalize(), on_release=partial(self.selecionar_cliente, foto_cliente))
            lista_clientes.add_widget(imagem)
            lista_clientes.add_widget(label)

        #carregar as fotos dos produtos
        arquivos = os.listdir('icones/fotos_produtos')
        pagina_adicionarvendas = self.root.ids['adicionarvendaspage']
        lista_produtos = pagina_adicionarvendas.ids['lista_produtos']
        for foto_produto in arquivos:
            imagem = ImageButton(source= f'icones/fotos_produtos/{foto_produto}', on_release=partial(self.selecionar_produto, foto_produto))
            label = LabelButton(text= foto_produto.replace(".png", "").capitalize(), on_release=partial(self.selecionar_produto, foto_produto))
            lista_produtos.add_widget(imagem)
            lista_produtos.add_widget(label)

        #carregar a data
        pagina_adicionarvendas = self.root.ids['adicionarvendaspage']
        label_data = pagina_adicionarvendas.ids['label_data']
        label_data.text = f"Data: {date.today().strftime('%d/%m/%Y')}"

        #Chama a função para carregar infos do usuário
        self.carregar_infos_usuario()
       
    def carregar_infos_usuario(self):
        try:
            #Utilizar dados do refresh_token para pegar infos do usuário, caso ele já tenha cadastro
            with open("refreshtoken.txt", "r") as arquivo:
                refresh_token = arquivo.read() #le o refresh_token que foi salvo no arquivo refreshtoken.txt
            local_id, id_token = self.firebase.trocar_token(refresh_token) #função do myfirebase para trocar o refresh_token por um id_token
            self.local_id = local_id
            self.id_token = id_token

            #pegar informações do usuário
            requisicao = requests.get(f"https://aplicativovendashash-ed6c7-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}") #link do App no Firebase + /.json , "auth" serve para segurança, precisa estar validado nas Regras do Firebase
            requisicao_dic = requisicao.json()
            
            #preencher foto de perfil
            avatar = requisicao_dic['avatar']
            self.avatar = avatar
            foto_perfil = self.root.ids["foto_perfil"]
            foto_perfil.source = f'icones/fotos_perfil/{avatar}' #atualiza a foto de perfil do usuário conforme está no banco de dados
            
            #preencher o total de vendas do usuário
            total_vendas = requisicao_dic['total_vendas']
            self.total_vendas = total_vendas
            homepage = self.root.ids['homepage']
            homepage.ids['label_total_vendas'].text = f'[color=#000000]Total de vendas:[/color] [b]R$ {total_vendas}[/b]'

            #preencher o ID único do usuário
            id_vendedor = requisicao_dic['id_vendedor']
            self.id_vendedor = id_vendedor
            pagina_ajustes = self.root.ids['ajustespage']
            pagina_ajustes.ids['id_vendedor'].text = f'Seu ID Vendedor: {id_vendedor}'

            #Para preencher a equipe do vendedor
            self.equipe = requisicao_dic['equipe']
          
            #preencher lista de vendas
            try:
                vendas = requisicao_dic['vendas']
                self.vendas = vendas
                pagina_homepage = self.root.ids['homepage']
                lista_vendas = pagina_homepage.ids["lista_vendas"]
                for id_venda in vendas:
                    venda = vendas[id_venda]
                    banner = BannerVenda(cliente=venda['cliente'], foto_cliente=venda['foto_cliente'], produto=venda['produto'], foto_produto=venda['foto_produto'], data=venda['data'], preco=venda['preco'], unidade=venda['unidade'], quantidade=venda['quantidade'])
                    lista_vendas.add_widget(banner) #para adicionar vendas no banner
            except Exception as excecao:
                print(excecao)
            
            #Para preencher a equipe do vendedor
            equipe = requisicao_dic['equipe']
            lista_equipe = equipe.split(",")
            pagina_listarvendedores = self.root.ids['listarvendedorespage']
            lista_vendedores = pagina_listarvendedores.ids["lista_vendedores"]

            for id_vendedor_equipe in lista_equipe:
                if id_vendedor_equipe != "":
                    banner_vendedor = BannerVendedor(id_vendedor=id_vendedor_equipe)
                    lista_vendedores.add_widget(banner_vendedor)
          
                self.mudar_tela("homepage") #ir para a homepage após o 1ºlogin
        
        except Exception as excecao1:
                print(excecao1)

    def mudar_tela(self, id_tela):
        print(id_tela)
        gerenciador_telas = self.root.ids["screen_manager"] #sempre que utilizar o self.root está referenciando o arquivo main.kv com os seus ids
        gerenciador_telas.current = id_tela #current é a tela atual

    def mudar_foto_perfil(self, foto, *args):
        foto_perfil = self.root.ids["foto_perfil"]
        foto_perfil.source = f'icones/fotos_perfil/{foto}' #atualiza a foto de perfil do usuário somente na tela do app
        info = f'{{"avatar": "{foto}"}}' #precisa enviar para o banco de dados o dicionário todo em formato de texto no json
        requisicao = requests.patch(f'https://aplicativovendashash-ed6c7-default-rtdb.firebaseio.com/{self.local_id}.json??auth={self.id_token}', data=info) #data é a informação a ser atualizada no banco de dados

        self.mudar_tela("homepage")
    
    def adicionar_vendedor(self, id_vendedor_adicionado):
        link = f'https://aplicativovendashash-ed6c7-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"&equalTo="{id_vendedor_adicionado}"'
        requisicao = requests.get(link)
        requisicao_dic = requisicao.json()
        
        pagina_adicionarvendedor = self.root.ids['adicionarvendedorpage']
        mensagem_texto = pagina_adicionarvendedor.ids['mensagem_outrovendedor']

        if requisicao_dic == {}: #caso o vendedor nao exista no banco de dados
            mensagem_texto.text = "Vendedor não encontrado"
        else:
            equipe = self.equipe.split(",")
            if id_vendedor_adicionado in equipe:
                mensagem_texto.text = "Vendedor já adicionado na equipe"
            else:
                self.equipe = self.equipe + f",{id_vendedor_adicionado}"              
                info = f'{{"equipe": "{self.equipe}"}}'
                requests.patch(f'https://aplicativovendashash-ed6c7-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}', data=info)
                mensagem_texto.text = "Vendedor adicionado com sucesso"

                #Para adicionar um novo banner na lista de vendedores
                pagina_listavendedores = self.root.ids['listarvendedorespage']
                lista_vendedores = pagina_listavendedores.ids["lista_vendedores"]
                banner_vendedor = BannerVendedor(id_vendedor=id_vendedor_adicionado)
                lista_vendedores.add_widget(banner_vendedor)

    def selecionar_cliente(self, foto, *args):
        self.cliente = foto.replace(".png", "") # usa o self. para gravar informação e utilizar na função adicionar_venda()
        #pintar de branco todas as outras letras
        pagina_adicionarvendas = self.root.ids['adicionarvendaspage']
        lista_clientes = pagina_adicionarvendas.ids['lista_clientes']
        for item in list(lista_clientes.children): #para selecionar os itens da lista de clientes
            item.color = (1, 1, 1, 1)   #cor branca               
            #pintar de azul o item selecionado
            # foto -> carrefour.png / Label -> Carrefour -> carrefour.png
            try:
                texto = item.text
                texto = texto.lower() + ".png"
                if foto == texto:
                    item.color = (0, 207/255, 219/255, 1) #cor azul
            except:
                pass
    def selecionar_produto(self, foto, *args):
        #pintar de branco todas as outras letras
        self.produto = foto.replace(".png", "") # usa o self. para gravar informação e utilizar na função adicionar_venda()
        pagina_adicionarvendas = self.root.ids['adicionarvendaspage']
        lista_produtos = pagina_adicionarvendas.ids['lista_produtos']
        for item in list(lista_produtos.children): #para selecionar os itens da lista de produtos
            item.color = (1, 1, 1, 1)   #cor branca               
            #pintar de azul o item selecionado
            # foto -> arroz.png / Label -> Arroz -> arroz.png
            try:
                texto = item.text
                texto = texto.lower() + ".png"
                if foto == texto:
                    item.color = (0, 207/255, 219/255, 1) #cor azul
            except:
                pass

    def selecionar_unidade(self, id_label, *args):
        pagina_adicionarvendas = self.root.ids['adicionarvendaspage']
        self.unidade = id_label.replace("unidades_", "") # usa o self. para gravar informação e utilizar na função adicionar_venda()
        #pintar de branco todas as outras letras
        pagina_adicionarvendas.ids["unidades_kg"].color = (1, 1, 1, 1)
        pagina_adicionarvendas.ids["unidades_unidades"].color = (1, 1, 1, 1)
        pagina_adicionarvendas.ids["unidades_litros"].color = (1, 1, 1, 1)
        #pintar de azul o item selecionado
        pagina_adicionarvendas.ids[id_label].color = (0, 207/255, 219/255, 1) #cor azul
 
    def adicionar_venda(self):
        cliente = self.cliente
        produto = self.produto
        unidade = self.unidade
        pagina_adicionarvendas = self.root.ids['adicionarvendaspage']
        data = pagina_adicionarvendas.ids['label_data'].text.replace("Data: ", "")
        preco = pagina_adicionarvendas.ids['preco_total'].text
        quantidade = pagina_adicionarvendas.ids['quantidade'].text 
        
        if not cliente:
            pagina_adicionarvendas.ids['label_selecione_cliente'].color = (1,0,0,1) #cor vermelha
        if not produto:
            pagina_adicionarvendas.ids['label_selecione_produto'].color = (1,0,0,1) #cor vermelha
        if not unidade:
            pagina_adicionarvendas.ids['unidades_kg'].color = (1,0,0,1) #cor vermelha
            pagina_adicionarvendas.ids['unidades_unidades'].color = (1,0,0,1) #cor vermelha
            pagina_adicionarvendas.ids['unidades_litros'].color = (1,0,0,1) #cor vermelha   
       
        if not preco:
            pagina_adicionarvendas.ids['label_preco'].color = (1,0,0,1) #cor vermelha
        else:
            try:
                preco = float(preco) #para verificar se foi preenchido o campo com valor float
            except:
                pagina_adicionarvendas.ids['label_preco'].color = (1,0,0,1) #cor vermelha
        
        if not quantidade:
            pagina_adicionarvendas.ids['label_quantidade'].color = (1,0,0,1) #cor vermelha        
        else:
            try:
                quantidade  = float(quantidade) #para verificar se foi preenchido o campo com valor float
            except:
                pagina_adicionarvendas.ids['label_quantidade'].color = (1,0,0,1) #cor vermelha

        if cliente and produto and unidade and preco and quantidade and (type(preco) == float) and (type(quantidade) == float): #se todos os campos foram preenchidos corretamente
            foto_produto = produto + ".png"
            foto_cliente = cliente + ".png"  
            #enviar os dados da venda para o firebase
            info = f'{{"cliente": "{cliente}", "foto_produto": "{foto_produto}", "produto": "{produto}", "foto_cliente": "{foto_cliente}", "data": "{data}", "preco": "{preco}", "quantidade": "{quantidade}", "unidade": "{unidade}"}}'
            requests.post(f'https://aplicativovendashash-ed6c7-default-rtdb.firebaseio.com/{self.local_id}/vendas.json?auth={self.id_token}', data=info)

            #atualizar o banner de venda do vendedor no app
            banner = BannerVenda(cliente=cliente, foto_cliente=foto_cliente, produto=produto, foto_produto=foto_produto, data=data, unidade=unidade, quantidade=quantidade, preco=preco)
            pagina_homepage = self.root.ids['homepage']   
            lista_vendas = pagina_homepage.ids['lista_vendas']
            lista_vendas.add_widget(banner)
            
            #atualizar o total de vendas do vendedor no firebase
            requisicao = requests.get(f"https://aplicativovendashash-ed6c7-default-rtdb.firebaseio.com/{self.local_id}/total_vendas.json?auth={self.id_token}")
            total_vendas = float(requisicao.json())
            total_vendas = float(total_vendas) + float(preco)
            info = f'{{"total_vendas": "{total_vendas}"}}'
            requests.patch(f"https://aplicativovendashash-ed6c7-default-rtdb.firebaseio.com/{self.local_id}/.json?auth={self.id_token}", data=info)
            
            #atualizar o total de vendas no app
            homepage = self.root.ids['homepage']
            homepage.ids['label_total_vendas'].text = f'[color=#000000]Total de vendas:[/color] [b]R$ {total_vendas}[/b]'
            
            #voltar para a Homepage
            self.mudar_tela("homepage")

        #Para setar como "vazio" a tela de adicionar vendas no próximo login
        self.cliente = None
        self.produto = None
        self.unidade = None
    
    def carregar_todas_vendas(self):
        #limpar a pagina todasvendaspage para evitar duplicação do banner
        pagina_todasvendas = self.root.ids['todasvendaspage']
        lista_vendas = pagina_todasvendas.ids['lista_vendas']
        
        for item in list(lista_vendas.children): #para selecionar os itens da lista de vendas
            lista_vendas.remove_widget(item) #para remover os itens da lista de vendas

        #preencher a pagina todasvendaspage
        #pegar informações da empresa
        requisicao = requests.get(f'https://aplicativovendashash-ed6c7-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"') #pegar informações de todos os vendedores no Firebase + /.json 
        requisicao_dic = requisicao.json()
        
        #preencher foto de perfil da empresa
        foto_perfil = self.root.ids["foto_perfil"]
        foto_perfil.source = f'icones/fotos_perfil/hash.png' #atualiza a foto de perfil da empresa "fixo"
        
        #preencher o total de vendas da empresa
        pagina_todasvendas = self.root.ids['todasvendaspage']
        lista_vendas = pagina_todasvendas.ids['lista_vendas']
        total_vendas = 0
        for local_id_usuario in requisicao_dic:
            try:
                vendas = requisicao_dic[local_id_usuario]['vendas']
                for id_venda in vendas:
                    venda = vendas[id_venda]
                    total_vendas += float(venda['preco'])  #total_vendas = total_vendas + (venda['preco']*venda['quantidade'])
                    banner = BannerVenda(cliente=venda['cliente'], foto_cliente=venda['foto_cliente'], produto=venda['produto'], foto_produto=venda['foto_produto'], data=venda['data'], preco=venda['preco'], unidade=venda['unidade'], quantidade=venda['quantidade'])
                    lista_vendas.add_widget(banner)
            except Exception as excecao:
                print(excecao)
        
        #preencher o total de vendas da empresa
        pagina_todasvendas.ids['label_total_vendas'].text = f'[color=#000000]Total de vendas:[/color] [b]R$ {total_vendas}[/b]'
        

        #redirecionar para pagina todasvendaspage
        self.mudar_tela("todasvendaspage")

    def sair_todas_vendas(self, id_tela):
        foto_perfil = self.root.ids["foto_perfil"]
        foto_perfil.source = f'icones/fotos_perfil/{self.avatar}' #retorna para a foto do usuário
        self.mudar_tela(id_tela)

    def carregar_vendas_vendedor(self, dic_info_vendedor, *args): #*args em razão do partial na função
        try:
            vendas = dic_info_vendedor['vendas']
            pagina_vendasoutrovendedor = self.root.ids['vendasoutrovendedorpage']
            lista_vendas = pagina_vendasoutrovendedor.ids['lista_vendas']
            
            #limpar a pagina todasvendaspage para evitar duplicação do banner
            for item in list(lista_vendas.children): #para selecionar os itens da lista de vendas
                lista_vendas.remove_widget(item) #para remover os itens da lista de vendas
                
            for id_venda in vendas:
                venda = vendas[id_venda]
                banner = BannerVenda(cliente=venda['cliente'], foto_cliente=venda['foto_cliente'], produto=venda['produto'], foto_produto=venda['foto_produto'], data=venda['data'], preco=venda['preco'], unidade=venda['unidade'], quantidade=venda['quantidade'])
                lista_vendas.add_widget(banner)
        except Exception as excecao:
            print(excecao)
        
        #preencher o total de vendas do vendedor
        total_vendas = dic_info_vendedor['total_vendas']
        pagina_vendasoutrovendedor.ids['label_total_vendas'].text = f'[color=#000000]Total de vendas:[/color] [b]R$ {total_vendas}[/b]'

        #preencher foto de perfil do vendedor
        foto_perfil = self.root.ids["foto_perfil"]
        avatar = dic_info_vendedor['avatar']
        foto_perfil.source = f'icones/fotos_perfil/{avatar}' #atualiza a foto de perfil do vendedor
        
        self.mudar_tela("vendasoutrovendedorpage")

MainApp().run()
