# Cómo generar los .exe sin tener Windows (vía GitHub Actions)

Esta carpeta ya tiene todo listo: cuando subas estos archivos a un repositorio
de GitHub, un robot de GitHub (no tu computador) abre una máquina con Windows,
instala Python, instala numpy/sympy, y compila los dos programas a `.exe`.
Tú solo descargas el resultado al final. Es gratis para repos normales.

## Contenido de esta carpeta (NO renombrar ni mover nada)

```
Calculadora_Gauss_Jordan.py
calculadora_valores_propios.py
requirements.txt
.github/
  └── workflows/
        └── build-windows-exe.yml   ← el "robot" que compila
```

La carpeta `.github/workflows/` es la que GitHub reconoce automáticamente.
Si esa carpeta no queda exactamente en la raíz del repositorio, no funcionará.

---

## Paso 1 — Crear cuenta en GitHub (si no tienes)

Entra a https://github.com y crea una cuenta gratuita.

## Paso 2 — Crear un repositorio nuevo

1. Click en el botón verde **"New"** (o el ícono **+** arriba a la derecha → "New repository").
2. Nombre sugerido: `calculadoras-algebra-lineal`.
3. Puede ser **Público** o **Privado**, no importa.
4. NO marques "Add a README" (para que el repo quede vacío).
5. Click en **"Create repository"**.

## Paso 3 — Subir los archivos manteniendo la estructura de carpetas

La forma más confiable (recomendada), usando solo el navegador:

1. En la página del repositorio recién creado, click en **"uploading an existing file"**
   (o el botón **"Add file" → "Upload files"**).
2. Descomprime el .zip que te entregué en tu computador.
3. **Arrastra la carpeta completa** (no los archivos uno por uno) desde el explorador
   de archivos hacia la zona de carga del navegador. Los navegadores modernos (Chrome,
   Edge) preservan la estructura de subcarpetas al arrastrar una carpeta completa,
   así que `.github/workflows/build-windows-exe.yml` debe aparecer en la lista con
   esa misma ruta.
4. Baja al final de la página y click en **"Commit changes"**.

> Si al arrastrar la carpeta GitHub no reconoce las subcarpetas (a veces pasa con
> Safari o con clics individuales), la alternativa sin usar la terminal es instalar
> **GitHub Desktop** (https://desktop.github.com/), clonar el repo vacío, copiar
> estos archivos dentro de la carpeta clonada respetando la estructura, y darle
> "Commit" + "Push" desde la app.

## Paso 4 — Esperar a que GitHub compile

1. Ve a la pestaña **"Actions"** en la parte superior del repositorio.
2. Verás un workflow llamado **"Build Windows EXE"** ejecutándose (ícono amarillo 🟡).
   Si no arrancó solo, entra a "Build Windows EXE" → botón **"Run workflow"** → "Run workflow".
3. Espera 2-4 minutos hasta que el ícono se ponga verde ✅.

## Paso 5 — Descargar los .exe

1. Click en la ejecución terminada (la que tiene el ✅).
2. Baja hasta la sección **"Artifacts"**.
3. Descarga el archivo `calculadoras-exe.zip`.
4. Dentro encontrarás:
   - `Calculadora_Gauss_Jordan.exe`
   - `Calculadora_Valores_Propios.exe`

Ambos son ejecutables independientes (`--onefile`): se pueden mover a cualquier
PC con Windows y abrir con doble clic, sin necesidad de instalar Python.

---

## Notas

- Cada vez que vuelvas a subir cambios a estos archivos (`git push`), el .exe se
  recompila automáticamente.
- Si quieres recompilar sin cambiar nada, usa el botón **"Run workflow"** en la
  pestaña Actions (Paso 4.2).
- Los artefactos de GitHub Actions se borran automáticamente después de 30 días
  (puedes cambiar `retention-days` en el archivo `.yml` si quieres conservarlos más).
