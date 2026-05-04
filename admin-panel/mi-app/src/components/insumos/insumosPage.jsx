import React, { useState } from 'react';
import IngredientesList from '../ingredientes/IngredientesList';
import EmpaquesList from './EmpaquesList';
import './InsumosPage.css'; // Crea uno pequeño para las pestañas

const InsumosPage = () => {
  const [tab, setTab] = useState('ingredientes');

  return (
    <div className="container-fluid p-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1 style={{color: '#2c3e50', fontWeight: '700'}}>📦 Gestión de Insumos</h1>
        <div className="btn-group shadow-sm">
          <button 
            className={`btn ${tab === 'ingredientes' ? 'btn-primary' : 'btn-outline-primary'}`}
            onClick={() => setTab('ingredientes')}
          >
            🧂 Ingredientes
          </button>
          <button 
            className={`btn ${tab === 'empaques' ? 'btn-primary' : 'btn-outline-primary'}`}
            onClick={() => setTab('empaques')}
          >
            🛍️ Empaques
          </button>
        </div>
      </div>
      
      <hr className="mb-4" />

      {tab === 'ingredientes' ? <IngredientesList /> : <EmpaquesList />}
    </div>
  );
};

export default InsumosPage;