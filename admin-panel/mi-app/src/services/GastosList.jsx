import React, { useState, useEffect } from 'react';
import { gastosService } from '../../services/gastosService';

const GastosList = () => {
  const [gastos, setGastos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [nuevoGasto, setNuevoGasto] = useState({
    descripcion: '',
    monto: '',
    fecha: new Date().toISOString().split('T')[0],
    categoria: 'Operativo'
  });

  const cargarGastos = async () => {
    try {
      setLoading(true);
      const data = await gastosService.getGastos();
      setGastos(data);
    } catch (err) {
      setError('No se pudieron cargar los gastos.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarGastos();
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNuevoGasto(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!nuevoGasto.descripcion || !nuevoGasto.monto || !nuevoGasto.fecha) {
      alert('Por favor, completa todos los campos.');
      return;
    }
    try {
      await gastosService.createGasto(nuevoGasto);
      // Limpiar formulario
      setNuevoGasto({
        descripcion: '',
        monto: '',
        fecha: new Date().toISOString().split('T')[0],
        categoria: 'Operativo'
      });
      // Recargar la lista
      cargarGastos();
    } catch (err) {
      alert('Error al registrar el gasto.');
    }
  };

  const handleEliminar = async (id) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar este gasto?')) {
      try {
        await gastosService.deleteGasto(id);
        cargarGastos();
      } catch (err) {
        alert('Error al eliminar el gasto.');
      }
    }
  };

  const formatearMoneda = (valor) => {
    return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(valor || 0);
  };

  return (
    <div className="container-fluid p-4">
      <h2 className="mb-4">💸 Gestión de Gastos Fijos y Operativos</h2>

      <div className="row">
        {/* Columna del Formulario */}
        <div className="col-lg-4 mb-4">
          <div className="card shadow-sm">
            <div className="card-header">
              <h5>Registrar Nuevo Gasto</h5>
            </div>
            <div className="card-body">
              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label htmlFor="descripcion" className="form-label">Descripción</label>
                  <input type="text" id="descripcion" name="descripcion" className="form-control" value={nuevoGasto.descripcion} onChange={handleInputChange} required />
                </div>
                <div className="mb-3">
                  <label htmlFor="monto" className="form-label">Monto</label>
                  <input type="number" id="monto" name="monto" className="form-control" value={nuevoGasto.monto} onChange={handleInputChange} required placeholder="Ej: 50000" />
                </div>
                <div className="mb-3">
                  <label htmlFor="fecha" className="form-label">Fecha del Gasto</label>
                  <input type="date" id="fecha" name="fecha" className="form-control" value={nuevoGasto.fecha} onChange={handleInputChange} required />
                </div>
                <div className="mb-3">
                  <label htmlFor="categoria" className="form-label">Categoría</label>
                  <select id="categoria" name="categoria" className="form-select" value={nuevoGasto.categoria} onChange={handleInputChange}>
                    <option value="Operativo">Operativo</option>
                    <option value="Arriendo">Arriendo</option>
                    <option value="Servicios">Servicios Públicos</option>
                    <option value="Salarios">Salarios</option>
                    <option value="Marketing">Marketing</option>
                    <option value="Varios">Varios</option>
                  </select>
                </div>
                <button type="submit" className="btn btn-primary w-100">Agregar Gasto</button>
              </form>
            </div>
          </div>
        </div>

        {/* Columna de la Tabla */}
        <div className="col-lg-8">
          <div className="card shadow-sm">
            <div className="card-header">
              <h5>Historial de Gastos</h5>
            </div>
            <div className="card-body p-0">
              {loading && <p className="p-3">Cargando...</p>}
              {error && <p className="p-3 text-danger">{error}</p>}
              {!loading && !error && (
                <div className="table-responsive">
                  <table className="table table-hover mb-0">
                    <thead>
                      <tr>
                        <th>Fecha</th>
                        <th>Descripción</th>
                        <th>Categoría</th>
                        <th className="text-end">Monto</th>
                        <th></th>
                      </tr>
                    </thead>
                    <tbody>
                      {gastos.map(gasto => (
                        <tr key={gasto.id_gasto}>
                          <td>{gasto.fecha}</td>
                          <td>{gasto.descripcion}</td>
                          <td><span className="badge bg-secondary">{gasto.categoria}</span></td>
                          <td className="text-end fw-bold">{formatearMoneda(gasto.monto)}</td>
                          <td className="text-center">
                            <button className="btn btn-sm btn-outline-danger" onClick={() => handleEliminar(gasto.id_gasto)}>🗑️</button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GastosList;