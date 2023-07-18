from flask import Flask, request, make_response
import json, time
from binance.client import Client
from binance.enums import *
# Configura tu API Key y Secret Key de Binance TOLVAS
#client = Client("JiiNHqwuxhhvUfayfHbAaFLkIUDlAMloAlPQHFMFIc7wk8QVskMgq2HdXKam0KZn","XGRMtw8rsyDSiBsB0AghvY7ewuCFgyybjR63Zv40k5HVpPX117FNCX80n2VqLsjv")

#MAMBRA

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './datos'

operacion ={}
def contar_claves_con_valor(diccionario, valor_buscado):
    count = 0
    for valor in diccionario.values():
        if valor == valor_buscado:
            count += 1
    return count
@app.route('/')
def home():
    while True:
        try:
            with open("datos.json", "r") as archivo:
                guardado = json.load(archivo)
            archivo.close()
            break
        except Exception:
            print("Estoy teniendo problema con el json")
    
    return jsonify(guardado)
        
@app.route('/trading-signal', methods=['POST'])
def receive_trading_signal():
    while True:
        try:
            with open("datos.json", "r") as archivo:
                guardado = json.load(archivo)
            archivo.close()
            break
        except Exception:
            print("Estoy teniendo problema con el json")
    time.sleep(2)
    senal = str(request.data, "UTF-8").lower()
    print(senal)
    moneda, indicador = senal.strip().split('|')

    try:
        guardado[0][moneda]
        indicador,posicion = indicador.strip().split(":")
        guardado[0][moneda][1][indicador]=posicion
    except Exception:
        client = Client("b1m4F6maj9cChCOUEo5gkcGnkgfC9gSjeivju245a51t71GZVYjza0eZHJEd8tsa","AbQ8BWY2WbQXkAJt63binouleSPZFKjQXcvKrBlbThArKq55O2vY1jhhjbTXvLbI")
        monedas = client.futures_exchange_info()
        for x in monedas["symbols"]:
            if x["symbol"] == moneda[:moneda.index("usdt")+4].upper():
                decimales = int(x["quantityPrecision"])
                break
        guardado[0][moneda]=[[decimales],{"posicion":"nulo","itgscalper":"0","heikin":"0","scalpin":"0","backtestin":"0","ce":"0"}]
        indicador,posicion = indicador.strip().split(":")
        guardado[0][moneda][1][indicador]=posicion

    print(indicador)
    print(posicion)
    cantidad_claves = contar_claves_con_valor(guardado[0][moneda][1], posicion)
    if cantidad_claves >= 3 and guardado[0][moneda][1]["posicion"] != posicion:
        client = Client("b1m4F6maj9cChCOUEo5gkcGnkgfC9gSjeivju245a51t71GZVYjza0eZHJEd8tsa","AbQ8BWY2WbQXkAJt63binouleSPZFKjQXcvKrBlbThArKq55O2vY1jhhjbTXvLbI")

        ticker = client.get_symbol_ticker(symbol=moneda[:moneda.index("usdt")+4].upper())
        cantidad = round(100 / float(ticker['price']),guardado[0][moneda][0][0])
        guardado[0][moneda][1]["posicion"]=posicion
        if posicion == "buy":
            order_long = client.futures_create_order(
                symbol=moneda[:moneda.index("usdt")+4].upper(),
                side='BUY',
                positionSide='LONG',
                type=ORDER_TYPE_MARKET,
                quantity=cantidad
            )
        else:
            
            client = Client("b1m4F6maj9cChCOUEo5gkcGnkgfC9gSjeivju245a51t71GZVYjza0eZHJEd8tsa","AbQ8BWY2WbQXkAJt63binouleSPZFKjQXcvKrBlbThArKq55O2vY1jhhjbTXvLbI")
            orders = client.futures_position_information(symbol=moneda[:moneda.index("usdt")+4].upper())
            print(orders)
            for orden in orders:
                if orden["notional"] != "0":
                    if orden["positionSide"] == "LONG":
                        order_long = client.futures_create_order(
                            symbol=moneda[:moneda.index("usdt")+4].upper(),
                            side='SELL',
                            positionSide='LONG',
                            type=ORDER_TYPE_MARKET,
                            quantity=round(float(orden["notional"])*-1,guardado[0][moneda][0][0])
                        )

    while True:
        
        try:
            with open("datos.json", "w") as archivo:
                json.dump(guardado, archivo)
            archivo.close()
            break
        except Exception:
            print("Estoy teniendo problema para guardar json")
    response = make_response('Solicitud procesada correctamente', 200)
    return response
