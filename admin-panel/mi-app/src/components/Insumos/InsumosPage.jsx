import React, { useState } from 'react';
import IngredientesList from '../ingredientes/IngredientesList';
import EmpaquesList from './EmpaquesList';

const InsumosPage = () => {
  const [tab, setTab] = useState('ingredients');

  return (
    <div className="container-fluid p-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1 style={{color: '#2c3e50', fontWeight: '700'}}>📦 Supplies Management</h1>
        <div className="btn-group shadow-sm">
          <button 
            className={`btn ${tab === 'ingredients' ? 'btn-primary' : 'btn-outline-primary'}`}
            onClick={() => setTab('ingredients')}
          >
            🧂 Ingredients
          </button>
          <button 
            className={`btn ${tab === 'packaging' ? 'btn-primary' : 'btn-outline-primary'}`}
            onClick={() => setTab('packaging')}
          >
            🛍️ Packaging
          </button>
        </div>
      </div>
      
      <hr className="mb-4" />

      {tab === 'ingredients' ? <IngredientesList /> : <EmpaquesList />}
    </div>
  );
};

export default InsumosPage;