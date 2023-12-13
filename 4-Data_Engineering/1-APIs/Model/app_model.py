from flask import Flask, request, jsonify
import os
import pickle
from sklearn.model_selection import cross_val_score
import pandas as pd
import sqlite3

os.chdir(os.path.dirname(__file__))

app = Flask(__name__)
app.config['DEBUG'] = True

@app.route("/", methods=['GET'])
def hello():
    return "Bienvenido a mi API del modelo advertising"

"""def crear_database():
      data_csv = pd.read_csv('ejercicio/data/Advertising.csv')
      data_csv.loc[0, 'newpaper'] = 69.2
      data_csv = data_csv.rename(columns={"newpaper":"newspaper"})
      data_csv = data_csv.drop(columns=["Unnamed: 0"])
      data_csv['newspaper'] = data_csv['newspaper'].astype('float64')
      conn = sqlite3.connect('ejercicio/data/Advertising.db')
      data_csv.to_sql('Advertising', conn, index=False, if_exists='replace')
      conn.close()"""


"""if not os.path.exists("ejercicio/data/Advertising.db"):
      crear_database()"""


# 1. Endpoint que devuelva la predicción de los nuevos datos enviados mediante argumentos en la llamada
@app.route('/v1/predict', methods=['GET'])
def predict():
    model = pickle.load(open('data/advertising_model','rb'))

    tv = request.args.get('tv', None)
    radio = request.args.get('radio', None)
    newspaper = request.args.get('newspaper', None)

    if tv is None or radio is None or newspaper is None:
        return "Missing args, the input values are needed to predict"
    else:
        prediction = model.predict([[int(tv),int(radio),int(newspaper)]])
        return "The prediction of sales investing that amount of money in TV, radio and newspaper is: " + str(round(prediction[0],2)) + 'k €'
    

# 2. Endpoint para almacenar nuevos registros en la base de datos
@app.route('/v2/ingest_data', methods=['POST'])
def ingest_data():
        data = request.get_json()

        conn = sqlite3.connect('data/Advertising.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Advertising (TV, radio, newspaper, sales) VALUES (?, ?, ?, ?)',
                       (data["TV"], data["radio"], data["newspaper"],data["sales"]))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Nuevos registros almacenados'})

# 3. Endpoint para reentrenar el modelo con los nuevos registros
@app.route('/v2/retrain', methods=['POST'])
def retrain_model():
    try:
        with open('data/advertising_model', 'rb') as archivo_modelo:
            model = pickle.load(archivo_modelo)

        conn = sqlite3.connect('data/Advertising.db')

        df = pd.read_sql_query("SELECT * FROM Advertising", conn)

        X_train = df[["TV", "radio", "newspaper"]]
        y_train = df["sales"]

        model.fit(X_train, y_train)

        with open('data/advertising_model', 'wb') as archivo_modelo:
            pickle.dump(model, archivo_modelo)

        conn.commit()
        conn.close()

        return jsonify({'message': 'Modelo entrenado correctamente'})

    except Exception as e:
        return jsonify({'error': str(e)})


# 4. Endpoint para obtener la predicción de ventas a partir de todos los valores de gastos en publicidad
@app.route('/v2/predict', methods=['GET'])

def predict_v2():
    # Conectar a la base de datos
    conn = sqlite3.connect('data/Advertising.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Advertising')
    advertising = cursor.fetchall()
    conn.close()

    model = pickle.load(open('data/advertising_model','rb'))

    TV = request.args.get('TV', None)
    radio = request.args.get('radio', None)
    newspaper = request.args.get('newspaper', None)

    if TV is None or radio is None or newspaper is None:
        return "Missing args, the input values are needed to predict"
    else:
        prediction = model.predict([[int(TV),int(radio),int(newspaper)]])
        return "The prediction of sales investing that amount of money in TV, radio and newspaper is: " + str(round(prediction[0],2)) + 'k €'

app.run(debug=True)