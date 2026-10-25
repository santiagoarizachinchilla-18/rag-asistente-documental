# Evaluación funcional del asistente documental RAG — NovaTech

## Objetivo y entorno de evaluación

Se evaluó el comportamiento del asistente documental en tres escenarios: **respuesta completa**, **respuesta parcial** y **abstención por falta de información**. Se conservaron las respuestas JSON obtenidas mediante ejecuciones reales de la API, junto con sus fuentes y una revisión manual de la pertinencia de las afirmaciones.

- **Aplicación:** API local desarrollada con FastAPI; las consultas se ejecutaron mediante `POST /ask` desde Swagger UI.
- **Corpus indexado:** tres documentos ficticios de NovaTech: `politica_vacaciones.md`, `politica_trabajo_remoto.md` y `politica_gastos_viajes.pdf`.
- **Índice vectorial:** ChromaDB con persistencia local. Después del ajuste de fragmentación, `POST /index` devolvió `{"documents": 3, "chunks": 19}`.
- **Configuración de las consultas:** `top_k=3` se estableció explícitamente en los tres casos. El valor predeterminado de la API permanece en `top_k=4`.
- **Pruebas automatizadas:** se registraron 28 pruebas aprobadas con `pytest` antes de esta evaluación funcional.
- **Fecha de las pruebas:** 25 de octubre de 2026.
- **Alcance:** revisión manual de tres consultas concretas. Los resultados no representan una estimación estadística de precisión, exhaustividad o fiabilidad general.

## Resumen de resultados

| Escenario | Evaluación manual | Evidencia principal |
|---|---|---|
| Respuesta completa | Aprobada | Plazo de cinco días hábiles y aprobación administrativa, respaldados por el PDF. |
| Respuesta parcial | Aprobada con observaciones | Diferencia las medidas de seguridad documentadas de una autorización internacional no especificada; la enumeración de medidas no es exhaustiva. |
| Abstención | Aprobada | No se generaron cifras salariales sin respaldo y la lista de fuentes quedó vacía. |

## Caso 1. Respuesta completa

**Pregunta evaluada:** ¿En qué plazo deben presentarse los comprobantes de gastos de viaje y quién aprueba el reembolso?

**Solicitud:** `POST /ask`, `top_k=3`.

**Respuesta obtenida de la API (JSON íntegro):**

```json
{
  "question": "¿En qué plazo deben presentarse los comprobantes de gastos de viaje y quién aprueba el reembolso?",
  "answer": "Los comprobantes de gastos de viaje deben presentarse **dentro de los cinco días hábiles siguientes a la finalización del viaje** [1][2].  \nEl reembolso es **aprobado por el responsable administrativo** [1][3].",
  "sources": [
    {
      "reference": 1,
      "source": "politica_gastos_viajes.pdf",
      "chunk_id": "politica_gastos_viajes_004",
      "excerpt": "Solicitud de reembolso Los empleados deben presentar los comprobantes de pago dentro de los cinco días hábiles siguientes a la finalización del viaje. La solicitud debe identificar el motivo laboral, las fechas del viaje y los gastos reclamados, y debe adjuntar los comprobantes correspondientes. Revisión y aprobación Los reembolsos deben ser aprobados por el responsable administrativo.",
      "distance": 0.19922125339508057
    },
    {
      "reference": 2,
      "source": "politica_gastos_viajes.pdf",
      "chunk_id": "politica_gastos_viajes_003",
      "excerpt": "La autorización del viaje no equivale a una aprobación automática de cualquier importe declarado posteriormente. Solicitud de reembolso Los empleados deben presentar los comprobantes de pago dentro de los cinco días hábiles siguientes a la finalización del viaje.",
      "distance": 0.23897099494934082
    },
    {
      "reference": 3,
      "source": "politica_gastos_viajes.pdf",
      "chunk_id": "politica_gastos_viajes_005",
      "excerpt": "Revisión y aprobación Los reembolsos deben ser aprobados por el responsable administrativo. El responsable puede pedir aclaraciones si un comprobante es ilegible o no permite relacionar el gasto con el viaje autorizado. La entrega de los documentos no garantiza por sí sola la aprobación del reembolso.",
      "distance": 0.322512686252594
    }
  ]
}
```

**Evaluación manual: aprobada.** Se identificaron correctamente el plazo de cinco días hábiles posteriores a la finalización del viaje y la aprobación del responsable administrativo. Los fragmentos citados mediante [1], [2] y [3] contienen evidencia directa de ambas condiciones.

## Caso 2. Respuesta parcial

**Pregunta evaluada:** ¿Puedo trabajar desde otro país durante tres meses y qué medidas de seguridad debo cumplir?

**Solicitud:** `POST /ask`, `top_k=3`.

**Respuesta obtenida de la API (JSON íntegro):**

