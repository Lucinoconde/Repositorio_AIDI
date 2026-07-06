import getpass
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

# 1. Definición de los dispositivos en un diccionario
dispositivos = [
    {
        "device_type": "cisco_ios",  
        "host": "170.5.0.1",    # IP del Router
        "username": "admin",
        "secret": "SecretClass123",  # Contraseña para el modo enable 
    },
    {
        "device_type": "cisco_ios",
        "host": "170.5.0.254",    # IP del Switch
        "username": "admin",
        "secret": "SecretClass123",
    },
    {       #agregando un firewall cambio 1
        "device_type": "cisco_ios",
        "host": "170.5.0.2",    # IP del Firewall
        "username": "admin",
        "secret": "SecretClass123",
    }
]

# 2. Comandos de configuración básica que se aplicarán
comandos_config = [
    "no ip domain-lookup",
    "banner motd # ACCESO RESTRINGIDO - SOLO PERSONAL AUTORIZADO #",
    "line vty 0 4",
    "exec-timeout 15 0",
    "logging synchronous",
    "exit"
]

def automatizar_configuracion(lista_equipos, comandos):
    # Solicitar la contraseña de SSH de forma segura una sola vez
    password = getpass.getpass(prompt="Introduce la contraseña SSH para los equipos: ")
    
    for equipo in lista_equipos:
        # Añadir la contraseña dinámica al diccionario del equipo
        equipo["password"] = password
        
        print(f"\n--- Conectando al dispositivo {equipo['host']} ---")
        
        try:
            # Establecer la conexión SSH
            net_connect = ConnectHandler(**equipo)
            
            # Entrar en modo privileged EXEC (enable) si es necesario
            net_connect.enable()
            
            # Obtener el prompt actual para saber el nombre del equipo
            prompt_actual = net_connect.find_prompt()
            print(f"Conexión exitosa con: {prompt_actual}")
            
            # Enviar los comandos de configuración
            print("Aplicando configuración básica...")
            output = net_connect.send_config_set(comandos)
            print(output)
            
            # Guardar la configuración en la NVRAM (copy running-config startup-config)
            print("Guardando cambios en la memoria...")
            net_connect.save_config()
            
            # Cerrar la sesión de manera limpia
            net_connect.disconnect()
            print(f"--- Configuración finalizada en {equipo['host']} ---\n")
            
        except NetmikoTimeoutException:
            print(f"[ERROR]: Tiempo de espera agotado al conectar a {equipo['host']}. Revisa la IP o la red.")
        except NetmikoAuthenticationException:
            print(f"[ERROR]: Fallo de autenticación en {equipo['host']}. Usuario o contraseña incorrectos.")
        except Exception as e:
            print(f"[ERROR inesperado]: {e}")

if __name__ == "__main__":
    automatizar_configuracion(dispositivos, comandos_config)