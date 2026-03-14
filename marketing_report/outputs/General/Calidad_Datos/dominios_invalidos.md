# Analisis de Dominios de Correo Invalidos

Este informe identifica dominios de correo electronico que no existen o son errores de tipeo, y estima cuantos leads podrian recuperarse si se corrigiesen.

## 1. Dominios con Errores de Tipeo Conocidos

Se detectaron **27** dominios con errores de tipeo, afectando **1,617** leads.
**Estimacion de matches recuperables si se corrigiesen:** 49 nuevos matches potenciales.

| Dominio_Typo   | Dominio_Correcto   |   Total_Leads |   Matcheados_Actuales |   No_Matcheados |   Tasa_Dominio_Correcto_% |   Matches_Recuperables_Est |
|:---------------|:-------------------|--------------:|----------------------:|----------------:|--------------------------:|---------------------------:|
| gmail.com.ar   | gmail.com          |           434 |                     7 |             427 |                      3.67 |                         15 |
| gmail.con      | gmail.com          |           354 |                    11 |             343 |                      3.67 |                         12 |
| gamil.com      | gmail.com          |           171 |                     5 |             166 |                      3.67 |                          6 |
| gmai.com       | gmail.com          |           119 |                     5 |             114 |                      3.67 |                          4 |
| gmil.com       | gmail.com          |            68 |                     2 |              66 |                      3.67 |                          2 |
| gimail.com     | gmail.com          |            65 |                     2 |              63 |                      3.67 |                          2 |
| gmail.comm     | gmail.com          |            63 |                     0 |              63 |                      3.67 |                          2 |
| gmal.com       | gmail.com          |            57 |                     0 |              57 |                      3.67 |                          2 |
| hmail.com      | gmail.com          |            45 |                     0 |              45 |                      3.67 |                          1 |
| gmail.co       | gmail.com          |            41 |                     1 |              40 |                      3.67 |                          1 |
| gmial.com      | gmail.com          |            41 |                     1 |              40 |                      3.67 |                          1 |
| gmeil.com      | gmail.com          |            35 |                     0 |              35 |                      3.67 |                          1 |
| gnail.com      | gmail.com          |            30 |                     3 |              27 |                      3.67 |                          0 |
| hotmail.con    | hotmail.com        |            24 |                     1 |              23 |                      1.19 |                          0 |
| gmail.comc     | gmail.com          |            13 |                     0 |              13 |                      3.67 |                          0 |
| gotmail.com    | hotmail.com        |            13 |                     0 |              13 |                      1.19 |                          0 |
| hotmal.com     | hotmail.com        |            10 |                     0 |              10 |                      1.19 |                          0 |
| hotmil.com     | hotmail.com        |             7 |                     0 |               7 |                      1.19 |                          0 |
| gmail.cm       | gmail.com          |             6 |                     0 |               6 |                      3.67 |                          0 |
| icloud.con     | icloud.com         |             5 |                     0 |               5 |                      6.31 |                          0 |
| hotamail.com   | hotmail.com        |             4 |                     0 |               4 |                      1.19 |                          0 |
| iclud.com      | icloud.com         |             3 |                     0 |               3 |                      6.31 |                          0 |
| hotamil.com    | hotmail.com        |             3 |                     0 |               3 |                      1.19 |                          0 |
| outlook.con    | outlook.com        |             3 |                     0 |               3 |                      2.17 |                          0 |
| live.con       | live.com           |             1 |                     0 |               1 |                      1.32 |                          0 |
| yahooo.com     | yahoo.com          |             1 |                     0 |               1 |                      2.06 |                          0 |
| gmail.om       | gmail.com          |             1 |                     1 |               0 |                      3.67 |                          0 |

### Como se calcula la estimacion
Se toma la tasa de match del dominio correcto (ej: gmail.com tiene ~5.5%) y se aplica a los leads no matcheados del dominio con typo. Esto da una estimacion conservadora de cuantos matches se recuperarian.

## 2. Otros Dominios Poco Comunes (Revision Manual)

Los siguientes dominios tienen 5 o mas leads pero no son proveedores de correo comunes. Podrian ser dominios corporativos legitimos, institucionales, o errores.

| Domain               |   Total_Leads |   Matcheados |   Tasa_Match_% |
|:---------------------|--------------:|-------------:|---------------:|
| abc.gob.ar           |           137 |            1 |           0.73 |
| mail.com             |            70 |            1 |           1.43 |
| bue.edu.ar           |            57 |            0 |           0    |
| example.com          |            56 |            3 |           5.36 |
| gmail.com.com        |            52 |            0 |           0    |
| admin.com            |            43 |            0 |           0    |
| sanluis.edu.ar       |            41 |            0 |           0    |
| gmail.coma           |            41 |            0 |           0    |
| gmail.i.comcom.com   |            41 |            0 |           0    |
| gmail.coml           |            34 |            0 |           0    |
| gamail.com           |            34 |            0 |           0    |
| mi.unc.edu.ar        |            32 |            0 |           0    |
| ymail.com            |            31 |            1 |           3.23 |
| devnull.facebook.com |            26 |            0 |           0    |
| gmail.comn           |            26 |            0 |           0    |
| gmail.coms           |            22 |            0 |           0    |
| gmaill.com           |            21 |            0 |           0    |
| fibertel.com.ar      |            18 |            0 |           0    |
| remax.com.ar         |            17 |            0 |           0    |
| gmail.comr           |            17 |            0 |           0    |
| gmsil.com            |            17 |            0 |           0    |
| hitmail.com          |            16 |            1 |           6.25 |
| hotmai.com           |            15 |            0 |           0    |
| gmail.comv           |            15 |            0 |           0    |
| gmail.comcom         |            15 |            0 |           0    |
| gmail.comi           |            15 |            0 |           0    |
| email.com            |            13 |            0 |           0    |
| gmail.om.com.comb    |            13 |            0 |           0    |
| hormail.com          |            12 |            1 |           8.33 |
| homail.com           |            12 |            0 |           0    |

## Nota Importante

**A la fecha (marzo 2026), las correcciones de dominios identificadas en este informe NO se aplican en el proceso de matching de leads con inscriptos** (`02_cruce_datos.py`). Este reporte es exclusivamente de auditoria y diagnostico. Los emails con dominios erroneos siguen sin matchear contra la base de inscriptos. Si se implementara la correccion previa al cruce, los matches recuperables estimados en la tabla anterior podrian concretarse.

