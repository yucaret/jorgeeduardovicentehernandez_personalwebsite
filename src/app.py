import sett
import services
import time
#from io import BytesIO
from flask import Flask, request, render_template, send_from_directory

#app = Flask(__name__)
app = Flask(__name__, template_folder='public')

# Ruta para servir archivos CSS
@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory('public/css', filename)

# Ruta para servir archivos JS
@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory('public/js', filename)

# Ruta para servir imágenes
@app.route('/assets/img/<path:filename>')
def serve_image(filename):
    return send_from_directory('public/assets/img', filename)

@app.route('/')
def index():
    return render_template("index.html")

agente_langchain = None
conversacion = []
conversacion_webpage = []

@app.route('/chat', methods=['GET','POST'])
def  chat():
    global conversacion, conversacion_webpage, agente_langchain
    
    ip_usuario = request.remote_addr
    country_usuario = services.get_ubicacion_por_ip(ip_usuario)

    time.sleep(1)

    print(ip_usuario)
    print(country_usuario)

    if request.method == 'POST':
        #mensaje_usuario = request.form['mensaje']
        #conversacion.append({'role': 'user', 'content': mensaje_usuario})
        #respuesta_chatgpt = services.obtener_respuesta_gpt(mensaje_usuario, conversacion)  # Implementa tu lógica para obtener la respuesta de GPT
        #print("respuesta de chatgpt: " + respuesta_chatgpt)
        #conversacion.append({'role': 'assistant', 'content': respuesta_chatgpt})
        #conversacion_webpage.append({'usuario': mensaje_usuario, 'chatgpt': respuesta_chatgpt})

        if agente_langchain is None:
            agente_langchain = services.configurar_agente()
        
        mensaje_usuario = request.form['mensaje']

        try:
            result = agente_langchain({"input": mensaje_usuario})
            respuesta_chatgptlangchain = result['output']

            time.sleep(1)

            tipo_pregunta = services.get_tipo_pregunta_gpt(mensaje_usuario)

            # Obtén la fecha actual en formato YYYY-MM-DD
            fecha_actual = time.strftime("%Y-%m-%d")
            
            # Obtén la hora actual en formato 24HH:MI:SS
            hora_actual = time.strftime("%H:%M:%S")
            
            services.guardar_preguntas_usuarios(ip_usuario, country_usuario, mensaje_usuario, tipo_pregunta, fecha_actual, hora_actual)

        except Exception as e:
            print('Error: ' + str(e))
            respuesta_chatgptlangchain = sett.textolimitetoken
        
        print("respuesta de chatgpt langchain: " + respuesta_chatgptlangchain)
        conversacion.append({'role': 'assistant', 'content': respuesta_chatgptlangchain})
        conversacion_webpage.append({'usuario': mensaje_usuario, 'chatgpt': respuesta_chatgptlangchain})
    else:
        conversacion = []
        conversacion_webpage = []
        agente_langchain = None

    return render_template('chat.html', conversacion = conversacion_webpage)

@app.route('/plot')
def mostrar_grafico():
    services.procesar_imagen_barras_tipo_pregunta(sett.preguntas_usuario_archivo, sett.imagen_plot_tipo_pregunta)

    return render_template('plot.html')

if __name__ == '__main__':
    app.run()