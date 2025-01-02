from botoes import ImageButton, Label, LabelButton
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle
import requests
from kivy.app import App #para importar a class App do arquivo main.py e usar o self.root
from functools import partial   

class BannerVendedor(FloatLayout):

    def __init__(self, **kwargs): #função para criar o banner, **kwards é um dicionário com todas as informações do banner
        super().__init__() #para utilizar todas as propriedades do FloatLayout
        
        with self.canvas:
            Color(rgba=(0,0,0,0.3)) #fundo preto na lista de vendas
            self.rec = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos= self.atualizar_rec, size=self.atualizar_rec)

        id_vendedor = kwargs['id_vendedor']
       
        link = f'https://aplicativovendashash-ed6c7-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"&equalTo="{id_vendedor}"' #link do App no Firebase com parametros de filtro pelo id_vendedor e orderby, foi necessário incluir Regras ".indexOn": ["id_vendedor"] na config do firebase para que o filtro funcionasse
        requisicao = requests.get(link)
        requisicao_dic = requisicao.json()
        print(requisicao_dic)
        valor = list(requisicao_dic.values())[0] #precisar transformar em lista para preencher o valor do banner com o valor do primeiro item da lista 
        avatar = valor['avatar']
        total_vendas = valor['total_vendas']
        
        meu_aplicativo = App.get_running_app() #para interagir com a class App principal main.py

        imagem = ImageButton(source=f'icones/fotos_perfil/{avatar}', pos_hint={"right": 0.4, "top": 0.9}, size_hint=(0.3, 0.8), on_release=partial(meu_aplicativo.carregar_vendas_vendedor, valor))
        label_id = LabelButton(text=f'ID Vendedor: {id_vendedor}', pos_hint={"right": 0.9, "top": 0.9}, size_hint=(0.5, 0.5), on_release=partial(meu_aplicativo.carregar_vendas_vendedor, valor))
        label_total = LabelButton(text=f'Total de Vendas: R$ {total_vendas}', pos_hint={"right": 0.9, "top": 0.6}, size_hint=(0.5, 0.5), on_release=partial(meu_aplicativo.carregar_vendas_vendedor, valor))

        self.add_widget(imagem)
        self.add_widget(label_id)
        self.add_widget(label_total)

    def atualizar_rec(self, *args): #função para redimencionar a cor de fundo da lista de vendas
        self.rec.pos = self.pos
        self.rec.size = self.size
        
        
        
        
        
    