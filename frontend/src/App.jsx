import {useState } from "react";

function App() {

  function App () {
    const [pantalla, setPantalla] = useState("Inicio"); // control de pantalla

    return (
     < div 
     style={{
      fontFamily: 'Arial, sans-serif',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignContent: 'center',
      height: '100vh',
      backgroundColor: '#f0f4f8',
      textAlign : 'center',
     }}
      >

        {pantalla === "Inicio" && (
        <>

        <h1 style={{ fontSize: "4rem", marginBottom: "50px", color: "#4CAF50" }}> 
          chweck-now

           </h1>

           <button

            onClick={() => alert("Ir a incio de sesión")}
            style={{
              padding: "15px 30px",
              fontSize: "1.5rem",
              margin: "10px",
              borderRadius: "8px",
              border: "none",
              backgroundColor: "#4CAF50",
              color: "white",
              cursor: "pointer",
              boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
            }}
            >

            Iniciar sesión
            </button>

            <button
            onClick={() => alert("Ir  a crear cuenta")}
            style={{
              padding: "15px 30px",
              fontSize: "1.5rem",
              margin: "10px",
              borderRadius: "8px",
              border: "2px solid #4CAF50",
              backgrounn: "white",
              color: "#4CAF50",
              cursor: "pointer",
              boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",

            }}
            > 

            Crear cuenta  
            </button>
          </>  
        )}
      </div>
    );
  }
}

import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
  