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
  const [isUpdating, setIsUpdating] = useState(false); // Para mostrar feedback visual de carga

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

  // OPTIMIZADO: Llamada única al backend para recalcular y guardar
  const actualizarCampoProducto = async (campo, valor) => {
    if (!productoSeleccionado) return;

    // 1. Actualización instantánea en la UI para que no se sienta lag
    const productoActualizado = { ...productoSeleccionado, [campo]: valor };
    setProductoSeleccionado(productoActualizado);
    setIsUpdating(true);

    try {
      const nuevoPax = campo === 'pax' ? valor : productoActualizado.pax;
      const nuevaUtilidad = campo === 'utilidad_porcentaje' ? valor : productoActualizado.utilidad_porcentaje;

      // 2. Solo llamamos a recalcular. El backend ya hace el UPDATE en la tabla productos.
      const data = await recetasService.recalcularCostos(
        productoSeleccionado.id_producto,
        parseInt(nuevoPax) || 1,
        parseFloat(nuevaUtilidad) || 0
      );

      // 3. Sincronizamos el estado de costos con la respuesta del servidor
      setCostos(data.costos || null);
    } catch (error) {
      console.error('Error al recalcular:', error);
    } finally {
      setIsUpdating(false);
    }
  };

  const handleEliminarReceta = async (id_receta) => {
    if (window.confirm('¿Eliminar este ingrediente?')) {
      try {
        await recetasService.deleteReceta(id_receta);
        cargarRecetasProducto(productoSeleccionado.id_producto);
      } catch (error) { console.error(error); }
    }
  };

  const handleEliminarEmpaque = async (id) => {
    if (window.confirm('¿Eliminar este empaque?')) {
      try {
        await empaquesService.deleteEmpaqueProducto(id); // Asegúrate que el service tenga este nombre
        cargarRecetasProducto(productoSeleccionado.id_producto);
      } catch (error) { console.error(error); }
    }
  };

  const handleCrearReceta = () => {
    if (!productoSeleccionado) return alert('Selecciona un producto primero');
    setShowModal(true);
  };

  const handleSubmitReceta = async (data, isEmpaque = false) => {
    try {
      if (isEmpaque) {
        await empaquesService.addEmpaqueProducto(productoSeleccionado.id_producto, data);
      } else {
        await recetasService.createReceta({ ...data, id_producto: productoSeleccionado.id_producto });
      }
      setShowModal(false);
      cargarRecetasProducto(productoSeleccionado.id_producto);
    } catch (error) { console.error('Error guardando:', error); }
  };

  const formatearMoneda = (valor) => {
    return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(valor || 0);
  };

  if (loading) return <div className="text-center p-5"><h3>Cargando sistema de costeo...</h3></div>;

  return (
    <div className="recetas-container container-fluid p-4">
      <h2 className="mb-4 text-center">📋 Análisis de Costos y Recetas</h2>

      <div className="card shadow-sm mb-4">
        <div className="card-body bg-light">
          <label className="form-label fw-bold">Seleccionar Producto para Costear:</label>
          <select 
            className="form-select form-select-lg"
            value={productoSeleccionado?.id_producto || ''}
            onChange={(e) => {
              const selectedId = e.target.value;
              if (selectedId) {
                cargarRecetasProducto(parseInt(selectedId));
              } else {
                // Si el usuario deselecciona, limpiamos el estado
                setProductoSeleccionado(null);
                setCostos(null);
              }
            }}
          >
            <option value="">-- Seleccione un producto del catálogo --</option>
            {productos.map(p => (
              <option key={p.id_producto} value={p.id_producto}>{p.nombre}</option>
            ))}
          </select>
        </div>
      </div>

      {productoSeleccionado && costos && (
        <div className="row">
          {/* Columna Izquierda: Ajustes */}
          <div className="col-lg-5">
            <div className="card shadow-sm border-0 mb-4">
              <div className="card-header bg-dark text-white">
                <h5 className="mb-0">⚙️ Parámetros de Venta</h5>
              </div>
              <div className="card-body">
                <h4 className="text-primary">{productoSeleccionado.nombre}</h4>
                <hr />
                
                <div className="mb-4">
                  <label className="form-label fw-bold">PAX (Unidades que rinde la receta):</label>
                  <div className="input-group">
                    <span className="input-group-text">📦</span>
                    <input 
                      type="number" 
                      className="form-control form-control-lg" 
                      // 💡 FIX: Se cambia `|| 1` por `?? ''`.
                      // Esto permite que el campo de texto esté momentáneamente vacío
                      // para que el usuario pueda borrar el valor y escribir uno nuevo,
                      // en lugar de forzarlo a ser '1' inmediatamente.
                      value={productoSeleccionado.pax ?? ''}
                      onChange={(e) => actualizarCampoProducto('pax', e.target.value)}
                    />
                  </div>
                  <small className="text-muted">El precio final se dividirá por este número.</small>
                </div>

                <div className="mb-4">
                  <label className="form-label fw-bold">Utilidad Deseada (%):</label>
                  <div className="input-group">
                    <input 
                      type="number"
                      className="form-control form-control-lg"
                      value={productoSeleccionado.utilidad_porcentaje ?? ''}
                      onChange={(e) => actualizarCampoProducto('utilidad_porcentaje', e.target.value)}
                    />
                    <span className="input-group-text">%</span>
                  </div>
                  <small className="text-muted">Porcentaje de ganancia sobre el costo total de producción.</small>
                </div>

                {isUpdating && <div className="text-primary"><span className="spinner-border spinner-border-sm me-2"></span>Recalculando...</div>}
              </div>
            </div>
          </div>

          {/* Columna Derecha: Desglose (Las 8 líneas) */}
          <div className="col-lg-7">
            <div className="card shadow-sm border-0">
              <div className="card-header bg-success text-white">
                <h5 className="mb-0">💰 Desglose Detallado de Precio</h5>
              </div>
              <div className="card-body p-0">
                <table className="table table-hover mb-0">
                  <tbody>
                    <tr>
                      <td className="ps-4">Costo Base (Ingredientes)</td>
                      <td className="text-end pe-4 fw-bold">{formatearMoneda(costos.costo_base)}</td>
                    </tr>
                    <tr className="table-light">
                      <td className="ps-4 text-muted small">+ 35% Gastos Operativos</td>
                      <td className="text-end pe-4">{formatearMoneda(costos.gastos_operativos)}</td>
                    </tr>
                    <tr className="table-light">
                      <td className="ps-4 text-muted small">+ 10% Depreciación Mercado</td>
                      <td className="text-end pe-4">{formatearMoneda(costos.dep_mercado)}</td>
                    </tr>
                    <tr className="table-light border-bottom">
                      <td className="ps-4 text-muted small">+ 5% Depreciación Equipos</td>
                      <td className="text-end pe-4">{formatearMoneda(costos.dep_equipos)}</td>
                    </tr>
                    <tr>
                      <td className="ps-4">+ Valor Total Empaques</td>
                      <td className="text-end pe-4">{formatearMoneda(costos.costo_empaques)}</td>
                    </tr>
                    <tr className="fw-bold bg-light">
                      <td className="ps-4 text-primary">TOTAL ANTES DE UTILIDAD</td>
                      <td className="text-end pe-4 text-primary">{formatearMoneda(costos.total3)}</td>
                    </tr>
                    <tr>
                      <td className="ps-4">{costos.utilidad_porcentaje}% Utilidad Seleccionada</td>
                      <td className="text-end pe-4 text-success">+ {formatearMoneda(costos.utilidad)}</td>
                    </tr>
                    <tr className="fw-bold">
                      <td className="ps-4">TOTAL CON UTILIDAD</td>
                      <td className="text-end pe-4">{formatearMoneda(costos.total4)}</td>
                    </tr>
                    <tr>
                      <td className="ps-4">8% Impuesto al Consumo (I.C.)</td>
                      <td className="text-end pe-4">{formatearMoneda(costos.ic)}</td>
                    </tr>
                    <tr className="table-dark">
                      <td className="ps-4 fs-5 py-3 fw-bold">PRECIO SUGERIDO FINAL (por unidad)</td>
                      <td className="text-end pe-4 fs-5 py-3 fw-bold text-warning">{formatearMoneda(costos.precio_sugerido)}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div className="card-footer text-center bg-white border-0 py-3">
                <button className="btn btn-outline-primary btn-lg" onClick={handleCrearReceta}>
                  ➕ Agregar Ingrediente o Empaque
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tablas Detalladas (Ingredientes / Empaques) abajo para orden */}
      {productoSeleccionado && (
        <div className="row mt-4">
            <div className="col-md-6">
                <div className="card shadow-sm">
                    <div className="card-header bg-secondary text-white">Ingredientes</div>
                    <div className="table-responsive">
                        <table className="table table-sm mb-0">
                            <thead><tr><th>Item</th><th>Cant.</th><th>Subtotal</th><th></th></tr></thead>
                            <tbody>
                                {recetasProducto.map((r) => (
                                    // FIX: Usar el ID único del registro como key y para la función de borrado.
                                    // El backend envía 'id', no 'id_receta'.
                                    <tr key={r.id}>
                                        <td>{r.ingrediente}</td>
                                        <td>{r.cantidad_necesaria} {r.unidad}</td>
                                        <td className="fw-bold">{formatearMoneda(r.costo_ingrediente)}</td>
                                        <td><button className="btn btn-link btn-sm text-danger" onClick={() => handleEliminarReceta(r.id)}>🗑️</button></td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            <div className="col-md-6">
                <div className="card shadow-sm">
                    <div className="card-header bg-secondary text-white">Empaques</div>
                    <div className="table-responsive">
                        <table className="table table-sm mb-0">
                            <thead><tr><th>Item</th><th>Cant.</th><th>Subtotal</th><th></th></tr></thead>
                            <tbody>
                                {empaquesProducto.map((e, i) => (
                                    <tr key={i}>
                                        <td>{e.nombre}</td>
                                        <td>{e.cantidad}</td>
                                        <td className="fw-bold">{formatearMoneda(e.subtotal)}</td>
                                        <td><button className="btn btn-link btn-sm text-danger" onClick={() => handleEliminarEmpaque(e.id)}>🗑️</button></td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
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