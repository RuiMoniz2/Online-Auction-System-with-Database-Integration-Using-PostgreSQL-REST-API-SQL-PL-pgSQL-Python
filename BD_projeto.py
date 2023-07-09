from typing import ContextManager
from flask import Flask, jsonify, request
import logging, psycopg2, time
from datetime import datetime
import random

app = Flask(__name__)

TOKENSDICT = {1 : 1000}

#OK
@app.route("/dbproj/user", methods=['POST']) 
def registoJSON():

    args = request.get_json()

    username = args.get("username")
    password = args.get("password")
    nome = args.get("nome")
    e_mail = args.get("e_mail")
    sexo = args.get("sexo")
    data_nascimento = args.get("data_nascimento")
    morada = args.get("morada")

    content = {}
    flag = True
    if password == None or username == None or nome == None or e_mail == None or sexo == None or data_nascimento == None or morada == None:
        content = {"Erro404" :  "Existem dado(s) em falta."}
        flag = False
    else:
        if confirmarCaracteresValidosUsername(username) == False:
            content.update({"Erro0" :  "Username não é válido. Não pode utilizar caracteres especiais."})
            flag = False
        if confirmarCaracteresValidosPassword(password) == False:
            content.update({"Erro1" :  "Password não é válida. Não pode utilizar caracteres especiais."})
            flag = False
        if confirmarCaracteresValidosNome(nome) == False:
            content.update({"Erro2" :  "Nome não é válido. Não pode utilizar caracteres especiais."})
            flag = False
        if confirmarCaracteresValidosMail(e_mail) == False:
            content.update({"Erro3" :  "Mail não é válido. Não pode utilizar caracteres especiais."})
            flag = False
        if sexo != "M" and sexo != "F":
            content.update({"Erro4" :  "Sexo não é válido. Deve introduzir apenas M ou F."})
            flag = False
        if confirmarData(data_nascimento) == False:
            content.update({"Erro5" :  "Formato de data inválido"})
            flag = False
        if confirmarCaracteresValidos(morada) == False:
            content.update({"Erro6" :  "Morada não é válida. Não pode utilizar caracteres especiais."})
            flag = False
    
    if flag:
        con = psycopg2.connect(
            host = "localhost",
            database = "Projeto",
            user = "postgres",
            password = "postgres",
            port  = 5432,
            )
        c1 = con.cursor()
        c1.execute("select * from criarutilizador('%s','%s','%s','%s','%s','%s','%s')" % (username, password, nome, e_mail, sexo, data_nascimento, morada))
        id = c1.fetchall()
        id = id[0][0]
        content = {"userID" : id}
        c1.close()
        con.commit()
        con.close()

    return jsonify(content)

#OK
@app.route("/dbproj/user", methods=['PUT']) 
def loginJSON():

    args = request.get_json()

    username = args.get("username")
    password = args.get("password")
    flag = True
    content = {}

    if confirmarCaracteresValidosUsername(username) == False:
        content.update({"Erro0" :  "Username não é válido. Não pode utilizar caracteres especiais."})
        flag = False
    if confirmarCaracteresValidosPassword(password) == False:
        content.update({"Erro1" :  "Password não é válida. Não pode utilizar caracteres especiais."})
        flag = False

    if flag:
        con = psycopg2.connect(
                host = "localhost",
                database = "Projeto",
                user = "postgres",
                password = "postgres",
                port  = 5432,
                )
        c1 = con.cursor()
        c1.execute("select login('%s','%s')" % (username, password))
        resultado = c1.fetchall()
        resultado = resultado[0][0]
        c1.close()
        con.close()
        if password == None or username == None:
            content = {"Erro404" :  "Username e/ou Password em falta."}
        elif resultado == -1:
            content = {"Erro1" :  "Username ou Password incorretos."}
        else:
            token = random.randint(0,9999999999)
            content = {"authToken" :  "Login realizado com sucesso! Token: %s" % (token)} 
            TOKENSDICT.update({token : resultado})

    return jsonify(content)
 
