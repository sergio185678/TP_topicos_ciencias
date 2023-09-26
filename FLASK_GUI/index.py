from flask import Flask,render_template, request, jsonify
from ortools.sat.python import cp_model

app=Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mi_ruta', methods=['POST'])
def recibir_datos_desde_js():
    datos = request.get_json()
    array_total = datos.get('array', [])  # Obtener el arreglo de números desde los datos recibidos
    
    resultado=emparejamiento(array_total)
    
    return jsonify(resultado)

if __name__ == '__main__':
    app.run(debug=True)

def emparejamiento(array_total=[]):

    nombres_hombres=array_total[0]
    nombres_mujeres=array_total[1]
    array_hombre_a_mujer=array_total[2]
    array_mujer_a_hombre=array_total[3]
    n=6

    model = cp_model.CpModel()

    #creación de las variables y dominios de hombres a mujeres
    grilla_hombres = []
    for i in range(n):
      fila = []
      for j in range(n):
        fila += [model.NewIntVar(0,1,'H'+str(i)+'_M'+str(j))]
      grilla_hombres+=[fila]

    #creación de las variables y dominios de mujeres a hombres
    grilla_mujeres = []
    for i in range(n):
      fila = []
      for j in range(n):
        fila += [model.NewIntVar(0,1,'M'+str(i)+'_H'+str(j))]
      grilla_mujeres+=[fila]

    #se unen las 2 grillas
    grilla_total=[grilla_hombres]+[grilla_mujeres]

    #restricciones
    # 1 elige, 0 no elige
    for i in range(n):
      #la fila solo puede sumar 1, ya que solo una persona puede elegir a una persona
      model.Add(sum(grilla_total[0][i])==1)
      model.Add(sum(grilla_total[1][i])==1)
      for j in range(n):
        #solo pueden elegir a personas con minimo de 4 orden de preferencia
        if(array_hombre_a_mujer[i][j]>4):
          model.Add(grilla_total[0][i][j]==0)
        if(array_mujer_a_hombre[i][j]>4):
          model.Add(grilla_total[1][i][j]==0)

    for j in range(n):
      #tambien la columna solo pueden ser elegido por una persona
      c1 = [grilla_total[0][i][j] for i in range(n)]
      c2 = [grilla_total[1][i][j] for i in range(n)]
      model.Add(sum(c1)==1)
      model.Add(sum(c2)==1)

    #las sumas de los valores de las transpuestas entre las 2 tablas no pueden sumar 1
    for i in range(n):
      for j in range(n):
        model.Add(grilla_total[0][i][j]+grilla_total[1][j][i]!=1)

    #solucionando el modelo
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10.0
    status = solver.Solve(model)

    stringggg=""
    for i in range(n):
        for j in range(n):
          if(solver.Value(grilla_total[0][i][j])==1):
            stringggg+="'"+str(nombres_hombres[i])+"' se casa con '"+str(nombres_mujeres[j])+"' , "
            print("'"+str(nombres_hombres[i])+"' se casa con '"+str(nombres_mujeres[j])+"'")

    return stringggg