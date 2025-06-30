def model_to_dict_feedback(feedbacks: list):
    """
    Convierte una lista de objetos Feedback del ORM en una lista de diccionarios simples,
    para que puedan ser usados fácilmente en análisis con pandas o serialización.
    """

    lista_dicts_feedback = []

    # Recorremos cada objeto de tipo Feedback
    for feedback in feedbacks:
        # Extraemos los campos relevantes en un diccionario
        feedback_dict = {
            "id": feedback.id,
            "autor": feedback.autor,
            "comentario": feedback.comentario,
            "fecha": feedback.fecha,
            "sentimiento": feedback.sentimiento,
            "etiquetas": feedback.etiquetas,
            "resumen": feedback.resumen,
        }

        # Lo añadimos a la lista final
        lista_dicts_feedback.append(feedback_dict)

    return lista_dicts_feedback


