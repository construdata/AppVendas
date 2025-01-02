from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle

class BannerVenda(GridLayout):

    def atualizar_rec(self, *args): #função para redimencionar a cor de fundo da lista de vendas
        self.rec.pos = self.pos
        self.rec.size = self.size

    def __init__(self, **kwargs): #função para criar o banner, **kwards é um dicionário com todas as informações do banner 
        self.rows = 1
        super().__init__() #para utilizar todas as propriedades do GridLayout

        with self.canvas:
            Color(rgba=(0,0,0,0.3)) #fundo preto na lista de vendas
            self.rec = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos= self.atualizar_rec, size=self.atualizar_rec)

        cliente = kwargs['cliente']
        foto_cliente = kwargs['foto_cliente']
        produto = kwargs['produto']
        foto_produto = kwargs['foto_produto']
        data= kwargs['data']
        unidade = kwargs['unidade']
        quantidade = float(kwargs['quantidade'])
        preco = float(kwargs['preco'])

        #Cliente
        esquerda = FloatLayout()
        esquerda_imagem = Image(pos_hint= {"right":1, "top":0.95}, size_hint= (1, 0.75), source= f'icones/fotos_clientes/{foto_cliente}')
        esquerda_label = Label(text=cliente, size_hint= (1, 0.2), pos_hint= {"right":1, "top":0.2})
        esquerda.add_widget(esquerda_imagem)
        esquerda.add_widget(esquerda_label)
       
       #Produto
        meio = FloatLayout()
        meio_imagem = Image(pos_hint= {"right":1, "top":0.95}, size_hint= (1, 0.75), source= f'icones/fotos_produtos/{foto_produto}')
        meio_label = Label(text=produto, size_hint= (1, 0.2), pos_hint= {"right":1, "top":0.2})
        meio.add_widget(meio_imagem)
        meio.add_widget(meio_label)

        #Detalhes
        direita = FloatLayout()
        direita_label_data = Label(text= f'Data: {data}', size_hint= (1, 0.33), pos_hint= {"right":1, "top":0.9})
        direita_label_preco = Label(text= f'Preço: R$ {preco:,.2f}', size_hint= (1, 0.33), pos_hint= {"right":1, "top":0.65})
        direita_label_quantidade = Label(text= f'{quantidade} {unidade}', size_hint= (1, 0.33), pos_hint= {"right":1, "top":0.4})
        direita.add_widget(direita_label_data)
        direita.add_widget(direita_label_preco)
        direita.add_widget(direita_label_quantidade)

        self.add_widget(esquerda)
        self.add_widget(meio)
        self.add_widget(direita)