```json
{
  "question": "¿Puedo trabajar desde otro país durante tres meses y qué medidas de seguridad debo cumplir?",
  "answer": "**Respuesta:**\n\n1. **Trabajar desde otro país durante tres meses**  \n   La política de trabajo remoto no establece un procedimiento de autorización ni condiciones específicas para estancias de trabajo en el extranjero que duren varios meses. Por lo tanto, no se puede determinar a partir de los documentos si esa situación está permitida o qué requisitos adicionales podrían aplicarse.  \n   *Referencia: [1]*  \n\n2. **Medidas de seguridad que debes cumplir**  \n   - Utilizar los equipos corporativos asignados.  \n   - Conectarse a los sistemas internos únicamente mediante la VPN de la empresa.  \n   - No compartir credenciales corporativas con otras personas.  \n   - En caso de problemas de acceso a la VPN o al equipo corporativo, contactar al equipo de soporte.  \n   *Referencias: [3], [1]*",
  "sources": [
    {
      "reference": 1,
      "source": "politica_trabajo_remoto.md",
      "chunk_id": "politica_trabajo_remoto_006",
      "excerpt": "## Soporte y aclaraciones Ante problemas de acceso a la VPN o al equipo corporativo, el empleado debe contactar al equipo de soporte. Esta política no fija un procedimiento de autorización ni condiciones específicas para estancias de trabajo en el extranjero durante varios meses; esas condiciones no pueden deducirse de la regla habitual de dos días por semana.",
      "distance": 0.4814150333404541
    },
    {
      "reference": 3,
      "source": "politica_trabajo_remoto.md",
      "chunk_id": "politica_trabajo_remoto_002",
      "excerpt": "La modalidad habitual no reemplaza las responsabilidades y horarios asignados al empleado. ## Condiciones de seguridad Durante el trabajo remoto, los empleados deben utilizar los equipos corporativos asignados y conectarse a los sistemas internos mediante la VPN de la empresa. No está permitido compartir credenciales corporativas con otras personas.",
      "distance": 0.5645385384559631
    }
  ]
}
```

**Evaluación manual: aprobada con observaciones.** Se distinguió correctamente entre la ausencia de reglas específicas para estancias prolongadas en el extranjero y las medidas de seguridad documentadas. Las referencias respaldan el uso de equipos corporativos, VPN, la prohibición de compartir credenciales y el contacto con soporte ante problemas de acceso. No obstante, la respuesta omitió el bloqueo de sesión cuando el equipo queda desatendido y la notificación de pérdidas o posibles accesos no autorizados. Asimismo, el término «únicamente», aplicado a la VPN, introduce un énfasis más restrictivo que el expresado literalmente en el documento. Se considera demostrada la capacidad de respuesta parcial, pero no la cobertura exhaustiva de las medidas de seguridad.

## Caso 3. Abstención

**Pregunta evaluada:** ¿Cuál es el salario promedio de los empleados de NovaTech?

**Solicitud:** `POST /ask`, `top_k=3`.

**Respuesta obtenida de la API (JSON íntegro):**

```json
{
  "question": "¿Cuál es el salario promedio de los empleados de NovaTech?",
  "answer": "No encuentro información suficiente en los documentos para responder.",
  "sources": []
}
```

**Evaluación manual: aprobada.** Los documentos del corpus no proporcionan cifras de salarios. Se obtuvo la abstención prevista y `sources: []`, sin incorporar información salarial ajena a las fuentes.

## Hallazgos y ajustes de la implementación

1. **Indexación:** se procesaron tres documentos. La configuración anterior produjo 16 fragmentos; tras ajustar el algoritmo y reconstruir el índice, se registraron 19.
2. **Tratamiento de preguntas con varias partes:** inicialmente se obtuvo una abstención total pese a existir contexto pertinente sobre trabajo remoto. Se precisaron las instrucciones de generación para responder las partes respaldadas e identificar por separado los datos no especificados.
3. **Pertinencia del contexto:** con `top_k=4` se recuperó también un fragmento de gastos y viajes, lo que dio lugar a una sección de reembolsos ajena a la consulta sobre trabajo remoto. En una prueba posterior con `top_k=3`, esa información irrelevante dejó de aparecer.
4. **Integridad de los fragmentos:** en el índice anterior se detectaron oraciones truncadas y algunas palabras aparentemente unidas. Se ajustó `app/chunker.py` para favorecer límites de oración, manteniendo un tamaño máximo de 400 caracteres y un solapamiento de 60. Tras reindexar se obtuvieron 19 fragmentos. En los extractos citados de la evaluación final no se observaron las uniones de palabras detectadas anteriormente; no se realizó una auditoría exhaustiva de todos los fragmentos del índice.
5. **Trazabilidad:** las referencias numéricas corresponden a fragmentos recuperados e identificables. Se revisó también la relación entre los extractos citados y las afirmaciones generadas. La validez numérica de una cita, por sí sola, no garantiza que su contenido respalde semánticamente la respuesta.

## Limitaciones y alcance de los resultados

- **Cobertura parcial:** no se mencionaron todas las medidas de seguridad de la política; quedaron fuera el bloqueo de sesión y el reporte de incidentes. La expresión «únicamente mediante la VPN» es más restrictiva que la formulación literal de la fuente.
- **Número de fragmentos recuperados:** `top_k=3` produjo respuestas adecuadas en estas tres consultas, pero no se ha establecido como configuración óptima. La API conserva `top_k=4` como valor predeterminado.
- **Representatividad:** el corpus y la cantidad de preguntas son reducidos. Los resultados describen los casos observados y no permiten generalizar el desempeño a otros documentos o consultas.
- **Reindexación:** la colección se reemplaza al volver a indexar; no se evaluó su comportamiento ante consultas simultáneas o fallos durante la reconstrucción.

## Conclusión

Se comprobaron los tres escenarios definidos para la evaluación: una respuesta sustentada en fragmentos identificables, una respuesta parcial que reconoce información no especificada y una abstención sin fuentes ante una pregunta fuera del corpus. **La validación funcional de estos casos se completó, con limitaciones documentadas en la respuesta parcial.**