#OK
@app.route("/dbproj/leilao", methods=['POST']) 
def criarLeilaoJSON():
    args = request.get_json()

    tempo = args.get("tempo")
    minimo = args.get("valor_minimo")
    token = args.get("token")
    id = TOKENSDICT.get(token)
    ean = args.get("ean")
    titulo = args.get("titulo")
    descricao = args.get("descricao")

    content = {}

    con = psycopg2.connect(
            host = "localhost",
            database = "Projeto",
            user = "postgres",
            password = "postgres",
            port  = 5432,
            )

    c1 = con.cursor()
    c1.execute("select max(ean) from artigos")
    max = c1.fetchall()
    max = max[0][0]
    flag = True

    if tempo == None or minimo == None or token == None or ean == None or titulo == None or descricao == None:
        content = {"Erro404" :  "Existem dado(s) em falta."}
        flag = False
    else:
        if tempo <= 0:
            content.update({"Erro0" :  "Tempo tem que ser número inteiro positivo."})
            flag = False
        if minimo <= 0:
            content.update({"Erro1" :  "Valor minimo tem que ser número inteiro positivo."})
            flag = False
        if token not in TOKENSDICT:
            content.update({"Erro2" :  "Token não é válido."})
            flag = False
        if ean <= 0 or ean > max:
            content.update({"Erro3" :  "ean não é válido."})
            flag = False
        if confirmarCaracteresValidos(titulo) == False:
            content.update({"Erro4" :  "Título não é válido. Não pode utilizar caracteres especiais."})
            flag = False
        if confirmarCaracteresValidos(descricao) == False:
            content.update({"Erro5" :  "Descração não é válida. Não pode utilizar caracteres especiais."})
            flag = False

    if flag:
        now = datetime.now()
        
        horas = now.hour
        dia = now.day
        mes = now.month
        ano = now.year

        while tempo >= 8784:
            if (((ano % 4 == 0 and ano % 100 != 0) or ano % 400 == 0) and mes <= 2 ) or ((((ano+1) % 4 == 0 and (ano+1) % 100 != 0) or (ano+1) % 400 == 0 ) and mes >= 3 ):
                ano += 1
                tempo -= 8784
            else:
                ano += 1
                tempo -= 8760
        while tempo >= 744:
            if mes == 1 or mes == 3 or mes == 5 or mes == 7 or mes == 8 or mes == 10 or mes == 12:
                tempo -= 744
            elif mes == 2:
                if ((ano % 4 == 0 and ano % 100 != 0) or ano % 400 == 0):
                    tempo -= 694
                else:
                    tempo -= 672
            else:
                tempo
            if mes == 12:
                mes = 1
                ano += 1
            else:
                mes += 1
        while tempo >= 24:
            tempo -= 24
            if dia == 31:
                dia = 1
                if mes == 12:
                    mes = 1
                    ano += 1
                else:
                    mes += 1
            elif (dia == 30 and (mes == 4 or mes == 6 or mes == 9 or mes == 11)):
                dia = 1
                mes += 1
            elif ((dia == 29 and mes == 2) or (dia == 28 and mes == 2 and (ano % 4 != 0 or (ano % 100 == 0 and ano % 400 != 0)))):
                dia = 1
                mes += 1
            else:
                dia += 1
        horas += tempo

        print("AQUI")
        c1.execute("select * from inserirleilao('%d-%d-%d %d:%d:%d', '%d-%d-%d %d:%d:%d',%d,%d,%d,'%s','%s')" % (now.year, now.month, now.day, now.hour, now.minute, now.second, ano, mes, dia, horas, now.minute, now.second, minimo, id, ean, titulo, descricao))
        resultado = c1.fetchall()
        resultado = resultado[0][0]
        con.commit()
        content = {"leilaoID" : resultado}

    c1.close()
    con.close()

    return jsonify(content)

#OK
@app.route("/dbproj/leiloes", methods=['GET']) 
def listarLeiloesAtivosJSON():
    args = request.get_json()

    token = args.get("token")

    content = {}

    if token not in TOKENSDICT:
        content.update({"Erro" :  "Token não é válido."})
        return jsonify(content)
    else:
        con = psycopg2.connect(
            host = "localhost",
            database = "Projeto",
            user = "postgres",
            password = "postgres",
            port  = 5432,
            )

        c1 = con.cursor()
        c1.execute("select * from searchleilaoativo()")
        lista = c1.fetchall()
        contentTotal = []

        #COMPLETA, comentar para ser só ID e descrição
        for i in range(len(lista)):
            content = {}
            content.update({"leilaoID" : lista[i][0]})
            content.update({"titulo" : lista[i][1]})
            content.update({"artigo" : lista[i][2]})
            content.update({"time_criacao" : lista[i][3]})
            content.update({"time_termino" : lista[i][4]})
            content.update({"valor_minimo" : lista[i][5]})
            content.update({"valor_atual" : lista[i][6]})
            #o 7, 8 e 9 estão ignorados propositadamente
            content.update({"username_criador" : lista[i][10]})
            content.update({"descricao" : lista[i][11]})
            contentTotal.append(content)

        c1.close()
        con.close()
        if contentTotal == []:
            contentTotal = {"Informação" : "Não existem leilões ativos de momento."}
        return jsonify(contentTotal)

#OK
@app.route("/dbproj/leiloes/<keyword>", methods=['GET']) 
def pesquisarLeiloes(keyword):
    args = request.get_json()

    token = args.get("token")

    content = {}

    if token not in TOKENSDICT:
        content.update({"Erro" :  "Token não é válido."})
        return jsonify(content)

    else:
        con = psycopg2.connect(
            host = "localhost",
            database = "Projeto",
            user = "postgres",
            password = "postgres",
            port  = 5432,
            )

        key = "%" + keyword + "%"

        c1 = con.cursor()
        c1.execute("select * from searchleilaopdescartigoativos('%s')" % key)
        lista = c1.fetchall()
        contentTotal = []

        #COMPLETA, comentar para ser só ID e descrição
        for i in range(len(lista)):
            content = {}
            content.update({"leilaoID" : lista[i][0]})
            content.update({"titulo" : lista[i][1]})
            content.update({"artigo" : lista[i][2]})
            content.update({"time_criacao" : lista[i][3]})
            content.update({"time_termino" : lista[i][4]})
            content.update({"valor_minimo" : lista[i][5]})
            content.update({"valor_atual" : lista[i][6]})
            #o 7, 8 e 9 estão ignorados propositadamente
            content.update({"username_criador" : lista[i][10]})
            content.update({"descricao" : lista[i][11]})
            contentTotal.append(content)

        c1.close()
        con.close()
        if contentTotal == []:
            contentTotal = {"Informação" : "Não existem leilões ativos cujo artigo tenha na descrição essa string."}
        return jsonify(contentTotal)

