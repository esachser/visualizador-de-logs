# Visualizador de logs.
Repositório dos fontes do visualizador de logs desenvolvido inicialmente para o Aeromóvel, mas que suporta a carga de arquivos CSV com valores.

## Bibliotecas necessárias:
Este programa foi feito para python3, e necessita as seguintes bibliotecas instaladas:
  + PyQt5
  + pyqtgraph
  + rx
  + pandas
  + numpy
  
## Rodando o programa
Para rodar o programa, basta digitar no terminal:
```bash
python3 view/Visualizador.py
```  

## Uso do programa
O programa é muito simples de ser utilizado. Basta que seja executado, escolher os arquivos
que se deseja analisar, *csv's*, e carregá-los.

É possível utilizar qualquer variável real ou de tempo como x e y, adicionar novas tabs,
gráficos com o eixo x compartilhado, etc...

Todas essas configurações podem ficar gravadas ao final do uso, bem como podem ser salvas
em um arquivo, para uso posterior.

É possível fazer a carga de qualquer arquivo *csv*, podendo ser utilizado como visualizador de dados gráficos.

Entre suas funcionalidades está a escolha das cores dos gráficos, além da escolha
de tipos de gráfico:
 + Linhas
 + Pontos
 + Pontos + Linhas

Outra funcionalidade interessante é a possibilidade de filtrar dados conforme
*querys*, tanto para o eixo x quanto para cada gráfico individualmente. Por 
exemplo, se desejarmos todos os pontos que tenham velocidade maior que 10km/h,
e menor que 30km/h, escrevemos uma *query* na seguinte forma:
```
10 < Velocidade < 30
```
Caso a velocidade esteja m/s, podemos escrever assim:
```
10 < Velocidade * 3.6 < 30
```