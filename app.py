from flask import Flask, request, make_response
import json, time
from binance.client import Client
from binance.enums import *
import sqlite3

app = Flask(__name__)

        
with open("datos.json", "r") as archivo:
    guardado = json.load(archivo)
archivo.close()
def contar_claves_con_valor(diccionario, valor_buscado):
    count = 0
    brinco = 0
    for valor in diccionario.values():
        if brinco >0:
            if valor == valor_buscado:
                count += 1
        else:
            brinco +=1
    return count

@app.route('/trading-signal', methods=['POST'])
def receive_trading_signal():
    conn = sqlite3.connect('DBindicadores.db')
    cursor = conn.cursor()
    conn.execute('''CREATE TABLE IF NOT EXISTS DBindicadores
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         moneda TEXT,
                         indicador TEXT,
                         senal TEXT)''')
    senal = str(request.data, "UTF-8").lower()
    print(senal)
    moneda, indicador = senal.strip().split('|')
    indicador,posicion = indicador.strip().split(":")
    
    try:
        guardado[0][moneda]
    except Exception:
        client = Client("b1m4F6maj9cChCOUEo5gkcGnkgfC9gSjeivju245a51t71GZVYjza0eZHJEd8tsa","AbQ8BWY2WbQXkAJt63binouleSPZFKjQXcvKrBlbThArKq55O2vY1jhhjbTXvLbI")
        monedas = client.futures_exchange_info()
        for x in monedas["symbols"]:
            if x["symbol"] == moneda[:moneda.index("usdt")+4].upper():
                decimales = int(x["quantityPrecision"])
                break
        guardado[0][moneda]=[[decimales],{"posicion":"nulo","trend":"0","itgscalper":"0","heikin":"0","scalpin":"0","backtestin":"0","ce":"0"}]
        
        
    
    conn.execute("INSERT INTO DBindicadores (moneda, indicador, senal) VALUES (?, ?, ?)", (moneda, indicador, posicion))
    
    
    ddb = cursor.execute("SELECT * FROM DBindicadores")
    for row in ddb:
        print(row)
        guardado[0][row[1]][1][row[2]]=row[3]
        with open("datos.json", "w") as archivo:
            json.dump(guardado, archivo)
        archivo.close()
        conn.execute("DELETE FROM DBindicadores WHERE id=?",(row[0],))
        conn.commit()
    #conn.execute('DROP TABLE DBindicadores')
    conn.close()
    print(posicion)
    print(guardado[0][moneda][1])
    cantidad_claves = contar_claves_con_valor(guardado[0][moneda][1], posicion)
    print(cantidad_claves)
    if cantidad_claves >= 3 and guardado[0][moneda][1]["posicion"] != posicion:
        
        print("OPERAR")
        client = Client("b1m4F6maj9cChCOUEo5gkcGnkgfC9gSjeivju245a51t71GZVYjza0eZHJEd8tsa","AbQ8BWY2WbQXkAJt63binouleSPZFKjQXcvKrBlbThArKq55O2vY1jhhjbTXvLbI")
    
        while True:
            try:
                orders = client.futures_position_information(symbol=moneda[:moneda.index("usdt")+4].upper())
                break
            except Exception:
                time.sleep(2)
        
        
        cantidad = round(100 / float(orders[0]["markPrice"]),guardado[0][moneda][0][0])
        
        if posicion == "buy":
            posicion="nulo"
            precioC = float(orders[1]["entryPrice"])-(float(orders[1]["entryPrice"])*0.01)
            print("Precio para comprar: "+str(precioC))
            if abs(float(orders[2]["positionAmt"])) != 0 and float(orders[2]["unRealizedProfit"]) >= 0:
                print("CERRAREMOS VENTA")  
                close_short = client.futures_create_order(
                      symbol=moneda[:moneda.index("usdt")+4].upper(),
                      side='BUY',
                      positionSide='SHORT',
                      type=ORDER_TYPE_MARKET,
                      quantity=abs(float(orders[2]["positionAmt"]))
                  )
            if  precioC >= float(orders[1]["markPrice"]) or precioC == 0.0:
                posicion="buy"
                order_long = client.futures_create_order(
                    symbol=moneda[:moneda.index("usdt")+4].upper(),
                    side='BUY',
                    positionSide='LONG',
                    type=ORDER_TYPE_MARKET,
                    quantity=cantidad
                )

        elif posicion == "sell":
            posicion="nulo"
            precioV = float(orders[2]["entryPrice"])+(float(orders[2]["entryPrice"])*0.01)
            print("Precio para vender: "+str(precioV))
            if abs(float(orders[1]["positionAmt"])) != 0 and float(orders[1]["unRealizedProfit"]) >= 0:
                print("CERRAREMOS COMPRA") 
                close_long = client.futures_create_order(
                    symbol=moneda[:moneda.index("usdt")+4].upper(),
                    side='SELL',
                    positionSide='LONG',
                    type=ORDER_TYPE_MARKET,
                    quantity=abs(float(orders[1]["positionAmt"]))
                )
            if  precioV <= float(orders[2]["markPrice"]) or precioV == 0.0:
                posicion="sell"
                order_short = client.futures_create_order(
                    symbol=moneda[:moneda.index("usdt")+4].upper(),
                    side='SELL',
                    positionSide='SHORT',
                    type=ORDER_TYPE_MARKET,
                    quantity=cantidad
                )
        
        guardado[0][moneda][1]={"posicion":posicion,"trend":"0","itgscalper":"0","heikin":"0","scalpin":"0","backtestin":"0","ce":"0"}
        with open("datos.json", "w") as archivo:
            json.dump(guardado, archivo)
        archivo.close()

            
            
                
            
    
        
    
    response = make_response('Solicitud procesada correctamente', 200)
    return response


