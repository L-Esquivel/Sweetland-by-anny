// src/components/recetas/RecetasList.jsx
import React, { useState, useEffect } from 'react';
import { recetasService } from '../../services/recetasService';
import { productosService } from '../../services/productosService';
import { ingredientesService } from '../../services/ingredientesService';
import RecetaForm from './RecetaForm';
import './RecetasList.css';

const RecetasList = () => {
  const [recetas, setRecetas] = useState([]);
  const [productos, setProductos] = useState([]);
  const [ingredientes, setIngredientes] = useState([]);
  const [productoSeleccionado, setProductoSeleccionado] = useState(null);
  const [recetasProducto, setRecetasProducto] = useState([]);
  const [costoProduccion, setCostoProduccion] = useState(0);
  const [margenBruto, setMargenBruto] = useState(0);
  const [margenPorcentaje, setMargenPorcentaje] = useState(0);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingReceta, setEditingReceta] = useState(null);

  useEffect(() => {
    cargarDatosIniciales();
  }, []);

  const cargarDatosIniciales = async () => {
    try {
      setLoading(true);
      const [recetasData, productosData, ingredientesData] = await Promise.all([
        recetasService.getRecetas(),
        productosService.getProductos(),
        ingredientesService.getIngredientes()
      ]);
      
      setRecetas(recetasData);
      setProductos(productosData);
      setIngredientes(ingredientesData);
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
      
      console.log('📦 Producto seleccionado:', producto);
      const data = await recetasService.getRecetasPorProducto(productoId);
      console.log('📊 Datos recibidos del servicio:', data);
      
      // Verificar estructura de datos recibida
      if (!data) {
        console.warn('⚠️ El servicio retornó null o undefined');
        setRecetasProducto([]);
        setCostoProduccion(0);
        setMargenBruto(0);
        setMargenPorcentaje(0);
        return;
      }

      // Diferentes posibles estructuras de respuesta
      let recetasData = [];
      let costoTotal = 0;
      let margenBrutoCalc = 0;
      let margenPorcentajeCalc = 0;

      // Caso 1: Estructura con propiedad 'costos'
      if (data.costos) {
        console.log('✅ Estructura con propiedad "costos" encontrada');
        recetasData = data.recetas || [];
        costoTotal = data.costos.costo_total_produccion || 0;
        margenBrutoCalc = data.costos.margen_bruto || 0;
        margenPorcentajeCalc = data.costos.margen_porcentaje || 0;
      }
      // Caso 2: Estructura con propiedades directas
      else if (data.recetas !== undefined) {
        console.log('✅ Estructura con propiedades directas');
        recetasData = data.recetas || [];
        costoTotal = data.costo_total_produccion || data.costo_total || 0;
        margenBrutoCalc = data.margen_bruto || 0;
        margenPorcentajeCalc = data.margen_porcentaje || 0;
      }
      // Caso 3: Solo array de recetas - calcular costos manualmente
      else if (Array.isArray(data)) {
        console.log('✅ Solo array de recetas recibido - calculando costos manualmente');
        recetasData = data;
        costoTotal = data.reduce((total, receta) => total + (receta.costo_ingrediente || 0), 0);
      }
      // Caso 4: Estructura desconocida
      else {
        console.warn('❌ Estructura de datos desconocida:', data);
        recetasData = [];
        costoTotal = 0;
      }

      // Calcular márgenes si no se recibieron del servicio
      if (producto && (margenBrutoCalc === 0 || margenPorcentajeCalc === 0)) {
        const precioVenta = producto.precio || 0;
        margenBrutoCalc = precioVenta - costoTotal;
        margenPorcentajeCalc = precioVenta > 0 ? ((margenBrutoCalc / precioVenta) * 100) : 0;
        
        console.log('🧮 Márgenes calculados manualmente:', {
          precioVenta,
          costoTotal,
          margenBrutoCalc,
          margenPorcentajeCalc
        });
      }

      console.log('📈 Valores finales:', {
        recetas: recetasData.length,
        costoTotal,
        margenBrutoCalc,
        margenPorcentajeCalc
      });

      setRecetasProducto(recetasData);
      setCostoProduccion(costoTotal);
      setMargenBruto(margenBrutoCalc);
      setMargenPorcentaje(margenPorcentajeCalc);

    } catch (error) {
      console.error('❌ Error cargando recetas del producto:', error);
      setRecetasProducto([]);
      setCostoProduccion(0);
      setMargenBruto(0);
      setMargenPorcentaje(0);
    }
  };

  const handleSeleccionarProducto = (productoId) => {
    if (productoId) {
      cargarRecetasProducto(productoId);
    } else {
      setProductoSeleccionado(null);
      setRecetasProducto([]);
      setCostoProduccion(0);
      setMargenBruto(0);
      setMargenPorcentaje(0);
    }
  };

  const handleCrearReceta = () => {
    if (!productoSeleccionado) {
      alert('Por favor selecciona un producto primero');
      return;
    }
    setEditingReceta(null);
    setShowModal(true);
  };

  const handleEditarReceta = (receta) => {
    setEditingReceta(receta);
    setShowModal(true);
  };

  const handleEliminarReceta = async (recetaId) => {
    if (window.confirm('¿Estás seguro de eliminar esta receta?')) {
      try {
        await recetasService.deleteReceta(recetaId);
        if (productoSeleccionado) {
          cargarRecetasProducto(productoSeleccionado.id_producto);
        }
        cargarDatosIniciales();
      } catch (error) {
        console.error('Error eliminando receta:', error);
      }
    }
  };

  const handleEliminarTodasRecetas = async () => {
    if (!productoSeleccionado) return;
    
    if (window.confirm(`¿Estás seguro de eliminar TODAS las recetas de ${productoSeleccionado.nombre}?`)) {
      try {
        await recetasService.deleteRecetasProducto(productoSeleccionado.id_producto);
        setRecetasProducto([]);
        setCostoProduccion(0);
        setMargenBruto(0);
        setMargenPorcentaje(0);
        cargarDatosIniciales();
      } catch (error) {
        console.error('Error eliminando recetas:', error);
      }
    }
  };

  const handleSubmitReceta = async (recetaData) => {
    try {
      if (editingReceta) {
        await recetasService.updateReceta(editingReceta.id_receta, recetaData);
      } else {
        await recetasService.createReceta({
          ...recetaData,
          id_producto: productoSeleccionado.id_producto
        });
      }
      
      setShowModal(false);
      if (productoSeleccionado) {
        // Forzar recarga completa de las recetas
        await cargarRecetasProducto(productoSeleccionado.id_producto);
      }
      await cargarDatosIniciales(); // Recargar datos generales
      
    } catch (error) {
      console.error('Error guardando receta:', error);
      throw error;
    }
  };

  const formatearMoneda = (valor) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP'
    }).format(valor);
  };

  const getColorRentabilidad = (porcentaje) => {
    if (porcentaje > 60) return 'bg-success';
    if (porcentaje > 40) return 'bg-warning';
    return 'bg-danger';
  };

  const getTextoRentabilidad = (porcentaje) => {
    if (porcentaje > 60) return '✅ Excelente';
    if (porcentaje > 40) return '⚠️ Buena';
    if (porcentaje > 20) return '📊 Regular';
    return '❌ Baja';
  };

  if (loading) {
    return <div className="text-center p-4">Cargando recetas...</div>;
  }

  return (
    <div className="recetas-container">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2 className="mb-0">📋 Sistema de Recetas</h2>
      </div>

      {/* Selector de Producto */}
      <div className="card mb-4">
        <div className="card-body">
          <h5 className="card-title">Seleccionar Producto</h5>
          <select 
            className="form-select"
            value={productoSeleccionado?.id_producto || ''}
            onChange={(e) => handleSeleccionarProducto(parseInt(e.target.value))}
          >
            <option value="">-- Selecciona un producto --</option>
            {productos.map(producto => (
              <option key={producto.id_producto} value={producto.id_producto}>
                {producto.nombre} - {formatearMoneda(producto.precio)}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Información del Producto Seleccionado con Márgenes */}
      {productoSeleccionado && (
        <div className="card mb-4">
          <div className="card-header bg-primary text-white">
            <h5 className="mb-0">📊 Análisis de Rentabilidad</h5>
          </div>
          <div className="card-body">
            <div className="row">
              <div className="col-md-6">
                <h5>{productoSeleccionado.nombre}</h5>
                <p className="text-muted">{productoSeleccionado.descripcion}</p>
                <div className="mb-3">
                  <strong>Precio de venta:</strong> 
                  <span className="fw-bold text-success ms-2">
                    {formatearMoneda(productoSeleccionado.precio)}
                  </span>
                </div>
              </div>
              <div className="col-md-6">
                <div className="costo-info">
                  <div className="mb-2">
                    <strong>Costo de producción:</strong>
                    <span className="fw-bold text-info ms-2">
                      {formatearMoneda(costoProduccion)}
                    </span>
                  </div>
                  
                  <div className="mb-2">
                    <strong>Margen de ganancia:</strong>
                    <span className={`fw-bold ${margenBruto > 0 ? 'text-success' : 'text-danger'} ms-2`}>
                      {formatearMoneda(margenBruto)} ({margenPorcentaje.toFixed(2)}%)
                    </span>
                  </div>
                  
                  <div className="mb-2">
                    <strong>Rentabilidad:</strong>
                    <span className={`badge ${getColorRentabilidad(margenPorcentaje)} ms-2`}>
                      {getTextoRentabilidad(margenPorcentaje)}
                    </span>
                  </div>

                  {/* Recomendación basada en el margen */}
                  {margenPorcentaje < 30 && (
                    <div className="alert alert-warning mt-2 py-2">
                      <small>
                        💡 <strong>Recomendación:</strong> Considera aumentar el precio para mejorar la rentabilidad
                      </small>
                    </div>
                  )}
                </div>

                <div className="btn-group mt-3">
                  <button className="btn btn-primary btn-sm" onClick={handleCrearReceta}>
                    ➕ Agregar Ingrediente
                  </button>
                  {recetasProducto.length > 0 && (
                    <button className="btn btn-danger btn-sm" onClick={handleEliminarTodasRecetas}>
                      🗑️ Eliminar Todas
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Lista de Recetas del Producto */}
      {productoSeleccionado && (
        <div className="card">
          <div className="card-header">
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
                    {recetasProducto.map(receta => (
                      <tr key={receta.id_receta}>
                        <td className="fw-semibold">{receta.ingrediente}</td>
                        <td>{receta.cantidad_necesaria}</td>
                        <td>
                          <span className="badge bg-secondary">{receta.unidad}</span>
                        </td>
                        <td>{formatearMoneda(receta.costo_unitario)}</td>
                        <td className="fw-bold text-success">
                          {formatearMoneda(receta.costo_ingrediente)}
                        </td>
                        <td className="text-center">
                          <div className="btn-group" role="group">
                            <button 
                              className="btn btn-warning btn-sm me-1"
                              onClick={() => handleEditarReceta(receta)}
                              title="Editar receta"
                            >
                              ✏️
                            </button>
                            <button 
                              className="btn btn-danger btn-sm"
                              onClick={() => handleEliminarReceta(receta.id_receta)}
                              title="Eliminar receta"
                            >
                              🗑️
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                  <tfoot className="table-dark">
                    <tr>
                      <td colSpan="4" className="text-end fw-bold">TOTAL PRODUCCIÓN:</td>
                      <td className="fw-bold text-success">{formatearMoneda(costoProduccion)}</td>
                      <td></td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Modal para crear/editar receta */}
      {showModal && (
        <RecetaForm
          receta={editingReceta}
          producto={productoSeleccionado}
          ingredientes={ingredientes}
          onSubmit={handleSubmitReceta}
          onClose={() => setShowModal(false)}
        />
      )}
    </div>
  );
};

export default RecetasList;