import React, { useState, useEffect } from 'react';
import { pedidosService } from '../../services/pedidosService';
import { usuariosService } from '../../services/usuariosService';

const PedidoForm = ({ productos, onSubmit, onClose, titulo = "➕ New Order" }) => {
  const [formData, setFormData] = useState({
    customer_email: '',
    customer_phone: '',
    customer_name: '',
    address: '',
    details: []
  });
  
  const [selectedProduct, setSelectedProduct] = useState('');
  const [quantity, setQuantity] = useState(1);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [isCheckingUser, setIsCheckingUser] = useState(false);
  const [foundUser, setFoundUser] = useState(null);
  const [users, setUsers] = useState([]);
  const [isLoadingUsers, setIsLoadingUsers] = useState(true);
  const [newUserCredentials, setNewUserCredentials] = useState(null);

  // Load REAL users from the database
  useEffect(() => {
    const fetchRealUsers = async () => {
      try {
        console.log('🔄 Loading real users...');
        setIsLoadingUsers(true);
        const usuariosReales = await usuariosService.getUsuarios();
        console.log('✅ Users loaded from DB:', usuariosReales);
        setUsers(usuariosReales);
      } catch (error) {
        console.error('❌ Error loading users:', error);
        setError('Error loading customer list');
        setUsers([]);
      } finally {
        setIsLoadingUsers(false);
      }
    };

    fetchRealUsers();
  }, []);

  // Check user when email or phone changes
  useEffect(() => {
    const checkUser = () => {
      const email = formData.customer_email.trim();
      const phone = formData.customer_phone.trim();
      
      if (!email && !phone) {
        setFoundUser(null);
        return;
      }

      if (isLoadingUsers) {
        console.log('⏳ Waiting for users to load...');
        return;
      }

      if (users.length === 0) {
        console.log('📭 No users loaded to search');
        setFoundUser(null);
        return;
      }

      setIsCheckingUser(true);
      
      console.log('🔍 Searching for user with:', { email, phone });
      console.log('📋 Searching in', users.length, 'users:', users);

      const existingUser = users.find(user => {
        const usuarioEmail = usuario.email ? usuario.email.toLowerCase().trim() : '';
        const inputEmail = email ? email.toLowerCase().trim() : '';
        
        const usuarioTel = usuario.telefono ? usuario.telefono.replace(/\D/g, '') : '';
        const inputTel = phone ? phone.replace(/\D/g, '') : '';
        
        const emailMatch = inputEmail && usuarioEmail === inputEmail;
        const telefonoMatch = inputTel && usuarioTel === inputTel && inputTel.length > 5;
        
        return emailMatch || telefonoMatch;
      });
      
      setTimeout(() => {
        if (existingUser) {
          console.log('✅ USER FOUND:', existingUser);
          setFoundUser(existingUser);
          setFormData(prev => ({
            ...prev,
            customer_name: existingUser.nombre,
            address: existingUser.address || prev.address
          }));
        } else {
          console.log('❌ User not found - will be a new customer');
          setFoundUser(null);
        }
        setIsCheckingUser(false);
      }, 500);
    };

    const timeoutId = setTimeout(checkUser, 600);
    return () => clearTimeout(timeoutId);
  }, [formData.customer_email, formData.customer_phone, users, isLoadingUsers]);

  const addProduct = () => {
    if (!selectedProduct || quantity < 1) {
      setError('Select a valid product and quantity');
      return;
    }

    const product = productos.find(p => p.id_producto === parseInt(selectedProduct));
    if (!product) {
      setError('Product not found');
      return;
    }

    const subtotal = product.precio * quantity;
    const newDetail = {
      producto_id: product.id_producto,
      producto_nombre: product.nombre,
      cantidad: quantity,
      precio_unitario: product.precio,
      subtotal: subtotal
    };

    setFormData(prev => ({
      ...prev,
      details: [...prev.details, newDetail]
    }));

    setSelectedProduct('');
    setQuantity(1);
    setError('');
  };

  const removeProduct = (index) => {
    setFormData(prev => ({
      ...prev,
      details: prev.details.filter((_, i) => i !== index)
    }));
  };

  const calculateTotal = () => {
    return formData.details.reduce((total, detail) => total + detail.subtotal, 0);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (!formData.customer_email && !formData.customer_phone) {
        throw new Error('You must enter at least an email or a phone number');
      }

      if (!formData.customer_name) {
        throw new Error('Customer name is required');
      }

      if (!formData.address) {
        throw new Error('Delivery address is required');
      }

      if (formData.details.length === 0) {
        throw new Error('You must add at least one product to the order');
      }

      let userId;
      let isNewUserCreated = false;

      if (foundUser) {
        userId = foundUser.id_usuario;
        console.log('✅ Using existing user:', foundUser.nombre);
      } else {
        console.log('🆕 Creating new user...');
        const newUserData = {
          nombre: formData.customer_name,
          email: formData.customer_email || null,
          telefono: formData.customer_phone || '',
          direccion: formData.address
        };

        const newUser = await usuariosService.createUsuario(newUserData);
        userId = newUser.id_usuario;
        isNewUserCreated = true;
        
        console.log('✅ New user created:', newUser);
        setNewUserCredentials({
          email: newUser.email,
          password: newUser.password_temporal,
          nombre: newUser.nombre
        });
        
        const updatedUsers = await usuariosService.getUsuarios();
        setUsers(updatedUsers);
      }

      // Build the payload for the order creation endpoint
      const items = formData.details.map(d => ({
        producto_id: d.producto_id,
        cantidad: d.cantidad
      }));

      const orderData = {
        usuario_id: userId,
        telefono: formData.customer_phone,
        direccion: formData.address,
        items: items
      };

      console.log('📦 Sending order data to backend:', orderData);
      await pedidosService.createPedido(orderData);

      console.log('🎉 Order completed successfully!');
      onClose();
      
    } catch (error) {
      console.error('❌ Error creating order:', error);
      setError('Error creating order: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  if (isLoadingUsers) {
    return (
      <div className="modal fade show d-block" style={{backgroundColor: 'rgba(0,0,0,0.5)'}}>
        <div className="modal-dialog">
          <div className="modal-content">
            <div className="modal-body text-center py-4">
              <div className="spinner-border text-primary" role="status">
                <span className="visually-hidden">Loading...</span>
              </div>
              <p className="mt-2">Loading customer list...</p>
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

              {/* Customer Information Section */}
              <div className="card mb-3">
                <div className="card-header bg-light">
                  <h6 className="mb-0">👤 Customer Information</h6>
                  <small className="text-muted">Database: {users.length} customers</small>
                </div>
                <div className="card-body">
                  <div className="row mb-3">
                    <div className="col-md-6">
                      <label className="form-label">Email</label>
                      <input
                        type="email"
                        className="form-control"
                        placeholder="customer@example.com"
                        value={formData.customer_email}
                        onChange={(e) => setFormData(prev => ({...prev, customer_email: e.target.value}))}
                      />
                    </div>
                    <div className="col-md-6">
                      <label className="form-label">Phone</label>
                      <input
                        type="text"
                        className="form-control"
                        placeholder="555-123-4567"
                        value={formData.customer_phone}
                        onChange={(e) => setFormData(prev => ({...prev, customer_phone: e.target.value}))}
                      />
                    </div>
                  </div>

                  {isCheckingUser && (
                    <div className="alert alert-info py-2">
                      <small>🔍 Searching in {users.length} customers...</small>
                    </div>
                  )}

                  {foundUser && (
                    <div className="alert alert-success py-2">
                      <small>✅ Customer found: <strong>{foundUser.nombre}</strong></small>
                    </div>
                  )}

                  {!foundUser && (formData.customer_email || formData.customer_phone) && !isCheckingUser && (
                    <div className="alert alert-warning py-2">
                      <small>🆕 New customer - Please complete the details</small>
                    </div>
                  )}

                  <div className="row">
                    <div className="col-md-6">
                      <label className="form-label">Full Name *</label>
                      <input
                        type="text"
                        className="form-control"
                        value={formData.customer_name}
                        onChange={(e) => setFormData(prev => ({...prev, customer_name: e.target.value}))}
                        required
                      />
                    </div>
                    <div className="col-md-6">
                      <label className="form-label">Delivery Address *</label>
                      <input
                        type="text"
                        className="form-control"
                        placeholder="Full address"
                        value={formData.address}
                        onChange={(e) => setFormData(prev => ({...prev, address: e.target.value}))}
                        required
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Products Section */}
              <div className="card mb-3">
                <div className="card-header bg-light">
                  <h6 className="mb-0">🛒 Add Products</h6>
                </div>
                <div className="card-body">
                  <div className="row g-2">
                    <div className="col-md-6">
                      <select
                        className="form-select"
                        value={selectedProduct}
                        onChange={(e) => setSelectedProduct(e.target.value)}
                      >
                        <option value="">Select a product...</option>
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
                        value={quantity}
                        onChange={(e) => setQuantity(parseInt(e.target.value) || 1)}
                      />
                    </div>
                    <div className="col-md-3">
                      <button
                        type="button"
                        className="btn btn-primary w-100"
                        onClick={addProduct}
                      >
                        ➕ Add
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              {/* Products List */}
              {formData.details.length > 0 && (
                <div className="table-responsive">
                  <table className="table table-sm">
                    <thead className="table-dark">
                      <tr>
                        <th>Product</th>
                        <th>Quantity</th>
                        <th>Unit Price</th>
                        <th>Subtotal</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {formData.details.map((detail, index) => (
                        <tr key={index}>
                          <td>{detail.producto_nombre}</td>
                          <td>{detail.cantidad}</td>
                          <td>${detail.precio_unitario.toLocaleString()}</td>
                          <td>${detail.subtotal.toLocaleString()}</td>
                          <td>
                            <button
                              type="button"
                              className="btn btn-danger btn-sm"
                              onClick={() => removeProduct(index)}
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
                        <td className="fw-bold text-success">${calculateTotal().toLocaleString()}</td>
                        <td></td>
                      </tr>
                    </tfoot>
                  </table>
                </div>
              )}
            </div>
            <div className="modal-footer">
              <button type="button" className="btn btn-secondary" onClick={onClose}>
                Cancel
              </button>
              <button 
                type="submit" 
                className="btn btn-success"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Creating...
                  </>
                ) : (
                  '✅ Create Order'
                )}
              </button>
            </div>
          </form>

          {newUserCredentials && (
            <div className="modal fade show d-block" style={{backgroundColor: 'rgba(0,0,0,0.7)', position: 'fixed', top: '0', left: '0', zIndex: 9999}}>
              <div className="modal-dialog">
                <div className="modal-content">
                  <div className="modal-header bg-info">
                    <h5 className="modal-title text-white">🔐 New User Credentials</h5>
                  </div>
                  <div className="modal-body">
                    <div className="alert alert-info">
                      <strong>User created successfully!</strong>
                      <br/>Share these credentials with the customer.
                    </div>
                    
                    <div className="mb-3">
                      <label className="form-label fw-bold">👤 Name:</label>
                      <input type="text" className="form-control" value={newUserCredentials.nombre} readOnly />
                    </div>
                    
                    <div className="mb-3">
                      <label className="form-label fw-bold">📧 Email:</label>
                      <input type="text" className="form-control" value={newUserCredentials.email} readOnly />
                    </div>
                    
                    <div className="mb-3">
                      <label className="form-label fw-bold">🔑 Temporary Password:</label>
                      <input type="text" className="form-control fw-bold text-success" value={newUserCredentials.password} readOnly />
                    </div>
                    
                    <div className="alert alert-warning">
                      <small>⚠️ <strong>Important:</strong> The customer should change their password on first login.</small>
                    </div>
                  </div>
                  <div className="modal-footer">
                    <button 
                      type="button" 
                      className="btn btn-primary"
                      onClick={() => {
                        navigator.clipboard.writeText(`Email: ${newUserCredentials.email}\nPassword: ${newUserCredentials.password}`);
                        alert('Credentials copied to clipboard!');
                        setNewUserCredentials(null);
                      }}
                    >
                      📋 Copy Credentials
                    </button>
                    <button 
                      type="button" 
                      className="btn btn-secondary"
                      onClick={() => setNewUserCredentials(null)}
                    >
                      Close
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