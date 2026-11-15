# Fuente POS + Unreal
**El Puestito** | Inmótica local | Unreal Engine 5.8

## Crear un paquete Win64

En PowerShell, configura `$env:UE_ROOT` a tu instalación Unreal Engine 5.8, por ejemplo `C:\Program Files\Epic Games\UE_5.8`, y ejecuta:

```powershell
./Tools/compilar_inmotica.ps1
```

El `.exe` aparecerá en `Build/Package/Windows`. Este paso es opcional: el proyecto puede probarse desde Unreal Editor.
