# Validacion local · 27 de octubre de 2026

- Windows x64, Python 3.12.10, entorno aislado `.venv`.
- 9 pruebas automaticas aprobadas: proximidad a frente, manos para clones,
  sosten/rearme del gesto, tolerancia a perdida breve, captura independiente del
  fondo, desaparicion/reaparicion, composicion de clones y Rasengan/reset.
- Los tres modelos locales arrancaron y procesaron un fotograma sintetico.
- Interfaz Tk abierta/cerrada sin webcam y distribucion visual revisada.
- OBS Studio 33.0.0 instalado desde el paquete oficial de WinGet.
- `tools/diagnose.py --camera 0 --virtual`: 12 fotogramas reales procesados,
  salida OBS Virtual Camera activa; hilo y camara liberados al finalizar.
- `pip check`: dependencias compatibles.

Pendiente de validacion humana: reconocer los gestos con la mano/iluminacion real,
calibrar un fondo sin personas, calidad percibida de los efectos y recepcion de la
camara virtual dentro de Teams. No se hizo una llamada ni se grabo la webcam.

## Correccion tras primera prueba del usuario

- Se observo `Fondo pendiente` en la app. Al pulsar el boton se verifico la cuenta
  regresiva; posteriormente la app mostro `Fondo listo` e `INVISIBLE`.
- Agregados aviso persistente, contador sobre la imagen y estado del boton para
  distinguir solicitud, captura en curso y fondo disponible.
- Deteccion de dedos considera profundidad; zona de frente ampliada, rostro
  reciente retenido 0,8 s ante oclusion y tolerancia de 0,18 s a perdida de gesto.
- 15 pruebas aprobadas, incluidas captura seguida de teletransporte, recaptura,
  dedos orientados hacia la camara y perdida breve/prolongada de deteccion.
- Prueba de callbacks Tk: boton encola captura, cuenta regresiva deshabilita el
  boton y la finalizacion muestra FONDO LISTO y retira el contador.
- Motor corregido comprobado con webcam 0 y salida OBS: 12 fotogramas procesados.
