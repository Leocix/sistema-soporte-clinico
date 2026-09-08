# Herramientas de la documentación

## `md_a_docx.py`

Genera `01_preinforme/Pre_informe_final.docx` a partir de `Pre_informe_final.md`.

```bash
cd documentacion/01_preinforme
python ../herramientas/md_a_docx.py
```

El documento **no se construye desde cero**: parte de `Pre_informe_40.docx`,
que es la plantilla institucional entregada por la Escuela y ya trae la portada
de la universidad, la sección de información general y los estilos de
encabezado. El script conserva todo lo anterior al índice, actualiza la fecha de
presentación y repone el cuerpo desde el Markdown. Así el formato exigido por el
subcriterio 1.6 de la rúbrica no depende de reproducirlo a mano.

**El Markdown es la fuente.** El `.docx` se regenera; no se edita a mano, porque
el siguiente cambio en el `.md` sobrescribiría la corrección.

Requisitos: `pip install python-docx`. Cierre el documento en Word antes de
ejecutarlo: Windows bloquea el archivo mientras está abierto.
