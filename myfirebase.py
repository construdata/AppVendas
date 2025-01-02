#https://cloud.google.com/identity-platform/docs/use-rest-api?hl=pt-br
#https://console.firebase.google.com/project/aplicativovendashash-ed6c7/settings/general?hl=pt-br&fb_gclid=CjwKCAiApsm7BhBZEiwAvIu2X8QfFrXQFn73wV75p7e11p0p1itKBUxJuzIFEmlZ6xhEKVc0OFVQGxoCXywQAvD_BwE

import requests
from kivy.app import App #para importar a class App do arquivo main.py e usar o self.root


class MyFirebase():
    API_KEY = "AIzaSyDeturkYeFH20fGYlJDG7nvlcEt7eHAAKg" #Essa chave API é gerada após cadastrar a forma de autenticação "Authentication"  (usuário e senha) do Projeto. Fica disponível em Configurações do Projeto (engrenagem)

    def criar_conta(self, email, senha): # função para criar conta via API Google no FireBase
        link = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.API_KEY}"
        
        #Padrão Payload do corpo da solicitação (está na documentação da API Google)
        info = {"email": email, 
                "password": senha, 
                "returnSecureToken": True}
        requisicao = requests.post(link, data=info)
        requisicao_dic = requisicao.json()
        
        if requisicao.ok:
            print("Conta criada com sucesso")
            id_token = requisicao_dic["idToken"] #Token de autenticação para restrições de acesso no FireBase
            refresh_token = requisicao_dic["refreshToken"] #Token que mantem o usuário logado (sem precisar fazer login com email e senha novamente)
            local_id = requisicao_dic["localId"] #Será o Id do usuário no banco de dados Firebase
            
            meu_aplicativo = App.get_running_app()
            meu_aplicativo.local_id = local_id
            meu_aplicativo.id_token = id_token

            #Para "perpetuar" a variável refresh_token e garantir que o usuário abra novamente o arquivo sem precisar fazer login novamente, utiliza-se um outro arquivo de texto .txt
            with open("refreshtoken.txt", "w") as arquivo: #para criar o arquivo novo .txt com o refresh_token
                arquivo.write(refresh_token)
        
            #Para verificar qual é o proximo_id_vendedor disponível no Firebase para vincular ao cadastro do vendedor de forma automática
            req_id = requests.get(f"https://aplicativovendashash-ed6c7-default-rtdb.firebaseio.com/proximo_id_vendedor.json?auth={self.id_token}")
            id_vendedor = req_id.json()

            #Para criar o usuário no banco de dados Firebase
            link = f"https://aplicativovendashash-ed6c7-default-rtdb.firebaseio.com/{local_id}.json?auth={self.id_token}"
            info_usuario = f'{{"avatar": "foto1.png", "equipe":"", "total_vendas":"0", "vendas":"", "id_vendedor": "{id_vendedor}"}}' #dados "padrão" inicial do novo usuário
            requisicao_usuario = requests.patch(link, data=info_usuario)  #Por regra no Firebase, precisa ser patch para criar o usuário, não pode ser o post pois senão ele cria o usuário com outro Id
            
            #Para atualizar o valor do proximo_id_vendedor no Firebase
            proximo_id_vendedor = int(id_vendedor) + 1
            info_id_vendedor = f'{{"proximo_id_vendedor": "{proximo_id_vendedor}"}}'
            requests.patch(f"https://aplicativovendashash-ed6c7-default-rtdb.firebaseio.com/.json?auth={self.id_token}", data=info_id_vendedor)
                                    
            meu_aplicativo.carregar_infos_usuario() #para carregar os dados do usuário recem criado
            meu_aplicativo.mudar_tela("homepage") #levar o usuário para a HomePage após o cadastro

        else:
            mensagem_erro = requisicao_dic["error"]["message"]
            meu_aplicativo = App.get_running_app()
            pagina_login = meu_aplicativo.root.ids["loginpage"]
            pagina_login.ids["mensagem_login"].text = mensagem_erro
            pagina_login.ids["mensagem_login"].color = (1,0,0,0.5) #mensagem erro cor vermelha
        print(requisicao_dic)

    def fazer_login(self, email, senha):
        link = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.API_KEY}' #link para fazer login com e-mail/senha(https://cloud.google.com/identity-platform/docs/use-rest-api?hl=pt-br)
        info = {
            "email": email,
            "password": senha,
            "returnSecureToken": True
        }
        requisicao = requests.post(link, data=info)
        requisicao_dic = requisicao.json()
        
        if requisicao.ok:
            refresh_token = requisicao_dic["refreshToken"] #Token que mantem o usuário logado (sem precisar fazer login com email e senha novamente)
            id_token = requisicao_dic["idToken"] #Token de autenticação para restrições de acesso no FireBase
            local_id = requisicao_dic["localId"] #Será o Id do usuário no banco de dados Firebase

            meu_aplicativo = App.get_running_app()
            meu_aplicativo.local_id = local_id
            meu_aplicativo.id_token = id_token

            with open("refreshtoken.txt", "w") as arquivo: #para criar o arquivo novo .txt com o refresh_token
                arquivo.write(refresh_token)
            meu_aplicativo.carregar_infos_usuario() #para carregar os dados do usuário recem logado
            meu_aplicativo.mudar_tela("homepage") #levar o usuário para a HomePage depois de logar

        else:
            mensagem_erro = requisicao_dic["error"]["message"]
            meu_aplicativo = App.get_running_app()
            pagina_login = meu_aplicativo.root.ids["loginpage"] 
            pagina_login.ids["mensagem_login"].text = mensagem_erro  
            pagina_login.ids["mensagem_login"].color = (1,0,0,0.5) #mensagem erro cor vermelha
        
    def trocar_token(self, refresh_token): #função para logar com RefreshToken
        link = f"https://securetoken.googleapis.com/v1/token?key={self.API_KEY}" #link Trocar um token de atualização por um token de ID (https://cloud.google.com/identity-platform/docs/use-rest-api?hl=pt-br)
        info = {"grant_type": "refresh_token", "refresh_token": refresh_token}
        requisicao = requests.post(link, data=info)
        requisicao_dic = requisicao.json()
        local_id = requisicao_dic["user_id"] #local_id é o user_id do dicionário
        id_token = requisicao_dic["id_token"] #Token de autenticação para restrições de acesso no FireBase
        return local_id, id_token