#OK
@app.route("/dbproj/leiloes2/<ean>", methods=['GET']) 
def pesquisarLeiloes2(ean):
    args = request.get_json()
    ean = int(ean)
    token = args.get("token")

    content = {}

    if token not in TOKENSDICT:
        content.update({"Erro" :  "Token não é válido."})
        return jsonify(content)

    else:
        con = psycopg2.connect(
            host = "localhost",
            database = "Projeto",
            user = "postgres",
            password = "postgres",
            port  = 5432,
            )

        c1 = con.cursor()
        c1.execute("select * from searchleilaopeanativos(%d)" % ean)
        lista = c1.fetchall()
        contentTotal = []

        #COMPLETA, comentar para ser só ID e descrição
        for i in range(len(lista)):
            content = {}
            content.update({"leilaoID" : lista[i][0]})
            content.update({"titulo" : lista[i][1]})
            content.update({"artigo" : lista[i][2]})
            content.update({"time_criacao" : lista[i][3]})
            content.update({"time_termino" : lista[i][4]})
            content.update({"valor_minimo" : lista[i][5]})
            content.update({"valor_atual" : lista[i][6]})
            #o 7, 8 e 9 estão ignorados propositadamente
            content.update({"username_criador" : lista[i][10]})
            content.update({"descricao" : lista[i][11]})
            contentTotal.append(content)

        c1.close()
        con.close()
        if contentTotal == []:
            contentTotal = {"Informação" : "Não existem leilões ativos cujo artigo tenha esse EAN."}
        return jsonify(contentTotal)

#OK
@app.route("/dbproj/leilao/<leilaoId>", methods=['GET'])
def detalhesLeilao(leilaoId):
    args = request.get_json()

    token = args.get("token")

    content = {}

    if token not in TOKENSDICT:
        content.update({"Erro" :  "Token não é válido."})
        return jsonify(content)

    else:
        con = psycopg2.connect(
            host = "localhost",
            database = "Projeto",
            user = "postgres",
            password = "postgres",
            port  = 5432,
            )

        leilaoId = int(leilaoId)

        c1 = con.cursor()
        c1.execute("select * from searchleilaopid(%d)" % leilaoId) 
        lista = c1.fetchall()
        print(lista)
        if lista == []:
            contentTotal = {"Informação" : "Não existe leilão ccom esse ID."}
            return jsonify(contentTotal)

        contentTotal = []
        content = {}
        i = 0
        content.update({"leilaoID" : lista[i][0]})
        content.update({"titulo" : lista[i][1]})
        content.update({"artigo" : lista[i][2]})
        content.update({"time_criacao" : lista[i][3]})
        content.update({"time_termino" : lista[i][4]})
        content.update({"valor_minimo" : lista[i][5]})
        content.update({"valor_atual" : lista[i][6]})
        content.update({"terminado" : lista[i][7]})
        content.update({"cancelado" : lista[i][8]})
        content.update({"vendido" : lista[i][9]})
        content.update({"username_criador" : lista[i][10]})
        content.update({"descricao" : lista[i][11]})

        contentTotal.append(content)
        contentMeio = []

        c1.execute("select * from showlicitacoes(%d)" % leilaoId)
        tabela = c1.fetchall()
        for linha in tabela:
            content = {}
            content.update({"Data e Hora" : linha[0]})
            content.update({"Username" : linha[1]})
            content.update({"Valor" : linha[2]})
            contentMeio.append(content)

        if contentMeio == []:
            contentMeio = {"Licitações" : "Não exitem licitações neste leilão."}
        contentTotal.append(contentMeio)


        contentMeio = []

        c1.execute("select * from showmensagens(%d)" % leilaoId)
        tabela = c1.fetchall()
        for linha in tabela:
            content = {}
            content.update({"Data e Hora" : linha[0]})
            content.update({"Username" : linha[1]})
            content.update({"Mensagem" : linha[2]})
            contentMeio.append(content)

        if contentMeio == []:
            contentMeio = {"Mensagens" :"Não exitem mensagens neste leilão."}
        contentTotal.append(contentMeio)

        c1.close()
        con.close()
        return jsonify(contentTotal)

