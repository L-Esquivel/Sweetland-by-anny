// src/components/recetas/RecetasList.jsx
import React, { useState, useEffect } from 'react';
import { recetasService } from '../../services/recetasService';
import { productosService } from '../../services/productosService';
import { ingredientesService } from '../../services/ingredientesService';
import { empaquesService } from '../../services/empaquesService';
import RecetaForm from './RecetaForm';
import './RecetasList.css';

const RecetasList = () => {
  const [productos, setProductos] = useState([]);
  const [ingredientes, setIngredientes] = useState([]);
  const [empaques, setEmpaques] = useState([]);
  const [productoSeleccionado, setProductoSeleccionado] = useState(null);
  const [recetasProducto, setRecetasProducto] = useState([]);
  const [empaquesProducto, setEmpaquesProducto] = useState([]);
  const [costos, setCostos] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    cargarDatosIniciales();
  }, []);

  const cargarDatosIniciales = async () => {
    try {
      setLoading(true);
      const [productosData, ingredientesData, empaquesData] = await Promise.all([
        productosService.getProductos(),
        ingredientesService.getIngredientes(),
        empaquesService.getEmpaques()
      ]);
      setProductos(productosData);
      setIngredientes(ingredientesData);
      setEmpaques(empaquesData);
    } catch (error) {
      console.error('Error cargando datos:', error);
    } finally {
      setLoading(false);
    }
  };

  const cargarRecetasProducto = async (productoId) => {
    try {
      const producto = productos.find(p => p.id_producto === productoId);
      setProductoSeleccionado(producto);

      const data = await recetasService.getRecetasPorProducto(productoId);
      setRecetasProducto(data.recetas || []);
      setEmpaquesProducto(data.empaques || []);
      setCostos(data.costos || null);
    } catch (error) {
      console.error('Error cargando recetas:', error);
    }
  };

  const actualizarCampoProducto = async (campo, valor) => {
    if (!productoSeleccionado) return;

    const productoActualizado = { ...productoSeleccionado, [campo]: valor };
    setProductoSeleccionado(productoActualizado);

    try {
      await productosService.updateProducto(productoSeleccionado.id_producto, productoActualizado);
      // Refrescamos los costos después de actualizar pax o utilidad
      const data = await recetasService.getRecetasPorProducto(productoSeleccionado.id_producto);
      setCostos(data.costos || null);
    } catch (error) {
      console.error('Error actualizando:', error);
    }
  };

  const handleEliminarReceta = async (id_receta) => {
    if (window.confirm('¿Eliminar este ingrediente?')) {
      try {
        await recetasService.deleteReceta(id_receta);
        cargarRecetasProducto(productoSeleccionado.id_producto);
      } catch (error) {
        console.error(error);
      }
    }
  };

  const handleEliminarEmpaque = async (id) => {
    if (window.confirm('¿Eliminar este empaque?')) {
      try {
        await empaquesService.deleteEmpaque(id);
        cargarRecetasProducto(productoSeleccionado.id_producto);
      } catch (error) {
        console.error(error);
      }
    }
  };

  const handleCrearReceta = () => {
    if (!productoSeleccionado) {
      alert('Selecciona un producto primero');
      return;
    }
    setShowModal(true);
  };

  const handleSubmitReceta = async (data, isEmpaque = false) => {
    try {
      if (isEmpaque) {
        await empaquesService.addEmpaque(productoSeleccionado.id_producto, data);
      } else {
        await recetasService.createReceta({ ...data, id_producto: productoSeleccionado.id_producto });
      }
      setShowModal(false);
      cargarRecetasProducto(productoSeleccionado.id_producto);
    } catch (error) {
      console.error('Error guardando:', error);
    }
  };

  const formatearMoneda = (valor) => {
    return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP' }).format(valor || 0);
  };

  if (loading) return <div className="text-center p-4">Cargando...</div>;

  return (
    <div className="recetas-container">
      <h2 className="mb-4">📋 Sistema de Recetas</h2>

      <div className="card mb-4">
        <div className="card-body">
          <select 
            className="form-select"
            value={productoSeleccionado?.id_producto || ''}
            onChange={(e) => cargarRecetasProducto(parseInt(e.target.value))}
          >
            <option value="">-- Selecciona un producto --</option>
            {productos.map(p => (
              <option key={p.id_producto} value={p.id_producto}>
                {p.nombre} - {formatearMoneda(p.precio)}
              </option>
            ))}
          </select>
        </div>
      </div>

      {productoSeleccionado && costos && (
        <div className="card mb-4">
          <div className="card-header bg-primary text-white">
            <h5 className="mb-0">📊 Análisis de Rentabilidad</h5>
          </div>
          <div className="card-body">
            <div className="row">
              <div className="col-md-7">
                <h5>{productoSeleccionado.nombre}</h5>
                <p className="text-muted">{productoSeleccionado.descripcion}</p>
                <div className="mb-3">
                  <strong>Precio de venta:</strong> 
                  <span className="fw-bold text-success ms-2">{formatearMoneda(productoSeleccionado.precio)}</span>
                </div>

                <div className="mb-3">
                  <strong>PAX (unidades que rinde):</strong>
                  <input 
                    type="number" 
                    className="form-control d-inline-block ms-2" 
                    style={{width: '100px'}}
                    value={productoSeleccionado.pax || 1}
                    onChange={(e) => actualizarCampoProducto('pax', parseInt(e.target.value) || 1)}
                  />
                </div>

                <div className="mb-3">
                  <strong>Utilidad deseada (%):</strong>
                  <input 
                    type="number" 
                    className="form-control d-inline-block ms-2" 
                    style={{width: '100px'}}
                    value={productoSeleccionado.utilidad_porcentaje || 40}
                    onChange={(e) => actualizarCampoProducto('utilidad_porcentaje', parseFloat(e.target.value) || 40)}
                  />
                </div>
              </div>

              <div className="col-md-5">
                <div className="bg-light p-3 rounded">
                  <h6 className="text-center mb-3">Desglose según Excel</h6>

                  {/* === DESGLOSE CORREGIDO SEGÚN TUS AJUSTES === */}
                  <div className="d-flex justify-content-between mb-1">
                    <span>Costo Base</span>
                    <strong>{formatearMoneda(costos.costo_base)}</strong>
                  </div>
                  <div className="d-flex justify-content-between mb-1">
                    <span>+ 35% Gastos Operativos</span>
                    <strong>{formatearMoneda(costos.gastos_operativos)}</strong>
                  </div>
                  <div className="d-flex justify-content-between mb-1">
                    <span>+ 5% Depreciación Equipos</span>
                    <strong>{formatearMoneda(costos.dep_equipos)}</strong>
                  </div>
                  <div className="d-flex justify-content-between mb-1">
                    <span>+ 10% Depreciación Mercado</span>
                    <strong>{formatearMoneda(costos.dep_mercado)}</strong>
                  </div>
                  <div className="d-flex justify-content-between mb-1">
                    <span>+ Empaques</span>
                    <strong>{formatearMoneda(costos.costo_empaques)}</strong>
                  </div>

                  <hr />
                  <div className="d-flex justify-content-between mb-1">
                    <strong>Total antes de Utilidad</strong>
                    <strong>{formatearMoneda(costos.total3)}</strong>
                  </div>

                  <div className="d-flex justify-content-between mb-1">
                    <span>+ {costos.utilidad_porcentaje}% Utilidad</span>
                    <strong>{formatearMoneda(costos.utilidad)}</strong>
                  </div>

                  <hr />
                  <div className="d-flex justify-content-between mb-1">
                    <strong>Total con Utilidad</strong>
                    <strong>{formatearMoneda(costos.total4)}</strong>
                  </div>

                  <div className="d-flex justify-content-between mb-1">
                    <span>+ 8% I.C.</span>
                    <strong>{formatearMoneda(costos.ic)}</strong>
                  </div>

                  <hr className="border-primary" />
                  <div className="d-flex justify-content-between fs-5">
                    <strong>Precio Sugerido Final</strong>
                    <strong className="text-success">{formatearMoneda(costos.precio_sugerido)}</strong>
                  </div>
                  <small className="text-muted d-block text-end">
                    por unidad (PAX = {costos.pax})
                  </small>
                </div>
              </div>
            </div>

            <div className="text-center mt-4">
              <button className="btn btn-primary" onClick={handleCrearReceta}>
                ➕ Agregar Ingrediente o Empaque
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Tablas de Ingredientes y Empaques */}
      {productoSeleccionado && (
        <>
          <div className="card mb-4">
            <div className="card-header bg-primary text-white">
              <h5 className="mb-0">📝 Ingredientes de la Receta</h5>
            </div>
            <div className="card-body p-0">
              {recetasProducto.length === 0 ? (
                <div className="text-center text-muted py-4">
                  <p>No hay ingredientes en esta receta</p>
                  <button className="btn btn-primary btn-sm" onClick={handleCrearReceta}>
                    ➕ Agregar primer ingrediente
                  </button>
                </div>
              ) : (
                <div className="table-responsive">
                  <table className="table table-striped table-hover mb-0">
                    <thead className="table-dark">
                      <tr>
                        <th>Ingrediente</th>
                        <th>Cantidad</th>
                        <th>Unidad</th>
                        <th>Costo Unitario</th>
                        <th>Costo Total</th>
                        <th className="text-center">Acciones</th>
                      </tr>
                    </thead>
                    <tbody>
                      {recetasProducto.map((receta, index) => (
                        <tr key={index}>
                          <td className="fw-semibold">{receta.ingrediente || 'Sin nombre'}</td>
                          <td>{receta.cantidad_necesaria}</td>
                          <td><span className="badge bg-secondary">{receta.unidad}</span></td>
                          <td>{formatearMoneda(receta.costo_unitario)}</td>
                          <td className="fw-bold text-success">{formatearMoneda(receta.costo_ingrediente)}</td>
                          <td className="text-center">
                            <button className="btn btn-danger btn-sm" onClick={() => handleEliminarReceta(receta.id_receta)}>
                              🗑️
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>

          <div className="card">
            <div className="card-header bg-primary text-white">
              <h5 className="mb-0">📦 Empaques de la Receta</h5>
            </div>
            <div className="card-body p-0">
              {empaquesProducto.length === 0 ? (
                <div className="text-center text-muted py-4">
                  <p>No hay empaques configurados para este producto</p>
                </div>
              ) : (
                <div className="table-responsive">
                  <table className="table table-striped table-hover mb-0">
                    <thead className="table-dark">
                      <tr>
                        <th>Empaque</th>
                        <th>Cantidad</th>
                        <th>Precio Unitario</th>
                        <th>Subtotal</th>
                        <th className="text-center">Acciones</th>
                      </tr>
                    </thead>
                    <tbody>
                      {empaquesProducto.map((e, index) => (
                        <tr key={index}>
                          <td className="fw-semibold">{e.nombre || 'Sin nombre'}</td>
                          <td>{e.cantidad}</td>
                          <td>{formatearMoneda(e.precio)}</td>
                          <td className="fw-bold text-success">{formatearMoneda(e.subtotal)}</td>
                          <td className="text-center">
                            <button className="btn btn-danger btn-sm" onClick={() => handleEliminarEmpaque(e.id)}>
                              🗑️
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </>
      )}

      {showModal && (
        <RecetaForm
          producto={productoSeleccionado}
          ingredientes={ingredientes}
          empaques={empaques}
          onSubmit={handleSubmitReceta}
          onClose={() => setShowModal(false)}
        />
      )}
    </div>
  );
};

export default RecetasList;