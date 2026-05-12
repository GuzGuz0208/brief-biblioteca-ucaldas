# Guia Git para trabajo en pareja

## Configuracion inicial (una sola vez por pareja)

### Paso 1: Una persona crea el fork

Solo una persona del equipo hace fork de mi repositorio en GitHub.

### Paso 2: Agregar al compañero como colaborador

En el fork creado: **Settings > Collaborators > Add people**

Agregar el usuario de GitHub del compañero.

### Paso 3: Ambos clonan el fork compartido

```bash
git clone https://github.com/..
```

### Paso 4: Ambos configuran el upstream

El upstream conecta su fork con mi repositorio original. Esto les permite recibir actualizaciones que yo haga durante el taller.

```bash
git remote add upstream https://github.com/YanethM/brief-biblioteca-ucaldas.git
```

Verificar que quedo bien:

```bash
git remote -v
# origin    https://github.com/su-fork/repo.git
# upstream  https://github.com/YanethM/brief-biblioteca-ucaldas.git
```

---

## Flujo de trabajo 

### Antes de empezar a trabajar

Siempre partir del estado mas reciente:

```bash
git pull origin main
```

### Trabajar en su rama

Cada tarea o sesion de trabajo va en una rama propia:

```bash
# Crear y moverse a una rama nueva
git checkout -b nombre-tarea

# Ejemplos de nombres
git checkout -b especificacion
git checkout -b prompts-sesion1
git checkout -b tests-prestamos
```

### Guardar avances

```bash
git add .
git commit -m "descripcion corta de lo que hicieron"
```

### Subir la rama al fork compartido

```bash
git push origin nombre-tarea
```

### Fusionar al main cuando la tarea esta lista

En GitHub, abrir un **Pull Request** desde su rama hacia `main` del mismo fork. El compañero revisa y aprueba. Luego hacen merge.

---

## Cuando yo actualice el repositorio original

Si les aviso que hice cambios en mi repositorio, ejecuten esto para recibirlos:

```bash
# Traer mis cambios
git fetch upstream

# Fusionarlos en su main local
git merge upstream/main

# Subir al fork para que el compañero tambien los tenga
git push origin main
```

---

## Reglas de oro

- **Siempre** hacer `git pull origin main` antes de empezar.
- **Nunca** trabajar directamente en `main`; usar ramas.
- **Coordinar** con el compañero cuando van a fusionar cambios.
- **Sincronizar** el upstream cuando yo les avise que actualice el repo.