#OK
@app.route("/dbproj/leiloesAtividade", methods=['GET'])
def consultarLeiloesAtividade():
    args = request.get_json()

    token = args.get("token")
    id = TOKENSDICT.get(token)
    content = {}

    if token not in TOKENSDICT:
        content.update({"Erro" :  "Token não é válido."})
        return jsonify(content)

    else:
        con = psycopg2.connect(
            host = "localhost",
            database = "Projeto",
            user = "postgres",
            password = "postgres",
            port  = 5432,
            )

        c1 = con.cursor()
        c1.execute("select * from searchleiloesatividade(%d)" % id) 
        lista = c1.fetchall()
        contentTotal = []

        #COMPLETA, comentar para ser só ID e descrição
        for linha in lista:
            content = {}
            content.update({"leilaoID" : linha[0]})
            content.update({"titulo" : linha[1]})
            content.update({"artigo" : linha[2]})
            content.update({"time_criacao" : linha[3]})
            content.update({"time_termino" : linha[4]})
            content.update({"valor_minimo" : linha[5]})
            content.update({"valor_atual" : linha[6]})
            #o 7, 8 e 9 estão ignorados propositadamente
            content.update({"username_criador" : linha[10]})
            content.update({"descricao" : linha[11]})
            contentTotal.append(content)

        c1.close()
        con.close()
        if contentTotal == []:
            contentTotal = {"Informação" : "Não existem nenhum leilão criado por si ou no qual tenha licitado."}
        return jsonify(contentTotal)

#OK
@app.route("/dbproj/licitar/<leilaoId>/<licitacao>", methods=['GET'])
def licitar(leilaoId, licitacao):
    args = request.get_json()

    token = args.get("token")
    id = TOKENSDICT.get(token) 
    leilaoId = int(leilaoId)
    licitacao = int(licitacao)


    content = {}

    if token not in TOKENSDICT:
        content.update({"Erro" :  "Token não é válido."})
        return jsonify(content)
    else:
        if licitacao == None:
            content.update({"Erro404" : "Valor da licitação em falta."})
        else:
            con = psycopg2.connect(
                host = "localhost",
                database = "Projeto",
                user = "postgres",
                password = "postgres",
                port  = 5432,
                )

            c1 = con.cursor()
            c1.execute("select * from confirmarlicitacao(%d, %d, %d)" % (licitacao, leilaoId, id))
            conf = c1.fetchall()
            conf = conf[0][0]
            if conf:
                content.update({"Sucesso" : "Licitação realizada com sucesso."})
            else:
                content.update({"Erro" : "A sua licitação é demasiado baixo ou o leilão já terminou/é inexistente, o leilão não existe ou está a tentar licitar num leilão seu."})

            con.commit()
            c1.close()
            con.close()
    return jsonify(content)
    
#OK
@app.route("/dbproj/leilao/<leilaoId>", methods=['PUT'])
def alterarCaracteristicas(leilaoId):
    args = request.get_json()

    token = args.get("token")
    id = TOKENSDICT.get(token) 
    titulo = args.get("titulo")
    descricao = args.get("descricao")
    leilaoId = int(leilaoId)

    content = {}

    if token not in TOKENSDICT:
        content.update({"Erro" :  "Token não é válido."})
        return jsonify(content)
    else:
        if titulo == None and descricao == None:
            content.update({"Erro404" :  "Data not found."})
        else:
            flag = True
            if titulo != None and confirmarCaracteresValidos(titulo) == False:
                content.update({"Erro1" :  "Titulo contém caracteres inválidos."})
                flag = False
            if descricao != None and confirmarCaracteresValidos(descricao) == False:
                content.update({"Erro2" :  "Descrição contém caracteres inválidos."})
                flag = False

            if flag:
                con = psycopg2.connect(
                    host = "localhost",
                    database = "Projeto",
                    user = "postgres",
                    password = "postgres",
                    port  = 5432,
                    )
                c1 = con.cursor()
                if titulo != None:
                    c1.execute("select * from confirmchangetitle(%d, %d, '%s')" % (id,  leilaoId, titulo))
                    conf = c1.fetchall()
                    conf = conf[0][0]
                    if conf:
                        content.update({"Titulo":"Titulo alterado com sucesso."})
                    else:
                        content.update({"Erro":"Não é o criador deste leilão ou o leilão não existe."})
                if descricao != None:
                    c1.execute("select * from confirmchangedescript(%d, %d, '%s')" % (id,  leilaoId, descricao))
                    conf = c1.fetchall()
                    conf = conf[0][0]
                    if conf:
                        content.update({"descrição":"Descrição alterada com sucesso."})
                    else:
                        content.update({"Erro":"Não é o criador deste leilão ou o leilão não existe."})
                con.commit()
                c1.close()
                con.close()
    return jsonify(content)

#OK
@app.route("/dbproj/escrever/<leilaoId>", methods=['PUT'])
def escreverMensagem(leilaoId):
     args = request.get_json()

     token = args.get("token")
     texto = args.get("mensagem")
     id = TOKENSDICT.get(token) 
     leilaoId = int(leilaoId)

     if confirmarCaracteresValidos(texto) == False:
        content = {"Erro" : "Texte possui caracteres inválidos."}
        return jsonify(content)

     content = {}

     if token not in TOKENSDICT:
        content.update({"Erro" :  "Token não é válido."})
        return jsonify(content)
     else:
         con = psycopg2.connect(
                host = "localhost",
                database = "Projeto",
                user = "postgres",
                password = "postgres",
                port  = 5432,
                )
         c1 = con.cursor()
         c1.execute("select * from inserirmensagem('%s', %d, %d)" % (texto, leilaoId, id))   #confirmar nome funcao
         conf = c1.fetchall()
         conf = conf[0][0]
         if conf:
            content.update({"Sucesso" : "Mensagem enviada com sucesso."})
         else:
            content.update({"Erro" : "Não existe leilão com Id definido."})
         con.commit()
         c1.close()
         con.close()
     return jsonify(content)

