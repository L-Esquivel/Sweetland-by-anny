import React, { useState, useEffect } from 'react';
import { pedidosService } from '../../services/pedidosService';

const PedidoForm = ({ productos, onSubmit, onClose, titulo = "➕ Nuevo Pedido" }) => {
  const [formData, setFormData] = useState({
    cliente_email: '',
    cliente_telefono: '',
    cliente_nombre: '',
    direccion: '',
    detalles: []
  });
  
  const [productoSeleccionado, setProductoSeleccionado] = useState('');
  const [cantidad, setCantidad] = useState(1);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [verificandoUsuario, setVerificandoUsuario] = useState(false);
  const [usuarioEncontrado, setUsuarioEncontrado] = useState(null);
  const [usuarios, setUsuarios] = useState([]);
  const [cargandoUsuarios, setCargandoUsuarios] = useState(true);
  const [credencialesUsuario, setCredencialesUsuario] = useState(null);

  // Cargar usuarios REALES de la base de datos
  useEffect(() => {
    const cargarUsuariosReales = async () => {
      try {
        console.log('🔄 Cargando usuarios reales...');
        setCargandoUsuarios(true);
        const usuariosReales = await pedidosService.getUsuarios();
        console.log('✅ Usuarios cargados de la BD:', usuariosReales);
        setUsuarios(usuariosReales);
      } catch (error) {
        console.error('❌ Error cargando usuarios:', error);
        setError('Error al cargar la lista de clientes');
        setUsuarios([]);
      } finally {
        setCargandoUsuarios(false);
      }
    };

    cargarUsuariosReales();
  }, []);

  // Verificar usuario cuando cambia email o teléfono
  useEffect(() => {
    const verificarUsuario = () => {
      const email = formData.cliente_email.trim();
      const telefono = formData.cliente_telefono.trim();
      
      if (!email && !telefono) {
        setUsuarioEncontrado(null);
        return;
      }

      if (cargandoUsuarios) {
        console.log('⏳ Esperando a que carguen los usuarios...');
        return;
      }

      if (usuarios.length === 0) {
        console.log('📭 No hay usuarios cargados para buscar');
        setUsuarioEncontrado(null);
        return;
      }

      setVerificandoUsuario(true);
      
      console.log('🔍 Buscando usuario con:', { email, telefono });
      console.log('📋 Buscando en', usuarios.length, 'usuarios:', usuarios);

      // Búsqueda en usuarios REALES de la BD
      const usuarioExistente = usuarios.find(usuario => {
        const usuarioEmail = usuario.email ? usuario.email.toLowerCase().trim() : '';
        const inputEmail = email ? email.toLowerCase().trim() : '';
        
        const usuarioTel = usuario.telefono ? usuario.telefono.replace(/\D/g, '') : '';
        const inputTel = telefono ? telefono.replace(/\D/g, '') : '';
        
        const emailMatch = inputEmail && usuarioEmail === inputEmail;
        const telefonoMatch = inputTel && usuarioTel === inputTel && inputTel.length > 5;
        
        console.log(`Comparando: ${usuario.nombre}`, {
          emailMatch, 
          telefonoMatch,
          usuarioEmail, 
          inputEmail, 
          usuarioTel, 
          inputTel
        });
        
        return emailMatch || telefonoMatch;
      });
      
      setTimeout(() => {
        if (usuarioExistente) {
          console.log('✅ USUARIO ENCONTRADO:', usuarioExistente);
          setUsuarioEncontrado(usuarioExistente);
          setFormData(prev => ({
            ...prev,
            cliente_nombre: usuarioExistente.nombre,
            direccion: usuarioExistente.direccion || prev.direccion
          }));
        } else {
          console.log('❌ Usuario no encontrado - será nuevo cliente');
          setUsuarioEncontrado(null);
        }
        setVerificandoUsuario(false);
      }, 500);
    };

    const timeoutId = setTimeout(verificarUsuario, 600);
    return () => clearTimeout(timeoutId);
  }, [formData.cliente_email, formData.cliente_telefono, usuarios, cargandoUsuarios]);

  const agregarProducto = () => {
    if (!productoSeleccionado || cantidad < 1) {
      setError('Selecciona un producto y cantidad válida');
      return;
    }

    const producto = productos.find(p => p.id_producto === parseInt(productoSeleccionado));
    if (!producto) {
      setError('Producto no encontrado');
      return;
    }

    const subtotal = producto.precio * cantidad;
    const nuevoDetalle = {
      producto_id: producto.id_producto,
      producto_nombre: producto.nombre,
      cantidad: cantidad,
      precio_unitario: producto.precio,
      subtotal: subtotal
    };

    setFormData(prev => ({
      ...prev,
      detalles: [...prev.detalles, nuevoDetalle]
    }));

    setProductoSeleccionado('');
    setCantidad(1);
    setError('');
  };

  const eliminarProducto = (index) => {
    setFormData(prev => ({
      ...prev,
      detalles: prev.detalles.filter((_, i) => i !== index)
    }));
  };

  const calcularTotal = () => {
    return formData.detalles.reduce((total, detalle) => total + detalle.subtotal, 0);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (!formData.cliente_email && !formData.cliente_telefono) {
        throw new Error('Debe ingresar al menos email o teléfono');
      }

      if (!formData.cliente_nombre) {
        throw new Error('El nombre del cliente es obligatorio');
      }

      if (!formData.direccion) {
        throw new Error('La dirección de entrega es obligatoria');
      }

      if (formData.detalles.length === 0) {
        throw new Error('Debe agregar al menos un producto al pedido');
      }

      let usuarioId;
      let nuevoUsuarioCreado = false;

      // Lógica para usuario existente o nuevo
      if (usuarioEncontrado) {
        // Usar usuario existente
        usuarioId = usuarioEncontrado.id_usuario;
        console.log('✅ Usando usuario existente:', usuarioEncontrado.nombre);
      } else {
        // Crear nuevo usuario
        console.log('🆕 Creando nuevo usuario...');
        const nuevoUsuarioData = {
          nombre: formData.cliente_nombre,
          email: formData.cliente_email || null,
          telefono: formData.cliente_telefono || '',
          direccion: formData.direccion
        };

        const nuevoUsuario = await pedidosService.createUsuario(nuevoUsuarioData);
        usuarioId = nuevoUsuario.id_usuario;
        nuevoUsuarioCreado = true;
        
        // ✅ MOSTRAR CONTRASEÑA TEMPORAL
        console.log('✅ Nuevo usuario creado:', nuevoUsuario);
        setCredencialesUsuario({
          email: nuevoUsuario.email,
          password: nuevoUsuario.password_temporal,
          nombre: nuevoUsuario.nombre
        });
        
        // ACTUALIZAR LA LISTA DE USUARIOS después de crear uno nuevo
        const usuariosActualizados = await pedidosService.getUsuarios();
        setUsuarios(usuariosActualizados);
        console.log('🔄 Lista de usuarios actualizada');
      }

      // Crear el pedido
      const pedidoData = {
        usuario_id: usuarioId,
        telefono: formData.cliente_telefono,
        direccion: formData.direccion,
        total: calcularTotal()
      };

      console.log('📤 Creando pedido con datos:', pedidoData);
      const pedidoCreado = await pedidosService.createPedido(pedidoData);

      // ✅ AGREGAR ESTOS LOGS DE DEBUG (CORREGIDO)
      console.log('🔍 Respuesta completa de createPedido:', pedidoCreado);
      console.log('🔍 Todas las claves del objeto:', Object.keys(pedidoCreado));
      const pedidoId = pedidoCreado.id_pedido;
      console.log('✅ Pedido creado con ID:', pedidoId);
      console.log('🔍 Tipo de ID:', typeof pedidoId);

      // ✅ CREAR LOS DETALLES DEL PEDIDO (PRODUCTOS)
      console.log(`📝 Creando ${formData.detalles.length} detalles del pedido...`);
      
      for (const detalle of formData.detalles) {
        try {
          await pedidosService.createDetallePedidoAlternativo(pedidoId, {
            producto_id: detalle.producto_id,
            cantidad: detalle.cantidad,
            subtotal: detalle.subtotal
          });
          console.log(`✅ Detalle creado: ${detalle.producto_nombre} x${detalle.cantidad}`);
        } catch (detalleError) {
          console.error(`❌ Error creando detalle para ${detalle.producto_nombre}:`, detalleError);
          throw new Error(`Error al agregar producto ${detalle.producto_nombre}`);
        }
      }

      console.log('🎉 Pedido completado exitosamente!');
      onClose();
      
    } catch (error) {
      console.error('❌ Error creando pedido:', error);
      setError('Error al crear el pedido: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // Agregar indicador de carga de usuarios
  if (cargandoUsuarios) {
    return (
      <div className="modal fade show d-block" style={{backgroundColor: 'rgba(0,0,0,0.5)'}}>
        <div className="modal-dialog">
          <div className="modal-content">
            <div className="modal-body text-center py-4">
              <div className="spinner-border text-primary" role="status">
                <span className="visually-hidden">Cargando...</span>
              </div>
              <p className="mt-2">Cargando lista de clientes...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="modal fade show d-block" style={{backgroundColor: 'rgba(0,0,0,0.5)'}}>
      <div className="modal-dialog modal-xl" style={{maxWidth: '95%', height: '95vh'}}>
        <div className="modal-content h-100">
          <div className="modal-header bg-success text-white">
            <h5 className="modal-title">{titulo}</h5>
            <button type="button" className="btn-close" onClick={onClose}></button>
          </div>
          <form onSubmit={handleSubmit}>
            <div className="modal-body" style={{overflowY: 'auto', maxHeight: 'calc(95vh - 120px)'}}>
              {error && <div className="alert alert-danger">{error}</div>}

              {/* Sección de Información del Cliente */}
              <div className="card mb-3">
                <div className="card-header bg-light">
                  <h6 className="mb-0">👤 Información del Cliente</h6>
                  <small className="text-muted">Base de datos: {usuarios.length} clientes</small>
                </div>
                <div className="card-body">
                  <div className="row mb-3">
                    <div className="col-md-6">
                      <label className="form-label">Email</label>
                      <input
                        type="email"
                        className="form-control"
                        placeholder="correo@ejemplo.com"
                        value={formData.cliente_email}
                        onChange={(e) => setFormData(prev => ({...prev, cliente_email: e.target.value}))}
                      />
                    </div>
                    <div className="col-md-6">
                      <label className="form-label">Teléfono</label>
                      <input
                        type="text"
                        className="form-control"
                        placeholder="3001234567"
                        value={formData.cliente_telefono}
                        onChange={(e) => setFormData(prev => ({...prev, cliente_telefono: e.target.value}))}
                      />
                    </div>
                  </div>

                  {verificandoUsuario && (
                    <div className="alert alert-info py-2">
                      <small>🔍 Buscando en {usuarios.length} clientes...</small>
                    </div>
                  )}

                  {usuarioEncontrado && (
                    <div className="alert alert-success py-2">
                      <small>✅ Cliente encontrado: <strong>{usuarioEncontrado.nombre}</strong></small>
                    </div>
                  )}

                  {!usuarioEncontrado && (formData.cliente_email || formData.cliente_telefono) && !verificandoUsuario && (
                    <div className="alert alert-warning py-2">
                      <small>🆕 Cliente nuevo - Complete los datos</small>
                    </div>
                  )}

                  <div className="row">
                    <div className="col-md-6">
                      <label className="form-label">Nombre Completo *</label>
                      <input
                        type="text"
                        className="form-control"
                        value={formData.cliente_nombre}
                        onChange={(e) => setFormData(prev => ({...prev, cliente_nombre: e.target.value}))}
                        required
                      />
                    </div>
                    <div className="col-md-6">
                      <label className="form-label">Dirección de Entrega *</label>
                      <input
                        type="text"
                        className="form-control"
                        placeholder="Dirección completa"
                        value={formData.direccion}
                        onChange={(e) => setFormData(prev => ({...prev, direccion: e.target.value}))}
                        required
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Sección de Productos */}
              <div className="card mb-3">
                <div className="card-header bg-light">
                  <h6 className="mb-0">🛒 Agregar Productos</h6>
                </div>
                <div className="card-body">
                  <div className="row g-2">
                    <div className="col-md-6">
                      <select
                        className="form-select"
                        value={productoSeleccionado}
                        onChange={(e) => setProductoSeleccionado(e.target.value)}
                      >
                        <option value="">Seleccionar producto...</option>
                        {productos.map(producto => (
                          <option key={producto.id_producto} value={producto.id_producto}>
                            {producto.nombre} - ${producto.precio.toLocaleString()}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div className="col-md-3">
                      <input
                        type="number"
                        className="form-control"
                        min="1"
                        value={cantidad}
                        onChange={(e) => setCantidad(parseInt(e.target.value) || 1)}
                      />
                    </div>
                    <div className="col-md-3">
                      <button
                        type="button"
                        className="btn btn-primary w-100"
                        onClick={agregarProducto}
                      >
                        ➕ Agregar
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              {/* Lista de Productos */}
              {formData.detalles.length > 0 && (
                <div className="table-responsive">
                  <table className="table table-sm">
                    <thead className="table-dark">
                      <tr>
                        <th>Producto</th>
                        <th>Cantidad</th>
                        <th>Precio Unitario</th>
                        <th>Subtotal</th>
                        <th>Acciones</th>
                      </tr>
                    </thead>
                    <tbody>
                      {formData.detalles.map((detalle, index) => (
                        <tr key={index}>
                          <td>{detalle.producto_nombre}</td>
                          <td>{detalle.cantidad}</td>
                          <td>${detalle.precio_unitario.toLocaleString()}</td>
                          <td>${detalle.subtotal.toLocaleString()}</td>
                          <td>
                            <button
                              type="button"
                              className="btn btn-danger btn-sm"
                              onClick={() => eliminarProducto(index)}
                            >
                              🗑️
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                    <tfoot>
                      <tr>
                        <td colSpan="3" className="text-end fw-bold">Total:</td>
                        <td className="fw-bold text-success">${calcularTotal().toLocaleString()}</td>
                        <td></td>
                      </tr>
                    </tfoot>
                  </table>
                </div>
              )}
            </div>
            <div className="modal-footer">
              <button type="button" className="btn btn-secondary" onClick={onClose}>
                Cancelar
              </button>
              <button 
                type="submit" 
                className="btn btn-success"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                    Creando...
                  </>
                ) : (
                  '✅ Crear Pedido'
                )}
              </button>
            </div>
          </form>

          {/* Modal de Credenciales - AGREGADO */}
          {credencialesUsuario && (
            <div className="modal fade show d-block" style={{backgroundColor: 'rgba(0,0,0,0.7)', position: 'fixed', top: '0', left: '0', zIndex: 9999}}>
              <div className="modal-dialog">
                <div className="modal-content">
                  <div className="modal-header bg-info text-white">
                    <h5 className="modal-title">🔐 Credenciales del Nuevo Usuario</h5>
                  </div>
                  <div className="modal-body">
                    <div className="alert alert-info">
                      <strong>Usuario creado exitosamente!</strong>
                      <br/>Comparte estas credenciales con el cliente.
                    </div>
                    
                    <div className="mb-3">
                      <label className="form-label fw-bold">👤 Nombre:</label>
                      <input type="text" className="form-control" value={credencialesUsuario.nombre} readOnly />
                    </div>
                    
                    <div className="mb-3">
                      <label className="form-label fw-bold">📧 Email:</label>
                      <input type="text" className="form-control" value={credencialesUsuario.email} readOnly />
                    </div>
                    
                    <div className="mb-3">
                      <label className="form-label fw-bold">🔑 Contraseña Temporal:</label>
                      <input type="text" className="form-control fw-bold text-success" value={credencialesUsuario.password} readOnly />
                    </div>
                    
                    <div className="alert alert-warning">
                      <small>⚠️ <strong>Importante:</strong> El cliente debe cambiar su contraseña en el primer inicio de sesión.</small>
                    </div>
                  </div>
                  <div className="modal-footer">
                    <button 
                      type="button" 
                      className="btn btn-primary"
                      onClick={() => {
                        // Copiar al portapapeles
                        navigator.clipboard.writeText(`Email: ${credencialesUsuario.email}\nContraseña: ${credencialesUsuario.password}`);
                        alert('Credenciales copiadas al portapapeles!');
                        setCredencialesUsuario(null);
                      }}
                    >
                      📋 Copiar Credenciales
                    </button>
                    <button 
                      type="button" 
                      className="btn btn-secondary"
                      onClick={() => setCredencialesUsuario(null)}
                    >
                      Cerrar
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PedidoForm;