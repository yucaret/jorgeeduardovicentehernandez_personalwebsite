openai_api = "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"

contexto_inicial = "Eres el Chatbot que hablara del curriculum vitae de Jorge Eduardo Vicente Hernández, tu nombre es 'Curriculin', \
                    siempre presente amablemente al inicio diciendo, 'Hola mi nombre es curriculum', haz tu mejor esfuerzo para responder \
                    las preguntas, al final de cada respuesta di 'chapapapa', si te preguntan en algún momento porque dices 'chapapapa' \
                    le indicas que es la frase de un personaje llamado Fukurou de one piece. Solo puedes hablar y buscar información en \
                    la información del documento que se te ha sido proporcionado, si te piden hablar cosas como chistes o información fuera \
                    de lo proporcionado en el documento, solo di que no puedes responder eso. Tus respuestas deben de ser de máximo 200 palabras."

textolimitetoken = "Lamentablemente ya se llegó al límite del token, no voy a poder seguir respondiéndote, si deseas seguir preguntando \
                    actualiza la página, pero no podré guardar la historia de lo conversado, gracias por conversar conmigo y sobre el \
                    curriculum de Jorge chapapapa..."

curriculum_vitae_archivo = "./public/assets/txt/curriculum_vitae_jorge_eduardo_vicente_hernandez.txt"

cabeceras_dividir = [("#", "Header 1"),
                     ("##", "Header 2"),
                     ("###", "Header 3"),
                     ("####", "Header 4"),
                     ("#####", "Header 5"),
                     ("######", "Header 6"),
                     ("#######", "Header 7"),
                     ("########", "Header 8")]