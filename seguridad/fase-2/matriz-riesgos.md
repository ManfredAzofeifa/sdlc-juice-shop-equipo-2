# Matriz de riesgos

Una fila por riesgo. La columna «Caso de abuso» cita los issues con #n. El checkpoint lee solo esta tabla: no agregue otras tablas a este archivo.

| ID | Amenaza | STRIDE | Caso de abuso | Probabilidad | Impacto | Riesgo | Tratamiento |
|:---|:---|:---|:---|:---|:---|:---|:---|
| R-01 | Cambio de contraseña sin validación actual | S | #3 | 2 | 3 | 6 | Corregir |
| R-02 | Acceso a archivos sensibles sin auditoría | R | #4 | 3 | 2 | 6 | Mitigar |
| R-03 | Acceso no autorizado a canastas ajenas | E | #5 | 3 | 2 | 6 | Corregir |
| R-04 | Uso de privilegios revocados con JWT antiguo | E | #6 | 2 | 3 | 6 | Corregir |
| R-05 | Exposición de hashes MD5 de contraseñas | I | #7 | 3 | 3 | 9 | Corregir |
| R-06 | Falsificación de autoría mediante UserId | T | #12 | 3 | 2 | 6 | Corregir |

## Escala

Probabilidad (P):

- **1, baja.** Requiere acceso privilegiado, conocimiento interno o una cadena de varios pasos.
- **2, media.** Un usuario registrado lo logra con herramientas comunes.
- **3, alta.** Cualquier visitante anónimo lo logra desde el navegador.

Impacto (I):

- **1, bajo.** Afecta a un usuario y se revierte sin pérdida.
- **2, medio.** Expone o altera datos de varios usuarios, o detiene una función.
- **3, alto.** Expone datos sensibles en masa, da control de administración o detiene la app.

Riesgo = P × I. De 1 a 2 es bajo, de 3 a 4 es medio y de 6 a 9 es alto.

Tratamiento: **mitigar** (con el requerimiento #n que lo cubre), **aceptar** (con justificación), **transferir** o **evitar**.

## Mapa de calor

Escriba los ID de riesgo en la celda que les corresponde.

```
            Impacto 1     Impacto 2     Impacto 3
P 3      |             |     R-02/R-03/R-06        |      R05       |
P 2      |             |             |             |       R-01/R-04     
P 1      |             |             |             |
```
