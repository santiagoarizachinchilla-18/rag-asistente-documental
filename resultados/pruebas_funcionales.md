# Pruebas funcionales del RAG - Corpus NovaTech

## Objetivo y entorno de prueba

Evaluar tres comportamientos obligatorios del asistente documental: **respuesta completa**, **respuesta parcial** y **abstención**. Se registran a continuación las salidas reales compartidas por el ejecutor, sin sustituirlas por respuestas esperadas ni resultados simulados.

- **Aplicación:** API local FastAPI, `POST /ask` desde Swagger.
- **Corpus indexado:** 3 documentos: `politica_vacaciones.md`, `politica_trabajo_remoto.md` y `politica_gastos_viajes.pdf`.
- **Índice persistente:** ChromaDB; `POST /index` devolvió `{"documents": 3, "chunks": 19}` tras sustituir el chunker.
- **Parámetro de las tres consultas de esta evaluación:** `top_k=3` especificado en cada solicitud. Este valor probado **no implica** que se haya cambiado el valor predeterminado de la API.
- **Pruebas automatizadas:** 28 aprobadas, según la ejecución informada por el usuario antes de esta evaluación.
- **Fecha de las pruebas:** 25 de octubre de 2026.
- **Alcance:** evaluación manual de tres consultas; no constituye una medición estadística de precisión, exhaustividad o fiabilidad general.

## Resumen de resultados

| Escenario | Resultado manual | Evidencia principal |
|---|---|---|
| Respuesta completa | Aprobada | Plazo de cinco días hábiles y aprobación administrativa, respaldados por el PDF. |
| Respuesta parcial | Aprobada con observaciones | Distingue reglas de seguridad documentadas de permiso internacional no definido; cobertura de seguridad no exhaustiva. |
| Abstención | Aprobada | No inventa salario y no atribuye fuentes. |

## Caso 1 - Respuesta completa

**Pregunta literal:** ¿En qué plazo deben presentarse los comprobantes de gastos de viaje y quién aprueba el reembolso?

**Solicitud:** `POST /ask`, `top_k=3`.

**Respuesta real de la API (JSON completo):**

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

**Evaluación manual:** **Correcta.** Indica los cinco días hábiles posteriores al viaje y la aprobación del responsable administrativo. Las referencias [1], [2] y [3] son pertinentes y sustentan ambas afirmaciones.

## Caso 2 - Respuesta parcial

**Pregunta literal:** ¿Puedo trabajar desde otro país durante tres meses y qué medidas de seguridad debo cumplir?

**Solicitud:** `POST /ask`, `top_k=3`.

**Respuesta real de la API (JSON completo):**

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

**Evaluación manual:** **Correcta con observaciones.** Distingue la falta de una autorización específica para estancias internacionales prolongadas de las medidas de seguridad sí documentadas. El contexto citado respalda equipos corporativos, VPN, credenciales y soporte. La respuesta omite otras medidas establecidas en la política (bloquear la sesión ante un equipo desatendido e informar pérdida o posibles accesos no autorizados); además, la palabra "únicamente" refuerza una exclusividad no expresada literalmente en el fragmento, que exige usar VPN sin usar esa palabra. Estas observaciones no invalidan el comportamiento de respuesta parcial, pero impiden calificarla como exhaustiva.

## Caso 3 - Abstención

**Pregunta literal:** ¿Cuál es el salario promedio de los empleados de NovaTech?

**Solicitud:** `POST /ask`, `top_k=3`.

**Respuesta real de la API (JSON completo):**

```json
{
  "question": "¿Cuál es el salario promedio de los empleados de NovaTech?",
  "answer": "No encuentro información suficiente en los documentos para responder.",
  "sources": []
}
```

**Evaluación manual:** **Correcta.** El corpus no incluye cifras salariales. El asistente no inventa datos y devuelve `sources: []`.

## Hallazgos y cambios durante P6

1. **Indexación del corpus:** tres documentos procesados correctamente. Antes de ajustar la fragmentación, el índice tenía 16 chunks; después de reindexar con el chunker corregido, quedó con 19.
2. **Respuesta parcial inicial:** con el prompt anterior se produjo una abstención total aunque se habían recuperado fragmentos pertinentes de trabajo remoto. El prompt se ajustó para exigir contestar por separado las partes respaldadas y reconocer expresamente los vacíos de información.
3. **Ruido con `top_k=4`:** en una prueba intermedia se recuperó un fragmento de gastos y viajes y el modelo añadió condiciones de reembolso irrelevantes para una pregunta de trabajo remoto internacional. Una prueba posterior con `top_k=3` eliminó ese apartado improcedente.
4. **Fragmentación:** se observaron cortes a mitad de oración y palabras aparentemente unidas en el índice anterior. Se sustituyó `app/chunker.py`, conservando tamaño de chunk 400 y solapamiento 60. La reindexación posterior produjo 19 fragmentos. Los extractos de estas pruebas finales no exhiben las palabras pegadas previamente observadas, pero la inspección de todos los fragmentos finales no forma parte de este registro.
5. **Referencias:** los números devueltos corresponden a fragmentos reales. Esta comprobación manual evalúa además si los extractos sustentan las respuestas; una referencia válida por formato no garantiza pertinencia semántica.

## Limitaciones observadas

- El caso de respuesta parcial no enumera todas las medidas de seguridad establecidas en la política: falta mencionar el bloqueo de sesión y el reporte de incidentes. Asimismo, el término "únicamente" introduce un matiz más fuerte que el texto citado sobre VPN.
- `top_k=3` funcionó para estas tres preguntas, pero no se ha demostrado que sea óptimo para todas las consultas ni se ha cambiado necesariamente el valor predeterminado del servicio.
- Con un corpus pequeño y tres casos funcionales, esta evaluación muestra comportamientos concretos, no una garantía de desempeño general.
- La colección se reconstruye al reindexar; no se realizaron consultas concurrentes durante ese proceso.

## Conclusión

Los tres escenarios requeridos fueron demostrados con salidas reales: respuesta documentada con citas, respuesta parcial con reconocimiento de información no definida y abstención ante ausencia de evidencia. **P6 puede darse por validada a nivel funcional, con observaciones documentadas en la respuesta parcial.** La siguiente etapa es completar el README y la evidencia de ejecución para la entrega.
