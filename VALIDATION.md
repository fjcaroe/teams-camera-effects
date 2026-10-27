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
