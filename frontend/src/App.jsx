import {usestate } from "react";

function app () { 
  const [pestaña, setpestaña] = usestate("Inicio"); // pestaña activa 
  const [areaseleccionada, setAreaseleccionada] = usestate(null); 

  // datos del clima simulados por cada area

  const datosclima ={
    "Area1 - Norte": { temperatura: "22°C", humedad: "60%", viento: "15 km/h" },
    "Area2 - Sur": { temperatura: "25°C", humedad: "55%", viento: "10 km/h" },
    "Area3 - Este": { temperatura: "20°C", humedad: "70%", viento: "20 km/h" },
    "Area4 - Oeste": { temperatura: "23°C", humedad: "65%", viento: "12 km/h" },
  };
}