#OK
@app.route("/dbproj/notificacoes", methods=['GET'])
def caixaDeEntrada():
     args = request.get_json()

     token = args.get("token")
     id = TOKENSDICT.get(token) 

     content = {}

     if token not in TOKENSDICT:
        content.update({"Erro" :  "Token não é válido."})
        return jsonify(content)
     else:
         con = psycopg2.connect(
                host = "localhost",
                database = "Projeto",
                user = "postgres",
                password = "postgres",
                port  = 5432,
                )
         c1 = con.cursor()
         c1.execute("select * from searchnotifications(%d)" % id)
         tabela = c1.fetchall()

         contentTotal = []

         for i in range(len(tabela)):
             content = {}
             content.update({"Data e hora" : tabela[i][0]})
             content.update({"Notificação" : tabela[i][1]})
             contentTotal.append(content)

         c1.close()
         con.close()
         if contentTotal == []:
             contentTotal = {"Info" : "Não tem notificações."}
         return jsonify(contentTotal)

#OK
@app.route("/dbproj/artigos", methods=['GET'])
def listarArtigos():
    args = request.get_json()

    token = args.get("token")

    content = {}

    if token not in TOKENSDICT:
        content.update({"Erro" :  "Token não é válido."})
        return jsonify(content)
    else:
        con = psycopg2.connect(
            host = "localhost",
            database = "Projeto",
            user = "postgres",
            password = "postgres",
            port  = 5432,
            )

        c1 = con.cursor()
        c1.execute("select * from showartigos()")
        lista = c1.fetchall()
        contentTotal = []

        for i in range(len(lista)):
            content = {}
            content.update({"EAN" : lista[i][0]})
            content.update({"Nome" : lista[i][1]})
            content.update({"Descrição" : lista[i][2]})
            contentTotal.append(content)

        c1.close()
        con.close()
        if contentTotal == []:
            contentTotal = {"Informação" : "Não existem artigos na base de dados."}
        return jsonify(contentTotal)

#OK
@app.route("/dbproj/artigo", methods=['PUT'])
def addArtigo():
    args = request.get_json()

    token = args.get("token")
    nome = args.get("nome")
    descricao = args.get("descricao")




    content = {}

    if token not in TOKENSDICT:
        content.update({"Erro" :  "Token não é válido."})
        return jsonify(content)
    else:
        flag = True
        if confirmarCaracteresValidos(nome) == False:
            content.update({"Erro1" :  "Nome contém caracteres inválidos."})
            flag = False
        if confirmarCaracteresValidos(descricao) == False:
            content.update({"Erro2" :  "Descrição contém caracteres inválidos."})
            flag = False

        if flag:
            con = psycopg2.connect(
                host = "localhost",
                database = "Projeto",
                user = "postgres",
                password = "postgres",
                port  = 5432,
                )

            c1 = con.cursor()
            print("call addartigo('%s','%s')" % (nome, descricao))
            c1.execute("call addartigo('%s','%s')" % (nome, descricao)) 
            con.commit()
            c1.close()
            con.close()
            content = {"Sucesso" : "Artigo adicionado com sucesso"}
        return jsonify(content)


#OK
@app.route("/dbproj/logout", methods=['PUT'])
def logout():
    args = request.get_json()

    token = args.get("token")

    content = {}
    print(TOKENSDICT)
    if token not in TOKENSDICT:
        content.update({"Erro" :  "Token não é válido."})
    else:
        TOKENSDICT.pop(token)
        content.update({"Sucesso" : "Logout realizado com sucesso"})
    print(TOKENSDICT)
    return jsonify(content)
    


