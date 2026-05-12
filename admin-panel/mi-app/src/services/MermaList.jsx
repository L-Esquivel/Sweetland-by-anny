import React, { useState, useEffect } from 'react';
import { mermaService } from '../../services/mermaService';
import { productosService } from '../../services/productosService';
import { ingredientesService } from '../../services/ingredientesService';

const MermaList = () => {
  const [registros, setRegistros] = useState([]);
  const [productos, setProductos] = useState([]);
  const [ingredientes, setIngredientes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [tipoMerma, setTipoMerma] = useState('producto'); // 'producto' o 'ingrediente'
  const [nuevoRegistro, setNuevoRegistro] = useState({
    id_item: '',
    cantidad: '',
    fecha: new Date().toISOString().split('T')[0],
    motivo: 'Caducidad'
  });

  const cargarDatos = async () => {
    try {
      setLoading(true);
      const [mermaData, productosData, ingredientesData] = await Promise.all([
        mermaService.getMermaRegistros(),
        productosService.getProductos(),
        ingredientesService.getIngredientes()
      ]);
      setRegistros(mermaData);
      setProductos(productosData);
      setIngredientes(ingredientesData);
    } catch (err) {
      setError('No se pudieron cargar los datos.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarDatos();
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNuevoRegistro(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!nuevoRegistro.id_item || !nuevoRegistro.cantidad || !nuevoRegistro.fecha) {
      alert('Por favor, selecciona un item y completa todos los campos.');
      return;
    }

    const dataToSend = {
      id_producto: tipoMerma === 'producto' ? nuevoRegistro.id_item : null,
      id_ingrediente: tipoMerma === 'ingrediente' ? nuevoRegistro.id_item : null,
      cantidad: nuevoRegistro.cantidad,
      fecha: nuevoRegistro.fecha,
      motivo: nuevoRegistro.motivo
    };

    try {
      await mermaService.createMermaRegistro(dataToSend);
      setNuevoRegistro({ id_item: '', cantidad: '', fecha: new Date().toISOString().split('T')[0], motivo: 'Caducidad' });
      cargarDatos();
    } catch (err) {
      alert(`Error al registrar la merma: ${err.message}`);
    }
  };

  const handleEliminar = async (id) => {
    if (window.confirm('¿Eliminar este registro de merma?')) {
      try {
        await mermaService.deleteMermaRegistro(id);
        cargarDatos();
      } catch (err) {
        alert('Error al eliminar.');
      }
    }
  };

  const formatearMoneda = (valor) => {
    return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(valor || 0);
  };

  return (
    <div className="container-fluid p-4">
      <h2 className="mb-4">📉 Gestión de Merma (Pérdidas)</h2>

      <div className="row">
        <div className="col-lg-4 mb-4">
          <div className="card shadow-sm">
            <div className="card-header"><h5>Registrar Nueva Pérdida</h5></div>
            <div className="card-body">
              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label className="form-label">Tipo de Merma</label>
                  <select className="form-select" value={tipoMerma} onChange={(e) => { setTipoMerma(e.target.value); setNuevoRegistro(p => ({...p, id_item: ''}))}}>
                    <option value="producto">Producto Terminado</option>
                    <option value="ingrediente">Ingrediente / Insumo</option>
                  </select>
                </div>

                <div className="mb-3">
                  <label htmlFor="id_item" className="form-label">Item</label>
                  <select id="id_item" name="id_item" className="form-select" value={nuevoRegistro.id_item} onChange={handleInputChange} required>
                    <option value="">-- Seleccione --</option>
                    {tipoMerma === 'producto' 
                      ? productos.map(p => <option key={p.id_producto} value={p.id_producto}>{p.nombre}</option>)
                      : ingredientes.map(i => <option key={i.id_ingrediente} value={i.id_ingrediente}>{i.nombre}</option>)
                    }
                  </select>
                </div>

                <div className="mb-3">
                  <label htmlFor="cantidad" className="form-label">Cantidad Perdida</label>
                  <input type="number" id="cantidad" name="cantidad" className="form-control" value={nuevoRegistro.cantidad} onChange={handleInputChange} required step="0.01" />
                </div>

                <div className="mb-3">
                  <label htmlFor="fecha" className="form-label">Fecha de la Pérdida</label>
                  <input type="date" id="fecha" name="fecha" className="form-control" value={nuevoRegistro.fecha} onChange={handleInputChange} required />
                </div>

                <div className="mb-3">
                  <label htmlFor="motivo" className="form-label">Motivo</label>
                  <select id="motivo" name="motivo" className="form-select" value={nuevoRegistro.motivo} onChange={handleInputChange}>
                    <option value="Caducidad">Caducidad / Vencimiento</option>
                    <option value="Error de Produccion">Error de Producción</option>
                    <option value="No Vendido">Producto no Vendido</option>
                    <option value="Daño">Daño / Rotura</option>
                    <option value="Otro">Otro</option>
                  </select>
                </div>
                <button type="submit" className="btn btn-danger w-100">Registrar Pérdida</button>
              </form>
            </div>
          </div>
        </div>

        <div className="col-lg-8">
          <div className="card shadow-sm">
            <div className="card-header"><h5>Historial de Mermas</h5></div>
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
                        <th>Motivo</th>
                        <th className="text-end">Costo Perdido</th>
                        <th></th>
                      </tr>
                    </thead>
                    <tbody>
                      {registros.map(r => (
                        <tr key={r.id_merma}>
                          <td>{r.fecha}</td>
                          <td>{r.descripcion} (x{r.cantidad})</td>
                          <td><span className="badge bg-warning text-dark">{r.motivo}</span></td>
                          <td className="text-end fw-bold text-danger">{formatearMoneda(r.costo_perdida)}</td>
                          <td className="text-center">
                            <button className="btn btn-sm btn-outline-danger" onClick={() => handleEliminar(r.id_merma)}>🗑️</button>
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

export default MermaList;