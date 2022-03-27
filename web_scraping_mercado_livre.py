# -*- coding: utf-8 -*-
"""
Created on Sun Mar 27 15:40:26 2022

@author: Usuario
"""

from selenium import webdriver
import pandas as pd
import re
import matplotlib.pyplot as plt
import seaborn as sns 
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(ChromeDriverManager().install())

url = "https://www.mercadolivre.com.br/ofertas?page="
df = pd.DataFrame()
produtos = []
preco = []
precoAntigoLista = []
descricaoProdutoLista = []

for i in range(0, 30):
    driver.get(url + str(i))
    driver.implicitly_wait(3)

    tituloProduto = driver.find_elements_by_class_name('promotion-item__title')
    precoAntigo = driver.find_elements_by_class_name('promotion-item__oldprice')
    precoProduto = driver.find_elements_by_xpath("//span[@class='promotion-item__price']//span")

    descricaoProduto = driver.find_elements_by_class_name('promotion-item__description')

    for x in tituloProduto:
        produtos.append(x.text)

    for x in precoProduto:
        preco.append(x.text)
        
    for x in precoAntigo:
        precoAntigoLista.append(x.text)
        
    for x in descricaoProduto:
         descricaoProdutoLista.append(x.text)
        
driver.close()

df['produto'] = produtos
df['preco'] = preco
df['preco_antigo'] = precoAntigoLista

df['preco'] = df['preco'].apply(lambda x: re.sub(r'R\$\s|\.', '', x))
df['preco'] = df['preco'].apply(lambda x: int(x))
df['preco_antigo'] = df['preco_antigo'].apply(lambda x: re.sub(r'R\$\s|\.', '', x))
df['preco_antigo'] = df['preco_antigo'].apply(lambda x: 0 if len(x) == 0 else x)
df['preco_antigo'] = df['preco_antigo'].apply(lambda x: int(x))

df2 = df.copy()
df2['descricao_produto'] = descricaoProdutoLista

df2['parcelas_sem_juros'] = df2['descricao_produto'].apply(lambda x: re.sub(r'(?!\d+(?=x)).*', '', x))
df2['parcelas_sem_juros'] = df2['parcelas_sem_juros'].apply(lambda x: re.sub(r'\s+', '', x))
df2['parcelas_sem_juros'] = df2['parcelas_sem_juros'].apply(lambda x: 0 if len(x) == 0 else x).apply(lambda x: int(x))
df2['frete_gratis'] = df2['descricao_produto'].apply(lambda x: re.sub(r'(^(?!.*(Frete\sgrátis)).*)', '', x))

df2['frete_gratis'] = df2['descricao_produto'].apply(lambda x: re.sub(r'((?!.*(Frete\sgrátis)).*)', '', x))
df2['frete_gratis'] = df2['frete_gratis'].apply(lambda x: re.sub(r'\s+', '', x))
df2['frete_gratis'] = df2['frete_gratis'].apply(lambda x: 'SIM' if x == 'F' else 'NÃO')

df2 = df2.loc[df['preco_antigo'] != 0]

df2['diferenca'] = df2['preco_antigo'] - df2['preco']
df2 = df2.loc[df2['diferenca'] != 0]

df2['desconto_porcento'] = round((df2['diferenca'] * 100 ) / df['preco_antigo'], 2)

df2['media_desconto'] = round(df2['diferenca'].mean(), 2)

df2['mediana'] = round(df2['diferenca'], 2).median()

df_parcelado = df2.loc[df2['parcelas_sem_juros'] > 0].round(2)

df_parcelado['valor_parcela'] = df_parcelado['preco'] / df_parcelado['parcelas_sem_juros'].round(2)
df_parcelado['valor_parcela'] = df_parcelado['valor_parcela'].round(2)


df2.to_excel('exemplo_ofertas_mercado_livre_27_marco_2022.xlsx')
df2.to_csv('exemplo_ofertas_mercado_livre_27_marco_2022.csv')


js = df2.to_json(orient = 'columns')

df2.to_json('estoque_mercado_livre.json', orient = 'table')