#CONFIRMAÇÕES
def confirmarCaracteresValidos(texto): #nomeArtigo , titulo leilao, descrião leilao
    for c in texto:
        if ( (c >= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z') or (c >= '0' and c <= '9') or c == '_' or c == '.' or c == '!' or c == '-' or c == ',' or c == '/'): #adicionar mais caracteres validos / acentos
            pass
        else:
            return False
    return True

def confirmarCaracteresValidosNome(texto): #nomeArtigo , titulo leilao, descrião leilao
    for c in texto:
        if ( (c >= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z') ): #adicionar mais caracteres validos / acentos
            pass
        else:
            return False
    return True

def confirmarCaracteresValidosUsername(texto):
    for c in texto:
        if ( (c >= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z') or (c >= '0' and c <= '9') or c == '_' or c == '.'):
            pass
        else:
            return False
    return True

def confirmarCaracteresValidosPassword(texto):
    for c in texto:
        if ( (c >= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z') or (c >= '0' and c <= '9') or c == '_' or c == '.'):
            pass
        else:
            return False
    return True

def confirmarCaracteresValidosMail(texto):
    for c in texto:
        if ( (c >= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z') or (c >= '0' and c <= '9') or c == '_' or c == '.' or c == '@'): #so um arroba
            pass
        else:
            return False
    return True

def confirmarData(data):
    for i in range (4):
        if data[i] >= '0' and data[i] <= '9':
            pass
        else:
            return False
    if data[4] != '-' or data[7] != '-':
        return False
    for i in range (5,7):
        if data[i] >= '0' and data[i] <= '9':
            pass
        else:
            return False
    for i in range (8,10):
        if data[i] >= '0' and data[i] <= '9':
            pass
        else:
            return False
    return True




##### NAO UTILIZADAS, APENAS PARA CONSULTA #######################################################
def login():
    
    while True:
        print("Insira o Username: ", end = '')
        username = input()
        if confirmarCaracteresValidosUsername(username):
            break
        else:
            print("Por favor coloque um username válido. (Só são aceites bla bla bla...") #corrigir print
    
    while True:
        print("Insira a Password: ", end = '')
        password = input()
        if confirmarCaracteresValidosPassword(password):
            break
        else:
            print("Por favor coloque um username válido. (Só são aceites bla bla bla...") #corrigir print

    con = psycopg2.connect(
            host = "localhost",
            database = "Projeto",
            user = "postgres",
            password = "postgres",
            port  = 5432,
            )

    c1 = con.cursor()
    c1.execute("select login(%s,%s)" % (username, password))

    resultado = c1.fetchall()
    resultado = resultado[0][0]

    c1.close()
    con.close()

    return resultado

def main():
    while True:
        try:
            print("O que deseja fazer?\n1) Login\n2) Criar novo utilizador\n0) Terminar programa")
            acao = int(input())
            if acao == 0:
                break
            elif acao == 1:
                id = login()
                if id == 0:
                    print("Username ou Password errado.")
                else:
                    print("Login executado com sucesso!")
                    menuUtilizador(id)
            else:
                print("Insira uma ação válida.")
        except:
            print("Por favor coloque apenas um número inteiro.")

#ok
def criarLeilao(id):
    while True:
        print("Qual o título que quer colocar no leilão?")
        titulo = input()
        if confirmarCaracteresValidos(titulo):
            break
        else:
            print("Por favor coloque um título válido. (Só são aceites bla bla bla...") #corrigir print

    while True:
        print("Qual a descrição que quer colocar no leilão?")
        descricao = input()
        if confirmarCaracteresValidos(descricao):
            break
        else:
            print("Por favor coloque uma descrição válida. (Só são aceites bla bla bla...") #corrigir print

    while True:
        try:
            print("Quantas horas quer que o seu leilão dure?")
            tempo = int(input())
            if tempo > 0:
                break
            else:
                print("Por favor coloque um valor inteiro positivo.")
        except:
            print("Por favor coloque apenas um número inteiro.")


    while True:
        try:
            print("Qual o valor minimo que quer que o seu leilão tenha?")
            minimo = int(input())
            if minimo > 0:
                break
            else:
                print("Por favor coloque um valor inteiro positivo.")
        except:
            print("Por favor coloque apenas um número inteiro.")


    con = psycopg2.connect(
            host = "localhost",
            database = "Projeto",
            user = "postgres",
            password = "postgres",
            port  = 5432,
            )

    c1 = con.cursor()
    c1.execute("select max(ean) from artigos")
    max = c1.fetchall()
    max = max[0][0]

    flag = True
    while flag:
        try:
            print("Que ação quer realizar?\n1) Colocar um ean dum artigo existente\n2) Adicionar um artigo à base de dados que será vendido no seu leilão\n 3) Ver os artigos já existentes na base de dados")         
            acao = int(input())
            if acao == 1:
                try:
                    print("Qual o código EAN do artigo que está a vender?")
                    ean = int(input())
                    if max == None or ean > max or ean <= 0:
                        print("Por favor coloque um ean existente.")
                    else:
                        break
                except:
                    print("Por favor coloque apenas um número inteiro.")
            elif acao == 2:
                ean = adicionarArtigo()
                flag = False
                break
            elif acao == 3:
                visualizarArtigos()
            else:
                print("Por favor coloque uma ação existente.")
        except:
            print("Por favor coloque apenas um número inteiro.")
        


    now = datetime.now()
    
    horas = now.hour
    dia = now.day
    mes = now.month
    ano = now.year

    while tempo >= 8784:
        if (((ano % 4 == 0 and ano % 100 != 0) or ano % 400 == 0) and mes <= 2 ) or ((((ano+1) % 4 == 0 and (ano+1) % 100 != 0) or (ano+1) % 400 == 0 ) and mes >= 3 ):
            ano += 1
            tempo -= 8784
        else:
            ano += 1
            tempo -= 8760
    while tempo >= 744:
        if mes == 1 or mes == 3 or mes == 5 or mes == 7 or mes == 8 or mes == 10 or mes == 12:
            tempo -= 744
        elif mes == 2:
            if ((ano % 4 == 0 and ano % 100 != 0) or ano % 400 == 0):
                tempo -= 694
            else:
                tempo -= 672
        else:
            tempo
        if mes == 12:
            mes = 1
            ano += 1
        else:
            mes += 1
    while tempo >= 24:
        tempo -= 24
        if dia == 31:
            dia = 1
            if mes == 12:
                mes = 1
                ano += 1
            else:
                mes += 1
        elif (dia == 30 and (mes == 4 or mes == 6 or mes == 9 or mes == 11)):
            dia = 1
            mes += 1
        elif ((dia == 29 and mes == 2) or (dia == 28 and mes == 2 and (ano % 4 != 0 or (ano % 100 == 0 and ano % 400 != 0)))):
            dia = 1
            mes += 1
        else:
            dia += 1
    horas += tempo

    c1.execute("CALL addleilao('%d-%d-%d %d:%d:%d', '%d-%d-%d %d:%d:%d',%d,%d,%d,%s,%s)" % (now.year, now.month, now.day, now.hour, now.minute, now.second, ano, mes, dia, horas, now.minute, now.second, minimo, id, ean, titulo, descricao))
    #c1.execute("insert into leiloes (time_criacao, time_termino,valor_atual, terminado, cancelado, vendido, titulo, descricao, users_id, artigos_ean) values ('%d-%d-%d %d:%d:%d', '%d-%d-%d %d:%d:%d', %d, 0, FALSE, FALSE, FALSE, %d, %d)" % (now.year, now.month, now.day, now.hour, now.minute, now.second, ano, mes, dia, horas, now.minute, now.second, minimo, 0, 0, id, ean))
    con.commit()
        
    #close the cursor
    c1.close()   
        
    #close the connection
    con.close()

#OK
def visualizarArtigos():
    con = psycopg2.connect(
            host = "localhost",
            database = "Projeto",
            user = "postgres",
            password = "postgres",
            port  = 5432,
            )

    c1 = con.cursor()
    c1.execute("select * from artigos")
    tabela = c1.fetchall()
    c1.close()
    con.close()
    print("|      EAN      |         Nome         | Descrição")
    for linha in tabela:
        print("| %13d | %20s | %s" % (linha[0], linha[1], linha[2]))

def adicionarArtigo():
    while True:
        print("Nome do Artigo: ")
        nome = input()
        if confirmarCaracteresValidos(nome):
            break
        else:
            print("Por favor coloque um nome válido. (Só são aceites bla bla bla...") #corrigir print

    while True:
        print("Descrição do Artigo: ")
        desc = input()
        if confirmarCaracteresValidos(desc):
            break
        else:
            print("Por favor coloque uma descrição válida. (Só são aceites bla bla bla...") #corrigir print

    con = psycopg2.connect(
            host = "localhost",
            database = "Projeto",
            user = "postgres",
            password = "postgres",
            port  = 5432,
            )

    c1 = con.cursor()
    c1.execute("insert into artigos (nome, descricao) values ('%s', '%s')" % (nome, desc))     ##FUNCAO SQL
    resultado = c1.fetchall()
    resultado = resultado[0][0]
    c1.close()   
    con.close()
    return resultado

def visualizarLeiloesAtivos():
    con = psycopg2.connect(
            host = "localhost",
            database = "Projeto",
            user = "postgres",
            password = "postgres",
            port  = 5432,
            )

    c1 = con.cursor()
    c1.execute("select id, titulos.texto, time_criacao, time_termino, valor_minimo, valor_atual, artigos.nome, users.username from leiloes, artigos, titulos, users where terminado = FALSE and leiloes.artigos_ean = artigos.ean leiloes.users_id = users.id and titulos.n = leiloes.titulo")
    tabela = c1.fetchall()
    c1.close()
    con.close()
    print()
    print("|   ID   |        Titulo        | Data e Hora Criação | Data e Hora de Término | Valor Mínimo |  Valor Atual  |    Artigo à venda    |      Criado por      |")
    for linha in tabela:
        print("| %6d | %20s | %19s | %22s | %12d | %13d | %20s |" % (linha[0], linha[1], linha[2], linha[3], linha[4], linha[5], linha[6], linha[7]))
    print()

def visualizarLeiloesTodos():
    con = psycopg2.connect(
            host = "localhost",
            database = "Projeto",
            user = "postgres",
            password = "postgres",
            port  = 5432,
            )

    c1 = con.cursor()
    c1.execute("select leiloes.id, titulos.texto, time_criacao, time_termino, valor_minimo, valor_atual, artigos.nome, users.username, leiloes.terminado from leiloes, artigos, titulos, users where leiloes.artigos_ean = artigos.ean leiloes.users_id = users.id and titulos.n = leiloes.titulo")
    tabela = c1.fetchall()
    c1.close()
    con.close()
    print()
    print("|   ID   |        Titulo        | Data e Hora Criação | Data e Hora de Término | Valor Mínimo |  Valor Atual  |    Artigo à venda    |      Criado por      | Terminado |")
    for linha in tabela:
        print("| %6d | %20s | %19s | %22s | %12d | %13d | %20s | %20s | %9s | " % (linha[0], linha[1], linha[2], linha[3], linha[4], linha[5], linha[6], linha[7], linha[8]))
    print()
    
def consultarDetalhesLeilão():
    con = psycopg2.connect(
            host = "localhost",
            database = "Projeto",
            user = "postgres",
            password = "postgres",
            port  = 5432,
            )

    c1 = con.cursor()
    c1.execute("select max(id) from leiloes")
    max = c1.fetchall()
    max = max[0][0]

    while True:
        try:
            print("Que leilão deseja consultar? Se pretender ver a lista de todos os leilões, escreva 0.")
            id = int(input())
            if id == 0:
                visualizarLeiloesTodos()
            elif id > max or id < 0:
                print("Por favor coloque um id de leilao válido.")
            else:
                break
        except:
            print("Por favor coloque apenas um número inteiro.")
        
    c1.execute("select leiloes.id, titulos.texto, descricao.texto, time_criacao, time_termino, valor_minimo, valor_atual, terminado, cancelado, vendido, users.username, artigos.nome, artigos.descricao from leiloes, artigos, users, titulos, descricao where leiloes.artigos_ean = artigos.ean and leiloes.users_id = users.id and leiloes.titulo = tirulo.n and leiloes.descricao=descricao.n")
    info = c1.fetchall()
    info = info[0]
    c1.close()
    con.close()
    print("ID: " + str(id))
    print("Título: " + str(info[1]))
    print("Descrição: " + str(info[2]))
    print("Data e Hora da criação do leilão: " + str(info[1]))
    print("Data e Hora do término do leilão: " + str(info[2]))
    print("Valor Mínimo: " + str(info[3]))
    print("Valor Actual: " + str(info[4]))
    print("Terminado: " + str(info[5]))
    print("Cancelado: " + str(info[6]))
    print("Vendido:   " + str(info[7]))
    print("Username criador: " + str(info[8]))
    print("Artigo: " + str(info[9]))
    print("Descrição Artigo: " + str(info[10]))

#OK
def login():
    
    while True:
        print("Insira o Username: ", end = '')
        username = input()
        if confirmarCaracteresValidosUsername(username):
            break
        else:
            print("Por favor coloque um username válido. (Só são aceites bla bla bla...") #corrigir print
    
    while True:
        print("Insira a Password: ", end = '')
        password = input()
        if confirmarCaracteresValidosPassword(password):
            break
        else:
            print("Por favor coloque um username válido. (Só são aceites bla bla bla...") #corrigir print

    con = psycopg2.connect(
            host = "localhost",
            database = "Projeto",
            user = "postgres",
            password = "postgres",
            port  = 5432,
            )

    c1 = con.cursor()
    c1.execute("select login(%s,%s)" % (username, password))

    resultado = c1.fetchall()
    resultado = resultado[0][0]

    c1.close()
    con.close()

    return resultado

def menuLeilao():
    while True:
        try:
            print("Sobre que leilão (id) quer realizar a sua ação?")
            idLeilao = int(input())
        except:
            print("Por favor coloque apenas um número inteiro.")


def visualizarLeiloesPersonalizado(id):
    while True:
        try:
            print("Que tipo de pesquisa sobre leilões quer fazer?\n1) Criados por si\n2) Licitados por si\n3) Comentados por si\n4) As 3 anteriores\n5) Numa gama de licitação mais alta atual\n6) Por título\n7) Por descrição\n8) Por EAN do artigo a ser licitado\n9) Por nome do artigo a ser licitado\n10) Por username do utilizador que criou o leilão")
            if acao == 1:
                break
            elif acao == 2:
                break
            elif acao == 3:
                break
            elif acao == 4:
                break
            elif acao == 5:
                break
            elif acao == 6:
                break
            elif acao == 7:
                break
            elif acao == 8:
                break
            elif acao == 9:
                break
            elif acao == 10:
                break
            else:
                print("Insira uma ação válida.")
        except:
            print("Por favor coloque apenas um número inteiro.")


    while True:
        try:
            print("Qual o id do leilão que deseja licitar? ")
            n = int(input())
            pass
        except:
            print("Por favor coloque apenas um número inteiro.")

def menuUtilizador(id):
    while True:
        #if NOTIFICAÇOES
        try:
            print("Que ação deseja realizar?\n1) Visualizar leilões\n2) Criar leilão\n3) Realizar ações num leilão\n0) Logout")
            acao = int(input())
            if acao == 0:
                break
            elif acao == 1:
                while True:
                    try:
                        print("Que leilões deseja visualizar?\n1) Todos\n2) Apenas ativos\n3) Pesquisa personalizada")
                        acao = int(input())
                        if acao == 1:
                            visualizarLeiloesTodos()
                            break
                        elif acao == 2:
                            visualizarLeiloesAtivos()
                            break
                        elif acao == 3:
                            visualizarLeiloesPersonalizado(id)
                            break
                        else:
                            print("Insira uma ação válida.")
                    except:
                        print("Por favor coloque apenas um número inteiro.")
            elif acao == 2:
                criarLeilao(id)
            elif acao == 3:
                menuLeilao(id)
            else:
                print("Insira uma ação válida.")              
        except:
            print("Por favor coloque apenas um número inteiro.")


if __name__ == '__main__':
    app.run(host="localhost", port=8080, debug=True, threaded=True)