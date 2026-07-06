# Despliegue de Aplicación Web con DevOps

## Descripción del proyecto

Este proyecto implementa una simulación local de un proceso DevOps para generar, validar, contenerizar y desplegar una aplicación web en tres ambientes diferentes:

- Desarrollo (Dev)
- Control de calidad (QA)
- Producción (Prod)

La solución se ejecuta dentro de una máquina virtual Ubuntu y utiliza herramientas de automatización, infraestructura como código, contenedores y orquestación.

Los ambientes no utilizan máquinas virtuales independientes. Se encuentran separados lógicamente mediante namespaces dentro de un clúster local de Kubernetes proporcionado por Minikube.

---

## Objetivo

Automatizar el proceso de despliegue de una aplicación web mediante un pipeline de Jenkins que integre las siguientes actividades:

1. Validación de scripts Bash.
2. Generación de la aplicación web.
3. Validación de infraestructura con Terraform.
4. Validación de configuración con Ansible.
5. Validación de archivos Kubernetes.
6. Construcción de imágenes Docker.
7. Carga de imágenes en Minikube.
8. Despliegue en Kubernetes.
9. Verificación de los recursos desplegados.

---

## Herramientas utilizadas

### Máquina virtual Ubuntu

Proporciona el sistema operativo Linux donde se ejecutan las herramientas, los scripts, Jenkins, Docker y Minikube.

### Git

Controla las versiones de los archivos del proyecto y permite registrar los cambios realizados mediante commits.

### Jenkins

Automatiza el proceso de integración y despliegue continuo mediante un pipeline definido en el archivo `Jenkinsfile`.

Jenkins utiliza un agente instalado en la máquina virtual para acceder a Docker, Terraform, Ansible, ShellCheck, kubectl y Minikube.

### ShellCheck

Analiza el script Bash de la aplicación para detectar errores de sintaxis y malas prácticas.

### Docker

Empaqueta la aplicación web y el servidor Nginx dentro de imágenes independientes para Dev, QA y Prod.

### Ansible

Verifica y prepara el entorno local. Comprueba la instalación de las herramientas y la existencia de los namespaces del proyecto.

### Terraform

Representa la infraestructura como código y genera información de configuración para los tres ambientes.

### Minikube

Proporciona un clúster local de Kubernetes dentro de la máquina virtual.

### Kubernetes

Administra los deployments, pods, servicios, réplicas y namespaces de los ambientes.

---

## Arquitectura general

```text
Equipo físico
└── VirtualBox
    └── Máquina virtual Ubuntu
        ├── Git
        ├── Jenkins Controller
        ├── Jenkins Agent
        ├── ShellCheck
        ├── Terraform
        ├── Ansible
        ├── Docker
        └── Minikube
            ├── Namespace web-dev
            ├── Namespace web-qa
            └── Namespace web-prod
