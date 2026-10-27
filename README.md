# AnimeCam · Teams Camera Effects

Webcam con teletransporte de Goku, clones de sombra y Rasengan. Python 3.12,
Windows x64, webcam integrada o USB. Procesamiento local con MediaPipe y OpenCV;
sin API, cuentas, grabaciones ni subida de imagenes. La salida virtual se comparte
con la aplicacion que elijas (Teams, por ejemplo).

## Iniciar

1. Instala [Python 3.12](https://www.python.org/downloads/) si no esta disponible.
2. Instala [OBS Studio](https://obsproject.com/download). Su controlador registra
   **OBS Virtual Camera**. No hace falta abrir OBS; deja su camara virtual detenida
   porque AnimeCam envia los fotogramas directamente mediante `pyvirtualcam`.
3. Abre `start.bat`. La primera ejecucion crea `.venv` e instala dependencias.
4. Selecciona el indice de webcam: normalmente 0 es la integrada. Prueba 1 o 2
   para USB; los indices pueden cambiar al conectar dispositivos. Pulsa **Iniciar webcam**.
5. Pulsa **Capturar fondo**, apartate durante los 5 segundos y espera el aviso
   **Fondo listo**. Camara fija, iluminacion estable. Si ves tu silueta congelada
   al desaparecer, repite la captura con la habitacion vacia.
6. En Teams, abre **Configuracion → Dispositivos → Camara** y selecciona
   **OBS Virtual Camera**. Si no aparece, cierra Teams por completo y vuelve a abrirlo
   tras instalar OBS. Desactiva el desenfoque y fondos de Teams para conservar el efecto.

La app debe estar abierta con la webcam iniciada para que Teams reciba imagen.
Teams suele recordar la seleccion, pero esta app no inicia automaticamente con Teams.
El nombre del dispositivo sera OBS Virtual Camera, no AnimeCam. La vista previa sigue
funcionando si falta el controlador; el indicador dice **Solo vista previa**.

## Tecnicas

| Tecnica | Gesto | Control manual |
| --- | --- | --- |
| Teletransporte | Indice y medio extendidos junto a la frente; anular y menique doblados | 2 |
| Kage Bunshin | Dos manos visibles, indices extendidos y puntas juntas | 3 |
| Rasengan | Palma abierta hacia la camara | 4 |
| Volver a normal | Boton o teclado | 0 |
| Capturar fondo | Boton o teclado, cuenta regresiva de 5 s | 1 |

Sosten el gesto unos 0,6 segundos. Baja las manos al menos 0,35 segundos antes de
repetirlo; hay una pausa de 1,8 segundos entre activaciones. El gesto de Goku alterna
desaparecer/reaparecer incluso cuando solo se transmite el fondo: la deteccion sigue
mirando la webcam real. Los clones y Rasengan se activan y desactivan con su gesto.
Los controles manuales permiten ensayar; **Pausar gestos** evita activaciones al hablar.

El Rasengan sigue la palma abierta. Los clones usan segmentacion y una copia del
fondo; pueden fallar con poca luz, pelo, objetos o movimientos rapidos. El gesto de
Naruto es una aproximacion sencilla con indices juntos. No hay reconocimiento de
secuencias complejas de sellos todavia.

El fondo es una fotografia estatica en memoria; no se reconstruye lo que hay detras
de ti. Al desaparecer se oculta toda la imagen en vivo, incluidas otras personas y
objetos que entren al plano. No muevas la webcam tras calibrar. Los destellos y
efectos son dibujos procedurales, sin assets externos.

## Desarrollo y comprobaciones

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.venv\Scripts\python.exe -m unittest discover -s tests -v
.venv\Scripts\python.exe tools\diagnose.py
.venv\Scripts\python.exe app.py --smoke-test
# Opcional: abre webcam unos segundos sin guardar imagenes
.venv\Scripts\python.exe tools\diagnose.py --camera 0
# Opcional: comprueba el controlador OBS con imagen sintetica
.venv\Scripts\python.exe tools\diagnose.py --virtual
```

`camera_fx/gestures.py` contiene geometria y antirrebote, `effects.py` compone los
efectos, `engine.py` gestiona modelos/camara en un hilo y `app.py` la interfaz.
Salida 960×540, objetivo 24 FPS; depende del notebook. Se usa MediaPipe 0.10.21
porque incluye las soluciones y modelos locales; es una API heredada fijada para
este prototipo, no actualizar MediaPipe sin migrar el motor.

`requirements.txt` declara las dependencias directas y `requirements-lock.txt`
fija el entorno completo comprobado en Windows con Python 3.12.

Si la webcam no abre, cierra otras aplicaciones que la usen y revisa los permisos
de camara para aplicaciones de escritorio en Windows. Si la salida virtual no
abre, deten la camara virtual de OBS y otras instancias de AnimeCam. Reinicia la
captura desde la app tras instalar el controlador.

Referencias: [pyvirtualcam](https://github.com/letmaik/pyvirtualcam),
[camara virtual OBS](https://obsproject.com/kb/virtual-camera-guide),
[MediaPipe 0.10.21](https://pypi.org/project/mediapipe/0.10.21/).
