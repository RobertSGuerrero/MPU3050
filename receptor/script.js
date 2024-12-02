let scene, camera, renderer, cube;

// Variables para almacenar los valores de referencia
let referencePitch = 0;
let referenceRoll = 0;

// Ajuste del intervalo de tiempo (deltaTime) para integración
let lastUpdateTime = Date.now();

// Función para obtener el ancho del elemento padre
function parentWidth(elem) {
  return elem.parentElement.clientWidth;
}

// Función para obtener el alto del elemento padre
function parentHeight(elem) {
  return elem.parentElement.clientHeight;
}

// Inicializar la escena 3D
function init3D() {
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0xffffff);

  camera = new THREE.PerspectiveCamera(
    75,
    parentWidth(document.getElementById("3Dcube")) / parentHeight(document.getElementById("3Dcube")),
    0.1,
    1000
  );

  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(parentWidth(document.getElementById("3Dcube")), parentHeight(document.getElementById("3Dcube")));
  document.getElementById("3Dcube").appendChild(renderer.domElement);

  // Crear geometría del cubo
  const geometry = new THREE.BoxGeometry(5, 1, 4);

  // Materiales para cada cara del cubo
  const cubeMaterials = [
    new THREE.MeshBasicMaterial({ color: 0x03045e }),
    new THREE.MeshBasicMaterial({ color: 0x023e8a }),
    new THREE.MeshBasicMaterial({ color: 0x0077b6 }),
    new THREE.MeshBasicMaterial({ color: 0x03045e }),
    new THREE.MeshBasicMaterial({ color: 0x023e8a }),
    new THREE.MeshBasicMaterial({ color: 0x0077b6 }),
  ];

  // Crear el cubo con la geometría y los materiales
  cube = new THREE.Mesh(geometry, cubeMaterials);
  scene.add(cube);

  camera.position.z = 5;
  renderer.render(scene, camera);
}

// Redimensionar el objeto 3D cuando cambie el tamaño del navegador
function onWindowResize() {
  camera.aspect = parentWidth(document.getElementById("3Dcube")) / parentHeight(document.getElementById("3Dcube"));
  camera.updateProjectionMatrix();
  renderer.setSize(parentWidth(document.getElementById("3Dcube")), parentHeight(document.getElementById("3Dcube")));
}

window.addEventListener("resize", onWindowResize, false);

// Crear la representación 3D
init3D();

// Función para actualizar la rotación del cubo en base a los ángulos de pitch y roll
function updateRotation(pitch, roll) {
  const currentTime = Date.now();
  const deltaTime = (currentTime - lastUpdateTime) / 1; // Delta tiempo en segundos
  lastUpdateTime = currentTime;

  // Aplicar las rotaciones al cubo
  cube.rotation.x = -(pitch - referencePitch); // Pitch ajustado
  cube.rotation.z = -(roll - referenceRoll);   // Roll ajustado
}

// Función para obtener datos del sensor y actualizar el HTML
function fetchSensorData() {
  fetch("/events")
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .then((data) => {
      if (data && data.accelerometer && data.gyro) {
        const accX = data.accelerometer.accX;
        const accY = data.accelerometer.accY;
        const accZ = data.accelerometer.accZ;

        const gyroX = data.gyro.gyroX; // Velocidad angular en X
        const gyroY = data.gyro.gyroY; // Velocidad angular en Y
        const gyroZ = data.gyro.gyroZ; // Velocidad angular en Z

        // Calcular los ángulos de pitch y roll
        const pitch = Math.atan2(accY, Math.sqrt(accX ** 2 + accZ ** 2));
        const roll = Math.atan2(accX, Math.sqrt(accY ** 2 + accZ ** 2));

        // Actualizar datos del acelerómetro en el HTML
        document.getElementById("accX").innerHTML = accX.toFixed(2);
        document.getElementById("accY").innerHTML = accY.toFixed(2);
        document.getElementById("accZ").innerHTML = accZ.toFixed(2);

        // Actualizar datos del giroscopio en el HTML
        document.getElementById("gyroX").innerHTML = gyroX.toFixed(2);
        document.getElementById("gyroY").innerHTML = gyroY.toFixed(2);
        document.getElementById("gyroZ").innerHTML = gyroZ.toFixed(2);

        // Cambiar la rotación del cubo basado en pitch y roll
        updateRotation(pitch, roll);
      }
    })
    .catch((error) => {
      console.error("Error fetching sensor data:", error);
    });
}

// Obtener datos del sensor cada 50 ms
setInterval(fetchSensorData, 1);

// Función para renderizar la animación 3D en sincronización con el ciclo de pantalla
function animate3D() {
  requestAnimationFrame(animate3D);
  renderer.render(scene, camera);
}

animate3D(); // Iniciar la animación sincronizada

// Función para resetear la posición del cubo y establecer nuevos valores de referencia
function resetPosition() {
  fetch("/events")
    .then((response) => response.json())
    .then((data) => {
      if (data && data.accelerometer) {
        const accX = data.accelerometer.accX;
        const accY = data.accelerometer.accY;
        const accZ = data.accelerometer.accZ;

        // Calcular los ángulos actuales de pitch y roll como nueva referencia
        referencePitch = Math.atan2(accY, Math.sqrt(accX ** 2 + accZ ** 2));
        referenceRoll = Math.atan2(accX, Math.sqrt(accY ** 2 + accZ ** 2));

        console.log("Nuevos valores de referencia establecidos", {
          referencePitch,
          referenceRoll,
        });
      }
    })
    .catch((error) => {
      console.error("Error al capturar valores de referencia:", error);
    });
}


